from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from loaders.game_loader import GameLoader
from model.entities.state.factory import Factory
from simulation import Order, OrderResult, OrderType, SimulationEngine


ROOT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT_DIR / "templates" / "default_templates"
TEMPLATE_NAME = "victoria2"
SCENARIO_NAME = "1836"


def discover_worlds() -> list[dict]:
    worlds: list[dict] = []
    if not TEMPLATES_DIR.exists():
        return worlds

    for template_dir in sorted(path for path in TEMPLATES_DIR.iterdir() if path.is_dir()):
        world_dir = template_dir / "world"
        scenario_dir = template_dir / "scenario"
        if not world_dir.exists() or not scenario_dir.exists():
            continue
        scenarios = sorted(path.name for path in scenario_dir.iterdir() if path.is_dir())
        if not scenarios:
            continue
        worlds.append(
            {
                "template": template_dir.name,
                "label": template_dir.name.replace("_", " ").title(),
                "scenarios": scenarios,
                "default_scenario": scenarios[0],
            }
        )
    return worlds


AVAILABLE_WORLDS = discover_worlds()


def amount(value: float | int | None) -> float | int:
    if value is None:
        return 0
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return round(value, 4) if isinstance(value, float) else value


class VisualPlaytestSession:
    def __init__(self):
        self.engine = SimulationEngine()
        self.lock = threading.Lock()
        self.last_events: list[dict] = []
        self.last_results: list[OrderResult] = []
        self.template_name = TEMPLATE_NAME
        self.scenario_name = SCENARIO_NAME
        if AVAILABLE_WORLDS and not any(world["template"] == self.template_name for world in AVAILABLE_WORLDS):
            self.template_name = AVAILABLE_WORLDS[0]["template"]
            self.scenario_name = AVAILABLE_WORLDS[0]["default_scenario"]
        self.reset(self.template_name, self.scenario_name)

    def reset(self, template_name: str | None = None, scenario_name: str | None = None) -> dict:
        with self.lock:
            template_name = template_name or self.template_name
            scenario_name = scenario_name or self.scenario_name
            self._assert_world_exists(template_name, scenario_name)
            self.template_name = template_name
            self.scenario_name = scenario_name
            self.game_state = GameLoader.load(template_name, scenario_name)
            if scenario_name.isdigit():
                self.game_state.scenario.year = int(scenario_name)
            self.last_events = []
            self.last_results = []
            self._prepare_demo_state()
            return self.snapshot(f"Mundo cargado: {template_name} / {scenario_name}.")

    def _assert_world_exists(self, template_name: str, scenario_name: str) -> None:
        for world in AVAILABLE_WORLDS:
            if world["template"] == template_name and scenario_name in world["scenarios"]:
                return
        raise ValueError(f"Mundo no disponible: {template_name}/{scenario_name}")

    def _prepare_demo_state(self) -> None:
        factory_types = list(self.game_state.world.factory_types.values())
        if not factory_types:
            return

        for index, province in enumerate(self.game_state.provinces):
            world_province = self.game_state.world.get_province(province.id)
            if province.owner_tag and world_province and world_province.resource_id:
                province.rgo_workers = max(province.rgo_workers, 6 + index * 2)

        for factory in self.game_state.factories:
            factory_type = self.game_state.world.get_factory_type(factory.factory_type_id)
            country = self.game_state.get_country_state(factory.country_tag)
            if country:
                for resource_id, qty in (factory_type.input_goods if factory_type else {}).items():
                    country.stockpile.set_amount(resource_id, max(country.stockpile.get_amount(resource_id), qty * 5))

        if self.game_state.factories:
            return

        for province in self.game_state.provinces:
            if not province.owner_tag:
                continue
            factory_type = factory_types[0]
            country = self.game_state.get_country_state(province.owner_tag)
            if country:
                for resource_id, qty in factory_type.input_goods.items():
                    country.stockpile.set_amount(resource_id, max(country.stockpile.get_amount(resource_id), qty * 5))
            self.game_state.factories.append(
                Factory(
                    id=f"demo_{province.id}_{factory_type.id}",
                    factory_type_id=factory_type.id,
                    country_tag=province.owner_tag,
                    province_id=province.id,
                    level=1,
                    active=True,
                    efficiency=1.0,
                    current_workers=factory_type.needed_workers,
                )
            )
            break

    def run_ticks(self, ticks: int) -> dict:
        ticks = max(1, min(int(ticks), 30))
        with self.lock:
            self.last_events, self.last_results = self.engine.run(self.game_state, ticks)
            return self.snapshot(f"Avanzaste {ticks} dia(s).")

    def scripted_turn(self) -> dict:
        orders: list[Order] = []
        with self.lock:
            first_country = self.game_state.countries[0] if self.game_state.countries else None
            second_country = self.game_state.countries[1] if len(self.game_state.countries) > 1 else None

            if first_country:
                available_tech = next(
                    (tech for tech in self.game_state.world.techs if tech.id not in first_country.researched_techs),
                    None,
                )
                if available_tech:
                    orders.append(Order(OrderType.RESEARCH, first_country.tag, {"tech_id": available_tech.id}))

                owned_province = next(
                    (province for province in self.game_state.provinces if province.owner_tag == first_country.tag),
                    None,
                )
                factory_building = self.game_state.world.buildings.get("factory")
                factory_type = next(iter(self.game_state.world.factory_types.values()), None)
                if owned_province and factory_building and factory_type and first_country.money >= factory_building.construction_cost:
                    orders.append(
                        Order(
                            OrderType.BUILD,
                            first_country.tag,
                            {
                                "building_type_id": "factory",
                                "province_id": owned_province.id,
                                "factory_type_id": factory_type.id,
                            },
                        )
                    )

            first_army = self.game_state.armies[0] if self.game_state.armies else None
            if first_army:
                world_province = self.game_state.world.get_province(first_army.province_id)
                if world_province and world_province.adjacent_provinces:
                    orders.append(
                        Order(
                            OrderType.ARMY_MOVE,
                            first_army.owner_tag,
                            {"army_id": first_army.id, "to_province_id": world_province.adjacent_provinces[0]},
                        )
                    )

            if first_country and second_country:
                orders.append(
                    Order(
                        OrderType.DIPLOMACY,
                        first_country.tag,
                        {"action": "improve_relations", "target_tag": second_country.tag, "amount": 10},
                    )
                )
            self._submit_orders_locked(orders)
            accepted = sum(1 for result in self.last_results if result.accepted)
            return self.snapshot(f"Turno demo procesado: {accepted}/{len(orders)} orden(es) aceptada(s).")

    def submit_order(self, data: dict) -> dict:
        order_type = OrderType(data.get("type", ""))
        country_tag = str(data.get("country_tag", ""))
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        order = Order(order_type, country_tag, payload)
        with self.lock:
            self._submit_orders_locked([order])
            accepted = self.last_results[0].accepted if self.last_results else False
            message = "Orden aceptada." if accepted else "Orden rechazada."
            return self.snapshot(message)

    def _submit_orders_locked(self, orders: list[Order]) -> None:
        for order in orders:
            self.game_state.submit_order(order)
        self.last_events, self.last_results = self.engine.tick_forward(self.game_state)

    def snapshot(self, message: str = "") -> dict:
        game_state = self.game_state
        provinces = []
        for province in game_state.provinces:
            world_province = game_state.world.get_province(province.id)
            province_armies = [army.id for army in game_state.armies if army.province_id == province.id]
            province_buildings = [building.to_dict() for building in game_state.buildings if building.province_id == province.id]
            province_factories = [factory.to_dict() for factory in game_state.factories if factory.province_id == province.id]
            provinces.append(
                {
                    "id": province.id,
                    "name": world_province.name if world_province else province.name,
                    "owner_tag": province.owner_tag,
                    "population": province.population,
                    "fort_level": province.fort_level,
                    "resource_id": world_province.resource_id if world_province else None,
                    "terrain_id": world_province.terrain_id if world_province else None,
                    "adjacent_provinces": world_province.adjacent_provinces if world_province else [],
                    "rgo_workers": province.rgo_workers,
                    "armies": province_armies,
                    "buildings": province_buildings,
                    "factories": province_factories,
                }
            )

        countries = []
        for country in game_state.countries:
            countries.append(
                {
                    "tag": country.tag,
                    "name": country.name,
                    "capital": country.capital,
                    "population": country.population,
                    "money": amount(country.money),
                    "manpower": country.manpower,
                    "stockpile": {key: amount(value) for key, value in country.stockpile.resources.items()},
                    "researched_techs": list(country.researched_techs),
                    "actual_research": country.actual_research,
                    "relations": dict(country.relations),
                    "armies": list(country.armies),
                }
            )

        armies = []
        for army in game_state.armies:
            armies.append(
                {
                    "id": army.id,
                    "name": army.name,
                    "owner_tag": army.owner_tag,
                    "general_id": army.general_id,
                    "province_id": army.province_id,
                    "morale": amount(army.morale),
                    "organization": amount(army.organization),
                    "units": army.units.to_dict(),
                }
            )

        factories = []
        for factory in game_state.factories:
            factory_type = game_state.world.get_factory_type(factory.factory_type_id)
            factories.append(
                {
                    **factory.to_dict(),
                    "name": factory_type.name if factory_type else factory.factory_type_id,
                    "input_goods": dict(factory_type.input_goods) if factory_type else {},
                    "output_goods": dict(factory_type.output_goods) if factory_type else {},
                }
            )

        world = {
            "techs": [
                {
                    "id": tech.id,
                    "name": tech.name,
                    "branch": tech.branch.value,
                    "required_points": tech.required_points,
                    "effects": dict(tech.effects),
                    "activation_year": tech.activation_year,
                    "requirements": tech.requirements,
                    "banner": tech.banner,
                    "description": tech.description,
                }
                for tech in game_state.world.techs
            ],
            "buildings": [building.to_dict() for building in game_state.world.buildings.values()],
            "factory_types": [factory.to_dict() for factory in game_state.world.factory_types.values()],
            "resources": [resource.to_dict() for resource in game_state.world.resources],
        }

        return {
            "message": message,
            "template": self.template_name,
            "scenario_name": self.scenario_name,
            "available_worlds": AVAILABLE_WORLDS,
            "date": game_state.get_date(),
            "tick": game_state.current_tick,
            "scenario": game_state.scenario.name,
            "countries": countries,
            "provinces": provinces,
            "armies": armies,
            "factories": factories,
            "world": world,
            "last_events": self.last_events,
            "last_results": [self._serialize_result(result) for result in self.last_results],
            "event_log": game_state.get_event_log(limit=30),
            "event_statistics": game_state.get_event_statistics(),
        }

    def _serialize_result(self, result: OrderResult) -> dict:
        return {
            "accepted": result.accepted,
            "reason": result.reason,
            "order": {
                "type": result.order.type.value,
                "country_tag": result.order.country_tag,
                "payload": result.order.payload,
                "submitted_tick": result.order.submitted_tick,
            },
            "events": result.events,
        }


