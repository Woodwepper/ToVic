from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from loaders.game_loader import GameLoader
from loaders.managers.world_loader import WorldLoader
from loaders.validators.scenario_data_validator import ScenarioDataValidator
from loaders.validators.world_data_validator import WorldDataValidator
from model.entities.state.game_state import GameState
from simulation import Order, OrderResult, OrderType, SimulationEngine


ROOT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT_DIR / "templates" / "default_templates"
DEFAULT_TEMPLATE = "victoria2"
DEFAULT_SCENARIO = "1836"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


@dataclass(frozen=True)
class PlayableWorld:
    template: str
    scenario: str
    world_id: str | None
    label: str
    is_default: bool = False

    @property
    def key(self) -> str:
        world = self.world_id or self.template
        return f"{self.template}:{self.scenario}:{world}"


def amount(value: float | int | None) -> float | int:
    if value is None:
        return 0
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return round(value, 4) if isinstance(value, float) else value


def sort_id(value: str) -> tuple[int, int | str]:
    text = str(value)
    return (0, int(text)) if text.isdigit() else (1, text)


def section(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")


def playable_worlds() -> list[PlayableWorld]:
    worlds: list[PlayableWorld] = []
    if not TEMPLATES_DIR.exists():
        return worlds

    for template_dir in sorted(path for path in TEMPLATES_DIR.iterdir() if path.is_dir()):
        scenario_dir = template_dir / "scenario"
        if not scenario_dir.exists():
            continue

        scenarios = sorted(path.name for path in scenario_dir.iterdir() if path.is_dir())
        if not scenarios:
            continue

        world_options = WorldLoader.list_worlds(template_dir.name)
        if not world_options:
            continue

        for scenario in scenarios:
            for option in world_options:
                world_id = None if option.is_default else option.id
                label = f"{option.name} / {scenario}"
                worlds.append(
                    PlayableWorld(
                        template=template_dir.name,
                        scenario=scenario,
                        world_id=world_id,
                        label=label,
                        is_default=option.is_default,
                    )
                )
    return worlds


def resolve_world(template: str, scenario: str, world_id: str | None = None) -> PlayableWorld:
    for world in playable_worlds():
        if world.template != template or world.scenario != scenario:
            continue
        if (world.world_id or world.template) == (world_id or template):
            return world
    return PlayableWorld(
        template=template,
        scenario=scenario,
        world_id=None if world_id in (None, "", template, "default", "base") else world_id,
        label=f"{template} / {scenario}",
        is_default=world_id in (None, "", template, "default", "base"),
    )


def load_game(template: str, scenario: str, world_id: str | None = None) -> GameState:
    game_state = GameLoader.load(template, scenario, world_id=world_id)
    if scenario.isdigit():
        game_state.scenario.year = int(scenario)
    return game_state


def validation_errors(game_state: GameState) -> list[str]:
    errors: list[str] = []
    world_errors = WorldDataValidator(game_state.world).validate()
    scenario_errors = ScenarioDataValidator(game_state.scenario, game_state.world).validate()

    if world_errors:
        errors.append(f"[WORLD] {len(world_errors)} error(s)")
        errors.extend(f"  - {error}" for error in world_errors)
    if scenario_errors:
        errors.append(f"[SCENARIO] {len(scenario_errors)} error(s)")
        errors.extend(f"  - {error}" for error in scenario_errors)
    return errors


def describe_event(event: dict) -> str:
    event_type = event.get("type", "UNKNOWN")
    data = event.get("data") if "data" in event else event

    if event_type == "TICK_ADVANCED":
        return f"Tick {data.get('tick', event.get('tick'))} | {data.get('date', event.get('date'))}"
    if event_type == "LABOR_ALLOCATED":
        return (
            f"{data.get('country_tag')} asigno {data.get('factory_workers', 0)} workers a fabricas "
            f"y {data.get('rgo_workers', 0)} a RGO"
        )
    if event_type == "RGO_PRODUCED":
        return (
            f"{data.get('owner_tag')} produjo {amount(data.get('amount'))} "
            f"{data.get('resource_id')} en provincia {data.get('province_id')}"
        )
    if event_type == "FACTORY_RAN":
        produced = ", ".join(f"{key}:{amount(value)}" for key, value in data.get("produced", {}).items())
        return f"{data.get('country_tag')} fabrico {produced or 'nada'} en {data.get('factory_id')}"
    if event_type == "TECH_RESEARCHED":
        return f"{data.get('country_tag')} investigo {data.get('tech_id')}"
    if event_type == "BUILD_STARTED":
        return f"{data.get('country_tag')} inicio {data.get('building_type_id')} en {data.get('province_id')}"
    if event_type == "BUILD_COMPLETED":
        return f"{data.get('country_tag')} completo {data.get('building_type_id')} en {data.get('province_id')}"
    if event_type == "ARMY_MOVED":
        return f"Ejercito {data.get('army_id')}: {data.get('from_province_id')} -> {data.get('to_province_id')}"
    if event_type == "DIPLOMACY_ACTION":
        return f"{data.get('country_tag')} {data.get('action')} con {data.get('target_tag')}"
    if event_type == "CB_EXPIRED":
        return f"CB {data.get('cb_id')} expiro"
    return event_type


def serialize_result(result: OrderResult) -> dict:
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


def serialize_game_state(session: "PlaytestSession", message: str = "") -> dict:
    game_state = session.game_state
    world = game_state.world

    countries = []
    for country in game_state.countries:
        countries.append(
            {
                "tag": country.tag,
                "name": country.name,
                "money": amount(country.money),
                "population": country.population,
                "manpower": country.manpower,
                "workers_pool": country.workers_pool,
                "stockpile": country.stockpile.to_dict(),
                "researched_techs": list(country.researched_techs),
                "armies": list(country.armies),
            }
        )

    provinces = []
    for province in game_state.provinces:
        world_province = world.get_province(province.id)
        provinces.append(
            {
                "id": province.id,
                "name": world_province.name if world_province else province.name,
                "owner_tag": province.owner_tag,
                "population": province.population,
                "fort_level": province.fort_level,
                "terrain_id": world_province.terrain_id if world_province else None,
                "resource_id": world_province.resource_id if world_province else None,
                "adjacent_provinces": list(world_province.adjacent_provinces) if world_province else [],
                "factories": list(province.factories),
                "building_levels": dict(province.building_levels),
                "rgo_workers": province.rgo_workers,
            }
        )

    armies = []
    for army in game_state.armies:
        armies.append(
            {
                "id": army.id,
                "name": army.name,
                "owner_tag": army.owner_tag,
                "province_id": army.province_id,
                "morale": amount(army.morale),
                "organization": amount(army.organization),
                "units": army.units.to_dict(),
            }
        )

    return {
        "message": message,
        "template": session.world.template,
        "scenario": session.world.scenario,
        "world_id": session.world.world_id or session.world.template,
        "world_label": session.world.label,
        "available_worlds": [world.__dict__ | {"key": world.key} for world in playable_worlds()],
        "date": game_state.get_date(),
        "tick": game_state.current_tick,
        "summary": {
            "world_name": world.name,
            "provinces": len(world.provinces),
            "countries": len(game_state.countries),
            "armies": len(game_state.armies),
            "factories": len(game_state.factories),
            "projects": len(game_state.building_projects),
            "events": len(game_state.event_log),
        },
        "countries": countries,
        "provinces": provinces,
        "armies": armies,
        "factories": [factory.to_dict() for factory in game_state.factories],
        "projects": [project.to_dict() for project in game_state.building_projects],
        "last_events": session.last_events,
        "last_results": [serialize_result(result) for result in session.last_results],
        "event_log": game_state.get_event_log(limit=80),
        "event_statistics": game_state.get_event_statistics(),
    }


class PlaytestSession:
    def __init__(self, world: PlayableWorld):
        self.engine = SimulationEngine()
        self.lock = threading.Lock()
        self.world = world
        self.last_events: list[dict] = []
        self.last_results: list[OrderResult] = []
        self.game_state = load_game(world.template, world.scenario, world.world_id)

    def reset(self, world: PlayableWorld | None = None) -> dict:
        with self.lock:
            if world is not None:
                self.world = world
            self.game_state = load_game(self.world.template, self.world.scenario, self.world.world_id)
            self.last_events = []
            self.last_results = []
            return serialize_game_state(self, "Mundo reiniciado.")

    def run_ticks(self, ticks: int) -> dict:
        ticks = max(1, min(int(ticks), 365))
        with self.lock:
            self.last_events, self.last_results = self.engine.run(self.game_state, ticks)
            return serialize_game_state(self, f"Avanzaste {ticks} tick(s).")

    def submit_order(self, order_type: str, country_tag: str, payload: dict) -> dict:
        with self.lock:
            order = Order(OrderType(order_type), country_tag, payload)
            self.game_state.submit_order(order)
            self.last_events, self.last_results = self.engine.tick_forward(self.game_state)
            return serialize_game_state(self, "Orden enviada al engine.")

    def demo_turn(self) -> dict:
        with self.lock:
            for order in self._demo_orders():
                self.game_state.submit_order(order)
            self.last_events, self.last_results = self.engine.tick_forward(self.game_state)
            return serialize_game_state(self, "Turno demo ejecutado.")

    def _demo_orders(self) -> list[Order]:
        orders: list[Order] = []
        if not self.game_state.countries:
            return orders

        for country in self.game_state.countries:
            tech = self._first_available_tech(country.tag)
            if tech:
                orders.append(Order(OrderType.RESEARCH, country.tag, {"tech_id": tech.id}))
                break

        build_order = self._first_build_order()
        if build_order:
            orders.append(build_order)

        army_order = self._first_army_move_order()
        if army_order:
            orders.append(army_order)

        if len(self.game_state.countries) >= 2:
            source, target = self.game_state.countries[0], self.game_state.countries[1]
            orders.append(
                Order(
                    OrderType.DIPLOMACY,
                    source.tag,
                    {"action": "improve_relations", "target_tag": target.tag, "amount": 10},
                )
            )
        return orders

    def _first_available_tech(self, country_tag: str):
        country = self.game_state.get_country_state(country_tag)
        if not country:
            return None
        for tech in self.game_state.world.techs:
            if tech.id in country.researched_techs:
                continue
            if tech.activation_year > self.game_state.scenario.year:
                continue
            if tech.requirements and tech.requirements not in country.researched_techs:
                continue
            return tech
        return None

    def _first_build_order(self) -> Order | None:
        for province in self.game_state.provinces:
            if not province.owner_tag:
                continue
            country = self.game_state.get_country_state(province.owner_tag)
            if not country:
                continue
            for building_type in self.game_state.world.buildings.values():
                if building_type.required_technology and building_type.required_technology not in country.researched_techs:
                    continue
                if country.money < building_type.construction_cost:
                    continue
                payload = {"building_type_id": building_type.id, "province_id": province.id}
                if building_type.id == "factory":
                    factory_type = next(iter(self.game_state.world.factory_types.values()), None)
                    if not factory_type:
                        continue
                    payload["factory_type_id"] = factory_type.id
                return Order(OrderType.BUILD, country.tag, payload)
        return None

    def _first_army_move_order(self) -> Order | None:
        for army in self.game_state.armies:
            world_province = self.game_state.world.get_province(army.province_id or "")
            if world_province and world_province.adjacent_provinces:
                return Order(
                    OrderType.ARMY_MOVE,
                    army.owner_tag,
                    {"army_id": army.id, "to_province_id": world_province.adjacent_provinces[0]},
                )
        return None


SESSION = PlaytestSession(resolve_world(DEFAULT_TEMPLATE, DEFAULT_SCENARIO))


def print_worlds() -> None:
    section("Mundos disponibles")
    worlds = playable_worlds()
    if not worlds:
        print("No hay templates jugables en templates/default_templates.")
        return
    for index, world in enumerate(worlds, start=1):
        variant = world.world_id or "base"
        print(f"{index:>2}. {world.label} | template={world.template} scenario={world.scenario} world={variant}")


def print_summary(game_state: GameState) -> None:
    section("Resumen")
    print(f"World: {game_state.world.name} ({game_state.world.id})")
    print(f"Scenario: {game_state.scenario.name} | Date: {game_state.get_date()} | Tick: {game_state.current_tick}")
    print(
        "Defs: "
        f"{len(game_state.world.provinces)} provincias, "
        f"{len(game_state.world.resources)} recursos, "
        f"{len(game_state.world.techs)} techs, "
        f"{len(game_state.world.buildings)} edificios, "
        f"{len(game_state.world.factory_types)} fabricas"
    )
    print(
        "State: "
        f"{len(game_state.countries)} paises, "
        f"{len(game_state.provinces)} provincias, "
        f"{len(game_state.armies)} ejercitos, "
        f"{len(game_state.factories)} fabricas activas"
    )

    print("\nPaises")
    for country in game_state.countries:
        print(
            f"  {country.tag:<5} {country.name:<24} "
            f"money={amount(country.money):>8} pop={country.population:<10} armies={len(country.armies)}"
        )

    print("\nProvincias")
    for province in sorted(game_state.provinces, key=lambda item: sort_id(item.id)):
        world_province = game_state.world.get_province(province.id)
        resource = world_province.resource_id if world_province else None
        terrain = world_province.terrain_id if world_province else None
        print(
            f"  {province.id:<6} {(world_province.name if world_province else province.name):<24} "
            f"owner={province.owner_tag or 'NEUTRAL':<8} terrain={terrain or '-':<12} resource={resource or '-'}"
        )


def run_validate(args: argparse.Namespace) -> int:
    world = resolve_world(args.template, args.scenario, args.world)
    try:
        game_state = load_game(world.template, world.scenario, world.world_id)
    except Exception as error:
        print(f"[FALLO] No se pudo cargar {world.label}: {error}")
        return 1

    errors = validation_errors(game_state)
    print_summary(game_state)
    section("Validacion")
    if errors:
        print("[FALLO] Se encontraron errores:")
        for error in errors:
            print(error)
        return 1
    print("[OK] Mundo y escenario validos.")
    return 0


def run_audit(_: argparse.Namespace) -> int:
    section("Audit de templates")
    failures: list[str] = []
    worlds = playable_worlds()
    if not worlds:
        print("[FALLO] No hay mundos disponibles.")
        return 1

    for world in worlds:
        try:
            game_state = load_game(world.template, world.scenario, world.world_id)
            errors = validation_errors(game_state)
            if errors:
                failures.append(f"{world.label}: {len(errors)} error lines")
                print(f"[FALLO] {world.label}")
                for error in errors:
                    print(f"  {error}")
                continue

            engine = SimulationEngine()
            events, results = engine.run(game_state, 1)
            print(
                f"[OK] {world.label:<36} "
                f"tick={game_state.current_tick} events={len(events)} results={len(results)}"
            )
        except Exception as error:
            failures.append(f"{world.label}: {error}")
            print(f"[FALLO] {world.label}: {error}")

    section("Resultado audit")
    if failures:
        print(f"[FALLO] {len(failures)} mundo(s) con problemas.")
        return 1
    print(f"[OK] {len(worlds)} mundo(s) cargaron, validaron y avanzaron 1 tick.")
    return 0


def choose_world(current: PlayableWorld) -> PlayableWorld:
    worlds = playable_worlds()
    print_worlds()
    if not worlds:
        return current
    raw = input("\nElige mundo por numero (enter mantiene actual): ").strip()
    if not raw:
        return current
    try:
        index = int(raw)
    except ValueError:
        print("Entrada invalida.")
        return current
    if not 1 <= index <= len(worlds):
        print("Numero fuera de rango.")
        return current
    return worlds[index - 1]


def prompt_choice(label: str, options: list, describe) -> object | None:
    if not options:
        print(f"No hay opciones para {label}.")
        return None
    for index, item in enumerate(options, start=1):
        print(f"  {index}) {describe(item)}")
    raw = input(f"{label}: ").strip()
    try:
        selected = int(raw)
    except ValueError:
        print("Entrada invalida.")
        return None
    if not 1 <= selected <= len(options):
        print("Numero fuera de rango.")
        return None
    return options[selected - 1]


def console_research(session: PlaytestSession) -> None:
    country = prompt_choice("Pais", session.game_state.countries, lambda item: f"{item.tag} - {item.name}")
    if not country:
        return
    available = [tech for tech in session.game_state.world.techs if tech.id not in country.researched_techs]
    tech = prompt_choice("Tech", available, lambda item: f"{item.id} - {item.name}")
    if not tech:
        return
    session.submit_order(OrderType.RESEARCH.value, country.tag, {"tech_id": tech.id})


def console_build(session: PlaytestSession) -> None:
    country = prompt_choice("Pais", session.game_state.countries, lambda item: f"{item.tag} - {item.name}")
    if not country:
        return
    provinces = [province for province in session.game_state.provinces if province.owner_tag == country.tag]
    province = prompt_choice("Provincia", provinces, lambda item: f"{item.id} - {item.name}")
    if not province:
        return
    building = prompt_choice(
        "Edificio",
        list(session.game_state.world.buildings.values()),
        lambda item: f"{item.id} - {item.name} ({item.construction_cost})",
    )
    if not building:
        return
    payload = {"building_type_id": building.id, "province_id": province.id}
    if building.id == "factory":
        factory_type = prompt_choice(
            "Tipo de fabrica",
            list(session.game_state.world.factory_types.values()),
            lambda item: f"{item.id} - {item.name}",
        )
        if not factory_type:
            return
        payload["factory_type_id"] = factory_type.id
    session.submit_order(OrderType.BUILD.value, country.tag, payload)


def console_army_move(session: PlaytestSession) -> None:
    army = prompt_choice("Ejercito", session.game_state.armies, lambda item: f"{item.id} - {item.name} ({item.owner_tag})")
    if not army:
        return
    world_province = session.game_state.world.get_province(army.province_id or "")
    adjacent_ids = world_province.adjacent_provinces if world_province else []
    provinces = [session.game_state.world.get_province(province_id) for province_id in adjacent_ids]
    provinces = [province for province in provinces if province]
    province = prompt_choice("Destino", provinces, lambda item: f"{item.id} - {item.name}")
    if not province:
        return
    session.submit_order(OrderType.ARMY_MOVE.value, army.owner_tag, {"army_id": army.id, "to_province_id": province.id})


def console_diplomacy(session: PlaytestSession) -> None:
    source = prompt_choice("Pais origen", session.game_state.countries, lambda item: f"{item.tag} - {item.name}")
    if not source:
        return
    targets = [country for country in session.game_state.countries if country.tag != source.tag]
    target = prompt_choice("Pais objetivo", targets, lambda item: f"{item.tag} - {item.name}")
    if not target:
        return
    session.submit_order(
        OrderType.DIPLOMACY.value,
        source.tag,
        {"action": "improve_relations", "target_tag": target.tag, "amount": 10},
    )


def print_recent_events(session: PlaytestSession, limit: int = 12) -> None:
    events = session.game_state.get_event_log(limit=limit)
    if not events:
        print("Sin eventos todavia.")
        return
    for event in events:
        print(f"  tick={event.get('tick'):<4} {event.get('date'):<10} {describe_event(event)}")


def run_console(args: argparse.Namespace) -> int:
    session = PlaytestSession(resolve_world(args.template, args.scenario, args.world))
    while True:
        section(f"ToVIC console | {session.world.label}")
        print(f"Fecha: {session.game_state.get_date()} | Tick: {session.game_state.current_tick}")
        print("1) Resumen        2) Avanzar 1 tick   3) Avanzar 7 ticks")
        print("4) Turno demo     5) Investigar       6) Construir")
        print("7) Mover ejercito 8) Diplomacia       9) Eventos")
        print("10) Cambiar mundo 0) Salir")

        choice = input("\n> ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            print_summary(session.game_state)
        elif choice == "2":
            session.run_ticks(1)
        elif choice == "3":
            session.run_ticks(7)
        elif choice == "4":
            session.demo_turn()
        elif choice == "5":
            console_research(session)
        elif choice == "6":
            console_build(session)
        elif choice == "7":
            console_army_move(session)
        elif choice == "8":
            console_diplomacy(session)
        elif choice == "9":
            print_recent_events(session)
        elif choice == "10":
            session = PlaytestSession(choose_world(session.world))
        else:
            print("Opcion no reconocida.")

        input("\nEnter para continuar...")


WEB_HTML = r"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ToVIC Main Sandbox</title>
  <style>
    :root { color-scheme: dark; --bg:#121418; --panel:#1b1f26; --line:#303847; --text:#eef2f7; --muted:#9ca8b8; --accent:#7cc7a5; --warn:#f0b35f; --bad:#ef7d7d; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--text); }
    header { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:14px 18px; border-bottom:1px solid var(--line); background:#171b21; position:sticky; top:0; z-index:2; }
    h1 { font-size:18px; margin:0; font-weight:650; }
    main { display:grid; grid-template-columns:320px 1fr 380px; min-height:calc(100vh - 58px); }
    aside, section { padding:16px; border-right:1px solid var(--line); }
    section:last-child { border-right:0; }
    label { display:grid; gap:6px; color:var(--muted); font-size:12px; margin-bottom:12px; }
    select, input, button { font:inherit; }
    select, input { width:100%; border:1px solid var(--line); background:#101319; color:var(--text); padding:9px 10px; border-radius:6px; }
    button { border:1px solid var(--line); background:#232a34; color:var(--text); padding:9px 11px; border-radius:6px; cursor:pointer; }
    button:hover { border-color:var(--accent); }
    .toolbar { display:flex; flex-wrap:wrap; gap:8px; }
    .metric { display:grid; grid-template-columns:1fr auto; gap:8px; padding:9px 0; border-bottom:1px solid #252c37; color:var(--muted); }
    .metric strong { color:var(--text); }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:10px; }
    .item { border:1px solid var(--line); border-radius:8px; padding:10px; background:var(--panel); min-height:98px; }
    .item h3 { margin:0 0 8px; font-size:14px; }
    .item p { margin:4px 0; color:var(--muted); font-size:12px; }
    .tabs { display:flex; gap:8px; margin-bottom:14px; }
    .tabs button.active { background:#20352d; border-color:var(--accent); }
    .events { display:grid; gap:8px; max-height:calc(100vh - 180px); overflow:auto; }
    .event { border:1px solid var(--line); border-radius:8px; padding:9px; background:var(--panel); }
    .event small { color:var(--muted); display:block; margin-bottom:4px; }
    .status { color:var(--accent); min-height:20px; }
    .bad { color:var(--bad); }
    @media (max-width: 980px) { main { grid-template-columns:1fr; } aside, section { border-right:0; border-bottom:1px solid var(--line); } }
  </style>
</head>
<body>
  <header>
    <h1>ToVIC Main Sandbox</h1>
    <div class="toolbar">
      <button id="tick">Tick</button>
      <button id="week">7 ticks</button>
      <button id="demo">Demo</button>
      <button id="reset">Reset</button>
    </div>
  </header>
  <main>
    <aside>
      <label>Mundo <select id="world"></select></label>
      <p class="status" id="status"></p>
      <div id="metrics"></div>
      <h2>Orden</h2>
      <label>Tipo
        <select id="orderType">
          <option value="research">research</option>
          <option value="build">build</option>
          <option value="army_move">army_move</option>
          <option value="diplomacy">diplomacy</option>
        </select>
      </label>
      <label>Pais <input id="country" placeholder="ENG"></label>
      <label>Payload JSON <input id="payload" placeholder='{"tech_id":"railroad"}'></label>
      <button id="send">Enviar orden</button>
    </aside>
    <section>
      <div class="tabs">
        <button class="active" data-tab="provinces">Provincias</button>
        <button data-tab="countries">Paises</button>
        <button data-tab="armies">Ejercitos</button>
        <button data-tab="factories">Fabricas</button>
      </div>
      <div class="grid" id="content"></div>
    </section>
    <section>
      <h2>Eventos</h2>
      <div class="events" id="events"></div>
    </section>
  </main>
  <script>
    let state = null;
    let tab = "provinces";

    async function api(path, options) {
      const res = await fetch(path, options);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.statusText);
      state = data;
      render();
    }

    function post(path, body) {
      return api(path, { method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify(body) })
        .catch(err => document.getElementById("status").innerHTML = `<span class="bad">${escapeHtml(err.message)}</span>`);
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[ch]));
    }

    function metric(label, value) {
      return `<div class="metric"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
    }

    function render() {
      if (!state) return;
      document.getElementById("status").textContent = state.message || "";
      document.getElementById("metrics").innerHTML = [
        metric("Mundo", state.world_label),
        metric("Fecha", state.date),
        metric("Tick", state.tick),
        metric("Paises", state.summary.countries),
        metric("Provincias", state.summary.provinces),
        metric("Eventos", state.summary.events)
      ].join("");

      const select = document.getElementById("world");
      const key = `${state.template}:${state.scenario}:${state.world_id}`;
      select.innerHTML = state.available_worlds.map(world => {
        const selected = world.key === key ? "selected" : "";
        return `<option ${selected} value="${escapeHtml(world.key)}">${escapeHtml(world.label)}</option>`;
      }).join("");

      renderContent();
      renderEvents();
    }

    function renderContent() {
      const content = document.getElementById("content");
      const rows = state[tab] || [];
      content.innerHTML = rows.map(item => {
        if (tab === "countries") {
          return `<article class="item"><h3>${escapeHtml(item.tag)} - ${escapeHtml(item.name)}</h3><p>Money: ${escapeHtml(item.money)}</p><p>Pop: ${escapeHtml(item.population)}</p><p>Techs: ${escapeHtml(item.researched_techs.length)}</p></article>`;
        }
        if (tab === "armies") {
          return `<article class="item"><h3>${escapeHtml(item.id)} - ${escapeHtml(item.name)}</h3><p>${escapeHtml(item.owner_tag)} en ${escapeHtml(item.province_id)}</p><p>Morale ${escapeHtml(item.morale)} | Org ${escapeHtml(item.organization)}</p></article>`;
        }
        if (tab === "factories") {
          return `<article class="item"><h3>${escapeHtml(item.id)}</h3><p>${escapeHtml(item.factory_type_id)} | ${escapeHtml(item.country_tag)}</p><p>Workers ${escapeHtml(item.current_workers)} | Active ${escapeHtml(item.active)}</p></article>`;
        }
        return `<article class="item"><h3>${escapeHtml(item.id)} - ${escapeHtml(item.name)}</h3><p>Owner: ${escapeHtml(item.owner_tag || "NEUTRAL")}</p><p>${escapeHtml(item.terrain_id)} | ${escapeHtml(item.resource_id || "-")}</p><p>Adj: ${escapeHtml(item.adjacent_provinces.join(", ") || "-")}</p></article>`;
      }).join("");
    }

    function describe(event) {
      const data = event.data || event;
      if (event.type === "TICK_ADVANCED") return `Tick ${data.tick || event.tick} | ${data.date || event.date}`;
      if (event.type === "LABOR_ALLOCATED") return `${data.country_tag} asigno workers`;
      if (event.type === "RGO_PRODUCED") return `${data.owner_tag} produjo ${data.amount} ${data.resource_id}`;
      if (event.type === "FACTORY_RAN") return `${data.country_tag} fabrico ${Object.keys(data.produced || {}).join(", ")}`;
      if (event.type === "TECH_RESEARCHED") return `${data.country_tag} investigo ${data.tech_id}`;
      if (event.type === "BUILD_STARTED") return `${data.country_tag} inicio ${data.building_type_id}`;
      if (event.type === "BUILD_COMPLETED") return `${data.country_tag} completo ${data.building_type_id}`;
      if (event.type === "ARMY_MOVED") return `Ejercito ${data.army_id}: ${data.from_province_id} -> ${data.to_province_id}`;
      if (event.type === "DIPLOMACY_ACTION") return `${data.country_tag} ${data.action} con ${data.target_tag}`;
      return event.type;
    }

    function renderEvents() {
      const events = (state.event_log || []).slice().reverse();
      document.getElementById("events").innerHTML = events.map(event => (
        `<article class="event"><small>tick ${escapeHtml(event.tick)} | ${escapeHtml(event.date)}</small>${escapeHtml(describe(event))}</article>`
      )).join("") || `<p>Sin eventos todavia.</p>`;
    }

    document.querySelectorAll(".tabs button").forEach(btn => {
      btn.addEventListener("click", () => {
        tab = btn.dataset.tab;
        document.querySelectorAll(".tabs button").forEach(item => item.classList.toggle("active", item === btn));
        renderContent();
      });
    });

    document.getElementById("world").addEventListener("change", event => {
      const [template, scenario, world_id] = event.target.value.split(":");
      post("/api/reset", { template, scenario, world_id });
    });
    document.getElementById("tick").addEventListener("click", () => post("/api/tick", { ticks: 1 }));
    document.getElementById("week").addEventListener("click", () => post("/api/tick", { ticks: 7 }));
    document.getElementById("demo").addEventListener("click", () => post("/api/demo", {}));
    document.getElementById("reset").addEventListener("click", () => post("/api/reset", {}));
    document.getElementById("send").addEventListener("click", () => {
      let payload = {};
      try { payload = JSON.parse(document.getElementById("payload").value || "{}"); }
      catch (err) { document.getElementById("status").innerHTML = `<span class="bad">Payload JSON invalido</span>`; return; }
      post("/api/order", { type: document.getElementById("orderType").value, country_tag: document.getElementById("country").value, payload });
    });

    api("/api/state");
  </script>
</body>
</html>
"""


class MainHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_text(WEB_HTML, "text/html; charset=utf-8")
            return
        if path == "/api/state":
            self._send_json(serialize_game_state(SESSION))
            return
        if path == "/api/worlds":
            self._send_json({"worlds": [world.__dict__ | {"key": world.key} for world in playable_worlds()]})
            return
        self._send_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            data = self._read_json()
            if path == "/api/tick":
                self._send_json(SESSION.run_ticks(int(data.get("ticks", 1))))
                return
            if path == "/api/demo":
                self._send_json(SESSION.demo_turn())
                return
            if path == "/api/order":
                self._send_json(SESSION.submit_order(data["type"], data["country_tag"], data.get("payload", {})))
                return
            if path == "/api/reset":
                world = None
                if data.get("template") and data.get("scenario"):
                    world = resolve_world(data["template"], data["scenario"], data.get("world_id"))
                self._send_json(SESSION.reset(world))
                return
            self._send_json({"error": "Ruta no encontrada"}, status=404)
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)

    def log_message(self, format: str, *args) -> None:
        print(f"[web] {self.address_string()} - {format % args}")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, body: str, content_type: str, status: int = 200) -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_static(self, path: str) -> None:
        file_path = (ROOT_DIR / path.lstrip("/")).resolve()
        if not file_path.is_file() or ROOT_DIR not in file_path.parents:
            self._send_json({"error": "Archivo no encontrado"}, status=404)
            return
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_web(args: argparse.Namespace) -> int:
    global SESSION
    SESSION = PlaytestSession(resolve_world(args.template, args.scenario, args.world))
    server = ThreadingHTTPServer((args.host, args.port), MainHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"ToVIC main sandbox en {url}")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
    return 0


def add_world_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO)
    parser.add_argument("--world", default=None)


def build_parser() -> argparse.ArgumentParser:
    world_args = argparse.ArgumentParser(add_help=False)
    add_world_args(world_args)

    parser = argparse.ArgumentParser(description="ToVIC unified engine sandbox.")
    add_world_args(parser)

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("worlds", parents=[world_args], help="Lista templates/scenarios/world variants disponibles.")
    subparsers.add_parser("audit", parents=[world_args], help="Carga, valida y avanza 1 tick en cada mundo disponible.")
    subparsers.add_parser("validate", parents=[world_args], help="Carga y valida un mundo puntual.")
    subparsers.add_parser("console", parents=[world_args], help="Abre el playtest interactivo de consola.")

    web_parser = subparsers.add_parser("web", parents=[world_args], help="Abre el playtest visual local.")
    web_parser.add_argument("--host", default=DEFAULT_HOST)
    web_parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    web_parser.add_argument("--open", action="store_true", help="Abre el navegador automaticamente.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    command = args.command or "console"
    if command == "worlds":
        print_worlds()
        return 0
    if command == "audit":
        return run_audit(args)
    if command == "validate":
        return run_validate(args)
    if command == "console":
        return run_console(args)
    if command == "web":
        return run_web(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