SESSION = VisualPlaytestSession()


class VisualPlaytestHandler(BaseHTTPRequestHandler):
    server_version = "ToVICVisualPlaytest/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._send_text(INDEX_HTML, "text/html; charset=utf-8")
            return
        if path == "/api/state":
            self._send_json(SESSION.snapshot())
            return
        if path == "/api/worlds":
            self._send_json({"worlds": AVAILABLE_WORLDS})
            return
        if path == "/assets/tovic-logo-mark.png":
            self._send_file(ROOT_DIR / "docs" / "assets" / "tovic-logo-mark.png")
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/tick":
                self._send_json(SESSION.run_ticks(int(payload.get("ticks", 1))))
                return
            if path == "/api/demo":
                self._send_json(SESSION.scripted_turn())
                return
            if path == "/api/order":
                self._send_json(SESSION.submit_order(payload))
                return
            if path == "/api/reset":
                self._send_json(SESSION.reset(payload.get("template"), payload.get("scenario")))
                return
            self._send_json({"error": "Not found"}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def log_message(self, format: str, *args) -> None:
        return

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, body: str, content_type: str, status: int = 200) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path) -> None:
        if not path.exists():
            self._send_json({"error": "Asset not found"}, status=404)
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


INDEX_HTML = r"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ToVIC Visual Playtest</title>
  <link rel="icon" type="image/png" href="/assets/tovic-logo-mark.png">
  <style>
    :root {
      --bg: #0b0d10;
      --rail: #101317;
      --panel: #151a20;
      --panel-2: #1b232b;
      --panel-3: #222b34;
      --line: #2d3741;
      --text: #eef2f4;
      --muted: #9ba8b0;
      --teal: #38d6c3;
      --blue: #78a7ff;
      --amber: #e6b35a;
      --green: #65d48b;
      --red: #ff6b72;
      --violet: #b69cff;
      --slate: #7a96b0;
      --rose: #c98a8e;
      --sage: #72a882;
      --sand: #b89e72;
      --sky: #6aaec8;
      --shadow: rgba(0, 0, 0, 0.48);
      --grid: rgba(155, 168, 176, 0.1);
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      width: 100%;
      height: 100%;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", system-ui, sans-serif;
      overflow: hidden;
    }

    button,
    select,
    input {
      font: inherit;
    }

    button {
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--text);
      min-height: 36px;
      border-radius: 6px;
      padding: 0 12px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      cursor: pointer;
    }

    button:hover {
      border-color: var(--blue);
      background: #202b34;
    }

    button.primary {
      background: #12413f;
      border-color: var(--teal);
    }

    button.danger {
      background: #3b2025;
      border-color: var(--red);
    }

    select,
    input {
      border: 1px solid var(--line);
      background: #0c1014;
      color: var(--text);
      border-radius: 6px;
      min-height: 34px;
      padding: 0 9px;
      outline: none;
      min-width: 0;
    }

    select:focus,
    input:focus {
      border-color: var(--teal);
    }

    .app {
      position: relative;
      width: 100%;
      height: 100%;
      background:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px),
        #0c1014;
      background-size: 28px 28px;
      overflow: hidden;
    }

    .world-map {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      user-select: none;
      cursor: default;
      touch-action: none;
    }

    .world-map.panning {
      cursor: grabbing;
    }

    .sea-band {
      fill: #0f171d;
    }

    .province {
      stroke: rgba(238, 242, 244, 0.68);
      stroke-width: 2;
      cursor: pointer;
      transition: filter 120ms ease, stroke-width 120ms ease, opacity 120ms ease;
      opacity: 0.86;
    }

    .province:hover,
    .province.active {
      filter: brightness(1.18);
      stroke-width: 3;
      opacity: 1;
    }

    .province-label {
      pointer-events: none;
      fill: rgba(238, 242, 244, 0.9);
      font: 13px "Segoe UI", system-ui, sans-serif;
      font-weight: 700;
    }

    .province-sub {
      pointer-events: none;
      fill: rgba(238, 242, 244, 0.68);
      font: 11px "Segoe UI", system-ui, sans-serif;
    }

    .route {
      fill: none;
      stroke: rgba(56, 214, 195, 0.32);
      stroke-width: 3;
      stroke-dasharray: 9 10;
    }

    .marker {
      fill: #ffffff;
      stroke: #0b0d10;
      stroke-width: 4;
    }

    .marker.factory {
      fill: var(--amber);
    }

    .marker.army {
      fill: var(--teal);
    }

    .top-hud,
    .bottom-hud,
    .window,
    .side-dock {
      position: absolute;
      z-index: 5;
    }

    .top-hud {
      top: 14px;
      left: 14px;
      right: 14px;
      min-height: 64px;
      display: grid;
      grid-template-columns: minmax(260px, auto) 1fr auto;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      background: rgba(16, 19, 23, 0.94);
      box-shadow: 0 18px 45px var(--shadow);
      border-radius: 8px;
      padding: 10px 12px;
    }

    .brand {
      display: grid;
      grid-template-columns: 42px 1fr;
      gap: 11px;
      align-items: center;
      min-width: 0;
    }

    .brand-mark {
      width: 42px;
      height: 42px;
      display: grid;
      place-items: center;
      color: var(--teal);
      border: 1px solid var(--teal);
      border-radius: 8px;
      background: #0e1d1c;
    }

    .brand-mark img {
      width: 28px;
      height: 28px;
      object-fit: contain;
    }

    .brand h1,
    .brand p {
      margin: 0;
    }

    .brand h1 {
      font-size: 18px;
      line-height: 1.1;
    }

    .brand p {
      color: var(--muted);
      font-size: 12px;
      margin-top: 3px;
    }

    .hud-metrics {
      display: flex;
      gap: 8px;
      justify-content: center;
      min-width: 0;
      overflow-x: auto;
      scrollbar-width: none;
    }

    .metric {
      border: 1px solid var(--line);
      background: #11161b;
      border-radius: 8px;
      padding: 8px 10px;
      min-width: 112px;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .metric strong {
      display: block;
      margin-top: 3px;
      font-size: 18px;
      line-height: 1;
    }

    .hud-actions {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      flex-wrap: wrap;
    }

    .hud-actions select {
      width: 150px;
    }

    .window {
      border: 1px solid var(--line);
      background: rgba(17, 22, 27, 0.94);
      box-shadow: 0 18px 45px var(--shadow);
      border-radius: 8px;
      backdrop-filter: blur(8px);
    }

    .province-window {
      left: 18px;
      top: 94px;
      width: 360px;
      max-height: calc(100% - 178px);
      overflow: auto;
    }

    .orders-window {
      right: 18px;
      top: 94px;
      width: 390px;
      max-height: calc(100% - 178px);
      overflow: auto;
    }

    .events-window {
      right: 18px;
      bottom: 86px;
      width: 520px;
      max-height: 330px;
      overflow: auto;
    }

    .events-window.hidden {
      display: none;
    }

    .window-header {
      min-height: 48px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
    }

    .window-header h2 {
      margin: 0;
      font-size: 15px;
    }

    .window-body {
      padding: 14px;
      display: grid;
      gap: 12px;
    }

    .data-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      min-height: 36px;
      border: 1px solid var(--line);
      background: rgba(12, 16, 20, 0.84);
      border-radius: 7px;
      padding: 7px 9px;
    }

    .data-row span {
      color: var(--muted);
      font-size: 13px;
    }

    .data-row strong {
      text-align: right;
      font-size: 14px;
    }

    .section-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      margin-top: 4px;
    }

    .country-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
    }

    .country-card,
    .order-card,
    .event-card {
      border: 1px solid var(--line);
      background: rgba(12, 16, 20, 0.76);
      border-radius: 8px;
      padding: 10px;
    }

    .country-card h3,
    .order-card h3 {
      margin: 0 0 8px;
      font-size: 13px;
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
    }

    .stock-row {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 0 8px;
      color: var(--text);
      background: #101820;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
    }

    .pill.ok {
      border-color: rgba(101, 212, 139, 0.55);
      color: var(--green);
    }

    .pill.fail {
      border-color: rgba(255, 107, 114, 0.6);
      color: var(--red);
    }

    .form-grid {
      display: grid;
      gap: 8px;
    }

    .form-grid.two {
      grid-template-columns: 1fr 1fr;
    }

    .form-row {
      display: grid;
      gap: 5px;
    }

    .form-row label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .bottom-hud {
      left: 14px;
      right: 14px;
      bottom: 14px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      border: 1px solid var(--line);
      background: rgba(16, 19, 23, 0.94);
      box-shadow: 0 18px 45px var(--shadow);
      border-radius: 8px;
      padding: 10px 12px;
    }

    .ticker {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      scrollbar-width: none;
    }

    .event-chip {
      border: 1px solid var(--line);
      background: #11161b;
      border-radius: 999px;
      padding: 7px 10px;
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    .event-list {
      display: grid;
      gap: 8px;
    }

    .event-card {
      display: grid;
      gap: 4px;
    }

    .event-card strong {
      font-size: 13px;
    }

    .event-card span {
      color: var(--muted);
      font-size: 12px;
    }

    .status {
      color: var(--teal);
      font-size: 12px;
      text-align: right;
    }

    .empty {
      min-height: 58px;
      display: grid;
      place-items: center;
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 8px;
      font-size: 13px;
    }

    @media (max-width: 1050px) {
      .top-hud {
        grid-template-columns: 1fr;
      }

      .hud-actions {
        justify-content: flex-start;
      }

      .province-window,
      .orders-window,
      .events-window {
        top: auto;
        bottom: 86px;
        max-height: 42%;
      }

      .province-window {
        width: calc(50% - 24px);
      }

      .orders-window {
        width: calc(50% - 24px);
      }

      .events-window {
        left: 18px;
        right: 18px;
        width: auto;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <svg class="world-map" viewBox="0 0 1100 680" aria-label="Mapa visual del playtest">
      <rect class="sea-band" x="0" y="0" width="1100" height="680"></rect>
      <g id="mapViewport">
        <g id="routeLayer"></g>
        <g id="provinceLayer"></g>
        <g id="markerLayer"></g>
      </g>
    </svg>

    <header class="top-hud">
      <div class="brand">
        <div class="brand-mark"><img src="/assets/tovic-logo-mark.png" alt=""></div>
        <div>
          <h1>ToVIC Visual Playtest</h1>
          <p>Motor Python real: Tick -> Economy -> Orders</p>
        </div>
      </div>
      <div class="hud-metrics" id="metrics"></div>
      <div class="hud-actions">
        <select id="worldSelect" title="Mundo"></select>
        <select id="scenarioSelect" title="Escenario"></select>
        <button class="primary" id="tickBtn">Tick +1</button>
        <button id="weekBtn">+7 dias</button>
        <button id="demoBtn">Turno demo</button>
        <button id="eventsBtn">Eventos</button>
        <button class="danger" id="resetBtn">Reset</button>
      </div>
    </header>

    <section class="window province-window">
      <div class="window-header">
        <h2>Provincia</h2>
        <span class="pill" id="selectedPill">Seleccion</span>
      </div>
      <div class="window-body" id="provincePanel"></div>
    </section>

    <section class="window orders-window">
      <div class="window-header">
        <h2>Ordenes del motor</h2>
        <span class="pill ok">Auto-tick</span>
      </div>
      <div class="window-body" id="ordersPanel"></div>
    </section>

    <section class="window events-window hidden" id="eventsWindow">
      <div class="window-header">
        <h2>Eventos</h2>
        <button id="closeEventsBtn">Cerrar</button>
      </div>
      <div class="window-body">
        <div class="event-list" id="eventList"></div>
      </div>
    </section>

    <footer class="bottom-hud">
      <div class="ticker" id="eventTicker"></div>
      <div class="status" id="statusText">Conectando...</div>
    </footer>
  </div>

  <script>
    const ownerPalette = ["#6aaec8", "#c98a8e", "#72a882", "#b89e72", "#7a96b0", "#b69cff", "#b87a62"];
    const mapView = { scale: 1, x: 0, y: 0, panning: false, lastX: 0, lastY: 0 };
    let provinceShapes = {};
    let state = null;
    let selectedProvinceId = "1";

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Error de API");
      }
      return data;
    }

    async function post(path, body = {}) {
      setStatus("Procesando en SimulationEngine...");
      try {
        state = await api(path, { method: "POST", body: JSON.stringify(body) });
        render();
      } catch (error) {
        setStatus(error.message);
      }
    }

    async function refresh() {
      try {
        state = await api("/api/state");
        render();
      } catch (error) {
        setStatus(error.message);
      }
    }

    function render() {
      if (!state) {
        return;
      }
      if (!selectedProvince()) {
        selectedProvinceId = state.provinces[0]?.id || "1";
      }
      renderWorldSelectors();
      renderMetrics();
      renderMap();
      renderProvincePanel();
      renderOrdersPanel();
      renderTicker();
      renderEventsWindow();
      setStatus(state.message || `Tick ${state.tick} listo.`);
    }

    function renderWorldSelectors() {
      const worldSelect = document.getElementById("worldSelect");
      const scenarioSelect = document.getElementById("scenarioSelect");
      const worlds = state.available_worlds || [];
      worldSelect.innerHTML = worlds.map((world) => {
        const selected = world.template === state.template ? " selected" : "";
        return `<option value="${escapeHtml(world.template)}"${selected}>${escapeHtml(world.label)}</option>`;
      }).join("");

      const currentWorld = worlds.find((world) => world.template === state.template) || worlds[0];
      const scenarios = currentWorld?.scenarios || [];
      scenarioSelect.innerHTML = scenarios.map((scenario) => {
        const selected = scenario === state.scenario_name ? " selected" : "";
        return `<option value="${escapeHtml(scenario)}"${selected}>${escapeHtml(scenario)}</option>`;
      }).join("");
    }

    function renderMetrics() {
      const totalMoney = state.countries.reduce((sum, country) => sum + Number(country.money || 0), 0);
      const activeFactories = state.factories.filter((factory) => factory.active).length;
      const manufactured = state.world.resources.filter((resource) => !resource.is_natural).map((resource) => resource.id);
      const totalManufactured = state.countries.reduce((sum, country) => {
        return sum + manufactured.reduce((inner, resourceId) => inner + Number(country.stockpile[resourceId] || 0), 0);
      }, 0);
      document.getElementById("metrics").innerHTML = [
        metric("Mundo", state.template),
        metric("Fecha", state.date),
        metric("Tick", state.tick),
        metric("Tesoro total", money(totalMoney)),
        metric("Fabricas", activeFactories),
        metric("Manufactura", number(totalManufactured))
      ].join("");
    }

    function metric(label, value) {
      return `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
    }

    function renderMap() {
      syncMapLayout();
      renderRoutes();
      const provinceLayer = document.getElementById("provinceLayer");
      provinceLayer.innerHTML = state.provinces.map((province) => {
        const shape = provinceShapes[province.id];
        if (!shape) {
          return "";
        }
        const owner = province.owner_tag || "neutral";
        const fill = ownerColor(owner);
        const active = province.id === selectedProvinceId ? " active" : "";
        return `
          <polygon class="province${active}" data-province-id="${province.id}" points="${shape.points}" fill="${fill}"></polygon>
          <text class="province-label" x="${shape.label[0]}" y="${shape.label[1]}">${escapeHtml(province.name)}</text>
          <text class="province-sub" x="${shape.label[0]}" y="${shape.label[1] + 17}">${escapeHtml(owner)} | ${escapeHtml(province.resource_id || "none")}</text>
        `;
      }).join("");

      provinceLayer.querySelectorAll("[data-province-id]").forEach((node) => {
        node.addEventListener("click", () => {
          selectedProvinceId = node.dataset.provinceId;
          render();
        });
      });

      const markerLayer = document.getElementById("markerLayer");
      const markers = [];
      state.armies.forEach((army, index) => {
        const shape = provinceShapes[army.province_id];
        if (!shape) {
          return;
        }
        const x = shape.label[0] - 34 + index * 8;
        const y = shape.label[1] - 36;
        markers.push(`<circle class="marker army" cx="${x}" cy="${y}" r="9"></circle>`);
        markers.push(`<text class="province-sub" x="${x + 14}" y="${y + 4}">A${escapeHtml(army.id)}</text>`);
      });
      state.factories.forEach((factory) => {
        const shape = provinceShapes[factory.province_id];
        if (!shape) {
          return;
        }
        markers.push(`<rect class="marker factory" x="${shape.label[0] + 46}" y="${shape.label[1] - 42}" width="18" height="18" rx="3"></rect>`);
      });
      markerLayer.innerHTML = markers.join("");
      applyMapTransform();
    }

    function syncMapLayout() {
      const columns = Math.ceil(Math.sqrt(state.provinces.length || 1));
      const tile = 132;
      const gap = 26;
      const startX = 150;
      const startY = 150;
      provinceShapes = {};
      state.provinces.forEach((province, index) => {
        const col = index % columns;
        const row = Math.floor(index / columns);
        const x = startX + col * (tile + gap);
        const y = startY + row * (tile + gap);
        provinceShapes[province.id] = {
          x,
          y,
          width: tile,
          height: tile,
          center: [x + tile / 2, y + tile / 2],
          label: [x + 18, y + 52],
          points: `${x},${y} ${x + tile},${y} ${x + tile},${y + tile} ${x},${y + tile}`
        };
      });
    }

    function renderRoutes() {
      const seen = new Set();
      const routeLayer = document.getElementById("routeLayer");
      const routes = [];
      state.provinces.forEach((province) => {
        const from = provinceShapes[province.id];
        if (!from) {
          return;
        }
        province.adjacent_provinces.forEach((targetId) => {
          const key = [province.id, targetId].sort().join(":");
          const to = provinceShapes[targetId];
          if (seen.has(key) || !to) {
            return;
          }
          seen.add(key);
          routes.push(`<line class="route" x1="${from.center[0]}" y1="${from.center[1]}" x2="${to.center[0]}" y2="${to.center[1]}"></line>`);
        });
      });
      routeLayer.innerHTML = routes.join("");
    }

    function ownerColor(owner) {
      if (!owner || owner === "neutral") {
        return "#7a96b0";
      }
      const index = state.countries.findIndex((country) => country.tag === owner);
      return ownerPalette[(index >= 0 ? index : owner.length) % ownerPalette.length];
    }

    function applyMapTransform() {
      document.getElementById("mapViewport").setAttribute(
        "transform",
        `translate(${mapView.x} ${mapView.y}) scale(${mapView.scale})`
      );
    }

    function svgPointFromClient(clientX, clientY) {
      const svg = document.querySelector(".world-map");
      const point = svg.createSVGPoint();
      point.x = clientX;
      point.y = clientY;
      return point.matrixTransform(svg.getScreenCTM().inverse());
    }

    function zoomMap(delta, clientX, clientY) {
      const oldScale = mapView.scale;
      const nextScale = clamp(oldScale * (delta < 0 ? 1.12 : 0.88), 0.55, 3.2);
      const cursor = svgPointFromClient(clientX, clientY);
      const worldX = (cursor.x - mapView.x) / oldScale;
      const worldY = (cursor.y - mapView.y) / oldScale;
      mapView.scale = nextScale;
      mapView.x = cursor.x - worldX * nextScale;
      mapView.y = cursor.y - worldY * nextScale;
      applyMapTransform();
    }

    function clamp(valueText, min, max) {
      return Math.max(min, Math.min(max, valueText));
    }

    function renderProvincePanel() {
      const province = selectedProvince();
      const pill = document.getElementById("selectedPill");
      const panel = document.getElementById("provincePanel");
      if (!province) {
        pill.textContent = "Nada";
        panel.innerHTML = `<div class="empty">Selecciona una provincia del mapa.</div>`;
        return;
      }
      pill.textContent = province.id;
      const owner = countryByTag(province.owner_tag);
      const armies = province.armies.map((armyId) => armyById(armyId)).filter(Boolean);
      panel.innerHTML = `
        ${dataRow("Nombre", province.name)}
        ${dataRow("Owner", owner ? `${owner.tag} - ${owner.name}` : "Neutral")}
        ${dataRow("Terreno", province.terrain_id || "N/A")}
        ${dataRow("Recurso", province.resource_id || "Ninguno")}
        ${dataRow("Poblacion", number(province.population))}
        ${dataRow("RGO workers", number(province.rgo_workers))}
        <div class="section-label">Actividad local</div>
        ${armies.length ? armies.map((army) => dataRow(`Army ${army.id}`, `${army.name} | morale ${army.morale}`)).join("") : `<div class="empty">Sin ejercitos presentes.</div>`}
        ${province.factories.length ? province.factories.map((factory) => dataRow("Fabrica", factory.factory_type_id)).join("") : ""}
        ${province.buildings.length ? province.buildings.map((building) => dataRow("Edificio", `${building.building_type_id} L${building.level}`)).join("") : ""}
      `;
    }

    function renderOrdersPanel() {
      const countries = state.countries;
      const techs = state.world.techs;
      const buildings = state.world.buildings;
      const factoryTypes = state.world.factory_types;
      const armies = state.armies;
      const selected = selectedProvince();
      const panel = document.getElementById("ordersPanel");
      panel.innerHTML = `
        <div class="country-grid">
          ${countries.map(countryCard).join("")}
        </div>

        <div class="order-card">
          <h3>Research <span class="pill">RESEARCH</span></h3>
          <div class="form-grid two">
            ${selectField("researchCountry", "Pais", countries, (item) => item.tag, (item) => `${item.tag} - ${item.name}`)}
            ${selectField("researchTech", "Tech", techs, (item) => item.id, (item) => `${item.id} (${item.activation_year})`)}
          </div>
          <button class="primary" id="researchBtn">Enviar orden</button>
        </div>

        <div class="order-card">
          <h3>Build <span class="pill">BUILD</span></h3>
          <div class="form-grid">
            <div class="form-grid two">
              ${selectField("buildCountry", "Pais", countries, (item) => item.tag, (item) => `${item.tag} - ${item.name}`)}
              ${selectField("buildType", "Edificio", buildings, (item) => item.id, (item) => `${item.id} | ${money(item.construction_cost)}`)}
            </div>
            ${selectField("buildProvince", "Provincia", state.provinces, (item) => item.id, (item) => `${item.id} - ${item.name} (${item.owner_tag || "neutral"})`, selected?.id)}
            ${selectField("buildFactoryType", "Tipo de fabrica", factoryTypes, (item) => item.id, (item) => `${item.id} | workers ${item.needed_workers}`)}
          </div>
          <button class="primary" id="buildBtn">Enviar orden</button>
        </div>

        <div class="order-card">
          <h3>Army move <span class="pill">ARMY_MOVE</span></h3>
          <div class="form-grid two">
            ${selectField("armySelect", "Ejercito", armies, (item) => item.id, (item) => `${item.id} - ${item.owner_tag} en ${item.province_id}`)}
            <div class="form-row">
              <label>Destino</label>
              <select id="armyDestination"></select>
            </div>
          </div>
          <button class="primary" id="moveBtn">Enviar orden</button>
        </div>

        <div class="order-card">
          <h3>Diplomacy <span class="pill">DIPLOMACY</span></h3>
          <div class="form-grid two">
            ${selectField("diploCountry", "Origen", countries, (item) => item.tag, (item) => `${item.tag} - ${item.name}`)}
            ${selectField("diploTarget", "Objetivo", countries, (item) => item.tag, (item) => `${item.tag} - ${item.name}`)}
            ${selectField("diploAction", "Accion", ["improve_relations", "worsen_relations"], (item) => item, (item) => item)}
            <div class="form-row">
              <label>Cambio</label>
              <input id="diploAmount" type="number" value="25" min="1" max="100">
            </div>
          </div>
          <button class="primary" id="diploBtn">Enviar orden</button>
        </div>
      `;
      attachOrderHandlers();
      updateArmyDestinations();
    }

    function countryCard(country) {
      const resourceIds = state.world.resources.map((resource) => resource.id);
      const stock = resourceIds
        .filter((key) => Number(country.stockpile[key] || 0) > 0)
        .map((key) => `${key}:${number(country.stockpile[key])}`)
        .join("  ") || "sin stock";
      return `
        <div class="country-card">
          <h3>${escapeHtml(country.tag)} <span class="pill">${money(country.money)}</span></h3>
          <div class="stock-row">${escapeHtml(country.name)}</div>
          <div class="stock-row">${escapeHtml(stock)}</div>
        </div>
      `;
    }

    function attachOrderHandlers() {
      document.getElementById("researchBtn").addEventListener("click", () => {
        submitOrder("research", value("researchCountry"), { tech_id: value("researchTech") });
      });
      document.getElementById("buildBtn").addEventListener("click", () => {
        const payload = {
          building_type_id: value("buildType"),
          province_id: value("buildProvince")
        };
        if (payload.building_type_id === "factory") {
          payload.factory_type_id = value("buildFactoryType");
        }
        submitOrder("build", value("buildCountry"), payload);
      });
      document.getElementById("armySelect").addEventListener("change", updateArmyDestinations);
      document.getElementById("moveBtn").addEventListener("click", () => {
        const army = armyById(value("armySelect"));
        if (!army) {
          return;
        }
        submitOrder("army_move", army.owner_tag, {
          army_id: army.id,
          to_province_id: value("armyDestination")
        });
      });
      document.getElementById("diploBtn").addEventListener("click", () => {
        submitOrder("diplomacy", value("diploCountry"), {
          action: value("diploAction"),
          target_tag: value("diploTarget"),
          amount: Number(value("diploAmount") || 25)
        });
      });
    }

    function updateArmyDestinations() {
      const army = armyById(value("armySelect"));
      const select = document.getElementById("armyDestination");
      if (!army || !select) {
        return;
      }
      const province = provinceById(army.province_id);
      const adjacent = province?.adjacent_provinces || [];
      select.innerHTML = adjacent.map((provinceId) => {
        const target = provinceById(provinceId);
        return `<option value="${escapeHtml(provinceId)}">${escapeHtml(provinceId)} - ${escapeHtml(target?.name || "Provincia")}</option>`;
      }).join("");
    }

    function submitOrder(type, countryTag, payload) {
      post("/api/order", { type, country_tag: countryTag, payload });
    }

    function renderTicker() {
      const ticker = document.getElementById("eventTicker");
      const items = state.last_events.length ? state.last_events : state.event_log.map((event) => ({
        type: event.type,
        ...event.data
      }));
      ticker.innerHTML = (items.slice(-10).reverse()).map((event) => {
        return `<div class="event-chip">${escapeHtml(describeEvent(event))}</div>`;
      }).join("") || `<div class="event-chip">Sin eventos todavia</div>`;
    }

    function renderEventsWindow() {
      const list = document.getElementById("eventList");
      const events = (state.event_log || []).slice().reverse();
      if (!events.length) {
        list.innerHTML = `<div class="empty">Aun no hay eventos registrados.</div>`;
        return;
      }
      list.innerHTML = events.map((event) => {
        const readable = describeEvent({ type: event.type, ...(event.data || {}), tick: event.tick, date: event.date });
        return `
          <div class="event-card">
            <strong>${escapeHtml(readable)}</strong>
            <span>Tick ${escapeHtml(event.tick)} | ${escapeHtml(event.date)}</span>
          </div>
        `;
      }).join("");
    }

    function describeEvent(event) {
      if (event.type === "TICK_ADVANCED") {
        return `Tick ${event.tick} | ${event.date}`;
      }
      if (event.type === "RGO_PRODUCED") {
        return `${event.owner_tag} produjo ${number(event.amount)} ${event.resource_id}`;
      }
      if (event.type === "FACTORY_RAN") {
        return `${event.country_tag} fabrico ${Object.keys(event.produced || {}).join(", ")}`;
      }
      if (event.type === "TECH_RESEARCHED") {
        return `${event.country_tag} investigo ${event.tech_id}`;
      }
      if (event.type === "BUILD_STARTED") {
        return `${event.country_tag} inicio ${event.building_type_id} en ${event.province_id}`;
      }
      if (event.type === "BUILD_COMPLETED") {
        return `${event.country_tag} completo ${event.building_type_id} en ${event.province_id}`;
      }
      if (event.type === "ARMY_MOVED") {
        return `Army ${event.army_id}: ${event.from_province_id} -> ${event.to_province_id}`;
      }
      if (event.type === "DIPLOMACY_ACTION") {
        return `${event.country_tag} ${event.action} con ${event.target_tag}`;
      }
      if (event.type === "CB_EXPIRED") {
        return `CB ${event.cb_id} expiro`;
      }
      return event.type || "Evento";
    }

    function selectedProvince() {
      return provinceById(selectedProvinceId);
    }

    function provinceById(id) {
      return state?.provinces.find((province) => province.id === id);
    }

    function countryByTag(tag) {
      return state?.countries.find((country) => country.tag === tag);
    }

    function armyById(id) {
      return state?.armies.find((army) => army.id === id);
    }

    function dataRow(label, valueText) {
      return `<div class="data-row"><span>${escapeHtml(label)}</span><strong>${escapeHtml(valueText)}</strong></div>`;
    }

    function selectField(id, label, items, valueGetter, labelGetter, selectedValue) {
      return `
        <div class="form-row">
          <label>${escapeHtml(label)}</label>
          <select id="${escapeHtml(id)}">
            ${items.map((item) => {
              const itemValue = valueGetter(item);
              const selected = selectedValue && String(selectedValue) === String(itemValue) ? " selected" : "";
              return `<option value="${escapeHtml(itemValue)}"${selected}>${escapeHtml(labelGetter(item))}</option>`;
            }).join("")}
          </select>
        </div>
      `;
    }

    function value(id) {
      return document.getElementById(id)?.value || "";
    }

    function setStatus(text) {
      document.getElementById("statusText").textContent = text;
    }

    function money(valueText) {
      return `$${number(valueText)}`;
    }

    function number(valueText) {
      const valueNumber = Number(valueText || 0);
      return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(valueNumber);
    }

    function escapeHtml(valueText) {
      return String(valueText ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    document.getElementById("worldSelect").addEventListener("change", () => {
      const world = (state.available_worlds || []).find((item) => item.template === value("worldSelect"));
      const scenario = world?.default_scenario || value("scenarioSelect");
      selectedProvinceId = "";
      mapView.scale = 1;
      mapView.x = 0;
      mapView.y = 0;
      post("/api/reset", { template: value("worldSelect"), scenario });
    });
    document.getElementById("scenarioSelect").addEventListener("change", () => {
      selectedProvinceId = "";
      mapView.scale = 1;
      mapView.x = 0;
      mapView.y = 0;
      post("/api/reset", { template: value("worldSelect"), scenario: value("scenarioSelect") });
    });
    document.getElementById("tickBtn").addEventListener("click", () => post("/api/tick", { ticks: 1 }));
    document.getElementById("weekBtn").addEventListener("click", () => post("/api/tick", { ticks: 7 }));
    document.getElementById("demoBtn").addEventListener("click", () => post("/api/demo", {}));
    document.getElementById("eventsBtn").addEventListener("click", () => {
      document.getElementById("eventsWindow").classList.toggle("hidden");
      renderEventsWindow();
    });
    document.getElementById("closeEventsBtn").addEventListener("click", () => {
      document.getElementById("eventsWindow").classList.add("hidden");
    });
    document.getElementById("resetBtn").addEventListener("click", () => {
      selectedProvinceId = "";
      mapView.scale = 1;
      mapView.x = 0;
      mapView.y = 0;
      post("/api/reset", { template: value("worldSelect"), scenario: value("scenarioSelect") });
    });

    const svg = document.querySelector(".world-map");
    svg.addEventListener("wheel", (event) => {
      event.preventDefault();
      zoomMap(event.deltaY, event.clientX, event.clientY);
    }, { passive: false });
    svg.addEventListener("pointerdown", (event) => {
      if (event.button !== 1) {
        return;
      }
      event.preventDefault();
      mapView.panning = true;
      mapView.lastX = event.clientX;
      mapView.lastY = event.clientY;
      svg.classList.add("panning");
      svg.setPointerCapture(event.pointerId);
    });
    svg.addEventListener("pointermove", (event) => {
      if (!mapView.panning) {
        return;
      }
      const dx = event.clientX - mapView.lastX;
      const dy = event.clientY - mapView.lastY;
      const rect = svg.getBoundingClientRect();
      mapView.x += dx * 1100 / Math.max(1, rect.width);
      mapView.y += dy * 680 / Math.max(1, rect.height);
      mapView.lastX = event.clientX;
      mapView.lastY = event.clientY;
      applyMapTransform();
    });
    function stopPan(event) {
      mapView.panning = false;
      svg.classList.remove("panning");
      if (event?.pointerId && svg.hasPointerCapture(event.pointerId)) {
        svg.releasePointerCapture(event.pointerId);
      }
    }
    svg.addEventListener("pointerup", stopPan);
    svg.addEventListener("pointercancel", stopPan);
    svg.addEventListener("auxclick", (event) => {
      if (event.button === 1) {
        event.preventDefault();
      }
    });

    refresh();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="ToVIC visual playtest connected to the Python engine.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the browser automatically.")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), VisualPlaytestHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"ToVIC Visual Playtest running at {url}")
    print("Press Ctrl+C to stop.")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping visual playtest.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
