from __future__ import annotations

import argparse
import os
import shutil
from typing import Iterable

from loaders.game_loader import GameLoader
from loaders.managers.world_loader import WorldLoader, WorldOption
from model.entities.state.factory import Factory
from simulation import Order, OrderResult, OrderType, SimulationEngine


TEMPLATE_NAME = "victoria2"
SCENARIO_NAME = "1836"

COUNTRY_COLORS = {
    "ENG": "blue",
    "FRA": "magenta",
    "PRU": "cyan",
}

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
}


def color(text: object, name: str) -> str:
    if os.getenv("NO_COLOR"):
        return str(text)
    return f"{ANSI.get(name, '')}{text}{ANSI['reset']}"


def accent(text: object) -> str:
    return color(text, "cyan")


def ok(text: object) -> str:
    return color(text, "green")


def warn(text: object) -> str:
    return color(text, "yellow")


def bad(text: object) -> str:
    return color(text, "red")


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def terminal_width() -> int:
    return max(92, min(132, shutil.get_terminal_size((110, 30)).columns))


def rule(title: str = "") -> str:
    width = terminal_width()
    if not title:
        return "-" * width
    label = f" {title} "
    return label.center(width, "-")


def money(value: float) -> str:
    return f"${value:,.0f}"


def number(value: float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.2f}"
    return f"{value:,.0f}"


def short_stockpile(resources: dict[str, float], keys: Iterable[str] | None = None) -> str:
    selected = list(keys or resources.keys())
    parts = []
    for resource_id in selected:
        amount = resources.get(resource_id, 0)
        if amount:
            parts.append(f"{resource_id}:{number(amount)}")
    return "  ".join(parts) if parts else "sin stock"


def sort_id(value: str) -> tuple[int, int | str]:
    return (0, int(value)) if value.isdigit() else (1, value)


def option_label(option: WorldOption) -> str:
    suffix = " [base]" if option.is_default else ""
    return f"{option.name} ({option.id}){suffix}"


def choose_world_id(template_name: str, current_world_id: str | None = None) -> str:
    options = WorldLoader.list_worlds(template_name)
    if not options:
        return template_name

    clear_screen()
    print(rule("Mundos disponibles"))
    for index, option in enumerate(options, 1):
        marker = " *" if option.id == current_world_id else ""
        print(f"  {index}) {option_label(option)}{marker}")
    print("  0) Usar mundo base")

    raw = input("Mundo> ").strip().lower()
    if raw in {"", "0"}:
        return template_name
    if raw.isdigit() and 1 <= int(raw) <= len(options):
        return options[int(raw) - 1].id

    matching = next((option for option in options if option.id.lower() == raw), None)
    if matching:
        return matching.id

    print(warn("Seleccion invalida; usando mundo base."))
    return template_name


class ConsolePlaytest:
    def __init__(self, world_id: str | None = None):
        self.engine = SimulationEngine()
        self.world_id = world_id or TEMPLATE_NAME
        self.last_events: list[dict] = []
        self.last_results: list[OrderResult] = []
        self.status = ""
        self.game_state = None
        self.load_world(self.world_id)

    def load_world(self, world_id: str) -> None:
        self.world_id = world_id
        self.game_state = GameLoader.load(TEMPLATE_NAME, SCENARIO_NAME, world_id=world_id)
        self.game_state.scenario.year = 1836
        self.last_events = []
        self.last_results = []
        self.prepare_demo_state()
        self.status = (
            f"Mundo {self.game_state.world.name} cargado. "
            "Usa el menu para enviar ordenes, cambiar mundo o avanzar ticks."
        )

    def prepare_demo_state(self) -> None:
        worker_counts = [14, 12, 10, 8, 6, 6]
        provinces = sorted(self.game_state.provinces, key=lambda province: sort_id(province.id))
        for index, province in enumerate(provinces):
            province.rgo_workers = worker_counts[min(index, len(worker_counts) - 1)]

        prussia = self.game_state.get_country_state("PRU")
        if prussia:
            prussia.stockpile.set_amount("iron", max(prussia.stockpile.get_amount("iron"), 120))
            prussia.stockpile.set_amount("coal", max(prussia.stockpile.get_amount("coal"), 120))
            prussia.stockpile.set_amount("steel", prussia.stockpile.get_amount("steel"))

        factory_province_id = None
        if prussia and self.game_state.world.get_province(prussia.capital):
            factory_province_id = prussia.capital
        elif prussia:
            owned = next((province for province in self.game_state.provinces if province.owner_tag == "PRU"), None)
            factory_province_id = owned.id if owned else None

        if (
            factory_province_id
            and self.game_state.world.get_factory_type("steel_factory")
            and not any(factory.id == "demo_pru_steel_factory" for factory in self.game_state.factories)
        ):
            self.game_state.factories.append(
                Factory(
                    id="demo_pru_steel_factory",
                    factory_type_id="steel_factory",
                    country_tag="PRU",
                    province_id=factory_province_id,
                    level=1,
                    active=True,
                    efficiency=1.0,
                    current_workers=200,
                )
            )

    def run(self) -> None:
        while True:
            self.render()
            choice = input(accent("Orden> ")).strip().lower()
            if choice in {"0", "q", "quit", "exit"}:
                clear_screen()
                print("Playtest cerrado.")
                return
            if choice == "1":
                self.advance_ticks(1)
            elif choice == "2":
                self.advance_ticks(7)
            elif choice == "3":
                self.scripted_turn()
            elif choice == "4":
                self.create_research_order()
            elif choice == "5":
                self.create_build_order()
            elif choice == "6":
                self.create_army_move_order()
            elif choice == "7":
                self.create_diplomacy_order()
            elif choice == "8":
                self.show_event_log()
            elif choice == "9":
                self.switch_world()
            else:
                self.status = "Comando desconocido. Prueba con 1-9 o 0 para salir."

    def render(self) -> None:
        clear_screen()
        print(color("ToVIC Console Playtest", "bold"))
        print(
            f"Fecha {accent(self.game_state.get_date())} | "
            f"Tick {accent(self.game_state.current_tick)} | "
            f"Mundo {accent(self.game_state.world.name)} | "
            f"Scenario {accent(self.game_state.scenario.name)}"
        )
        print(rule())
        self.render_map()
        print(rule("Paises"))
        self.render_countries()
        print(rule("Ejercitos"))
        self.render_armies()
        print(rule("Industria"))
        self.render_factories()
        print(rule("Ultimo tick"))
        self.render_last_tick()
        print(rule("Menu"))
        print("  1) Avanzar 1 dia        2) Avanzar 7 dias       3) Turno demo")
        print("  4) Investigar tech      5) Construir edificio   6) Mover ejercito")
        print("  7) Diplomacia           8) Ver event log        9) Cambiar mundo")
        print("  0) Salir")
        print(rule())
        print(self.status)

    def render_map(self) -> None:
        print(rule("Mapa abstracto"))
        provinces = sorted(self.game_state.world.provinces, key=lambda province: sort_id(province.id))
        for world_province in provinces:
            adjacent = ", ".join(world_province.adjacent_provinces) or "ninguna"
            resource = world_province.resource_id or "none"
            print(
                f"  {self.province_card(world_province.id):<22} "
                f"{world_province.name:<26} "
                f"terrain={world_province.terrain_id:<9} resource={resource:<9} adj={adjacent}"
            )

    def province_card(self, province_id: str) -> str:
        province = self.game_state.get_province_state(province_id)
        world_province = self.game_state.world.get_province(province_id)
        if not province:
            return f"[{province_id}:???]"
        owner = province.owner_tag or "NEU"
        resource = world_province.resource_id if world_province and world_province.resource_id else "none"
        owner_text = color(owner, COUNTRY_COLORS.get(owner, "gray"))
        return f"[{province_id} {owner_text} {resource}]"

    def render_countries(self) -> None:
        for country in self.game_state.countries:
            tag = color(country.tag, COUNTRY_COLORS.get(country.tag, "white"))
            techs = ", ".join(country.researched_techs) if country.researched_techs else "ninguna"
            stock = short_stockpile(
                country.stockpile.resources,
                ["coal", "iron", "grain", "timber", "wine", "steel", "textiles"],
            )
            print(f"{tag:<15} {country.name:<22} money={money(country.money):>10} pop={country.population:>9,}")
            print(f"  stock: {stock}")
            print(f"  techs: {techs}")

    def render_armies(self) -> None:
        for army in self.game_state.armies:
            owner = color(army.owner_tag, COUNTRY_COLORS.get(army.owner_tag, "white"))
            adjacent = self.adjacent_text(army.province_id)
            print(
                f"[{army.id}] {army.name:<28} owner={owner:<14} "
                f"prov={army.province_id:<3} morale={army.morale:.3f} org={army.organization:.3f}"
            )
            print(f"    puede mover a: {adjacent}")

    def adjacent_text(self, province_id: str | None) -> str:
        if not province_id:
            return "sin provincia"
        province = self.game_state.world.get_province(province_id)
        if not province or not province.adjacent_provinces:
            return "ninguna"
        return ", ".join(province.adjacent_provinces)

    def render_factories(self) -> None:
        if not self.game_state.factories:
            print("No hay fabricas activas.")
            return
        for factory in self.game_state.factories:
            factory_type = self.game_state.world.get_factory_type(factory.factory_type_id)
            name = factory_type.name if factory_type else factory.factory_type_id
            state = ok("activa") if factory.active else warn("pausada")
            print(
                f"[{factory.id}] {name} | {factory.country_tag} prov={factory.province_id} "
                f"nivel={factory.level} eff={factory.efficiency:.2f} {state}"
            )
            if factory_type:
                print(f"    input: {factory_type.input_goods} -> output: {factory_type.output_goods}")

    def render_last_tick(self) -> None:
        if self.last_results:
            for result in self.last_results:
                status = ok("OK") if result.accepted else bad("FAIL")
                reason = "" if result.accepted else f" | {result.reason}"
                print(f"  {status} {result.order.type.value} de {result.order.country_tag}{reason}")
        else:
            print("  Sin ordenes procesadas en el ultimo tick.")

        if self.last_events:
            print("  Eventos:")
            for event in self.last_events[-8:]:
                print(f"    - {self.describe_event(event)}")
        else:
            print("  Sin eventos recientes.")

    def describe_event(self, event: dict) -> str:
        event_type = event.get("type", "UNKNOWN")
        if event_type == "TICK_ADVANCED":
            return f"TICK_ADVANCED -> {event.get('date')} (tick {event.get('tick')})"
        if event_type == "RGO_PRODUCED":
            return (
                f"RGO {event.get('owner_tag')} produjo {number(event.get('amount', 0))} "
                f"{event.get('resource_id')} en provincia {event.get('province_id')}"
            )
        if event_type == "FACTORY_RAN":
            return (
                f"FACTORY {event.get('factory_id')} consumio {event.get('consumed')} "
                f"y produjo {event.get('produced')}"
            )
        if event_type == "TECH_RESEARCHED":
            return f"TECH {event.get('country_tag')} investigo {event.get('tech_id')}"
        if event_type == "BUILD_STARTED":
            return f"BUILD {event.get('country_tag')} inicio {event.get('building_type_id')} en {event.get('province_id')}"
        if event_type == "ARMY_MOVED":
            return f"ARMY {event.get('army_id')} movio {event.get('from_province_id')} -> {event.get('to_province_id')}"
        if event_type == "DIPLOMACY_ACTION":
            return (
                f"DIPLOMACY {event.get('country_tag')} {event.get('action')} "
                f"con {event.get('target_tag')} = {event.get('relation')}"
            )
        if event_type == "CB_EXPIRED":
            return f"CB {event.get('cb_id')} expiro"
        return str(event)

    def advance_ticks(self, ticks: int) -> None:
        self.last_events, self.last_results = self.engine.run(self.game_state, ticks)
        self.status = f"Avanzaste {ticks} dia(s). Eventos generados: {len(self.last_events)}."

    def submit_orders_and_tick(self, orders: list[Order]) -> None:
        if not orders:
            self.status = "No se envio ninguna orden."
            return
        for order in orders:
            self.game_state.submit_order(order)
        self.last_events, self.last_results = self.engine.tick_forward(self.game_state)
        accepted = sum(1 for result in self.last_results if result.accepted)
        self.status = f"Procesadas {len(orders)} orden(es): {accepted} aceptada(s), {len(orders) - accepted} rechazada(s)."

    def scripted_turn(self) -> None:
        orders: list[Order] = []

        france = self.game_state.get_country_state("FRA")
        if france and "military_science" not in france.researched_techs:
            orders.append(Order(OrderType.RESEARCH, "FRA", {"tech_id": "military_science"}))

        england = self.game_state.get_country_state("ENG")
        if england and england.money >= 5000:
            orders.append(Order(OrderType.BUILD, "ENG", {"building_type_id": "factory", "province_id": "1"}))

        army = self.game_state.get_army_state("1")
        if army:
            world_province = self.game_state.world.get_province(army.province_id)
            adjacent_ids = world_province.adjacent_provinces if world_province else []
            if adjacent_ids:
                destination = adjacent_ids[0]
                orders.append(Order(OrderType.ARMY_MOVE, "ENG", {"army_id": "1", "to_province_id": destination}))

        orders.append(
            Order(
                OrderType.DIPLOMACY,
                "ENG",
                {"action": "improve_relations", "target_tag": "FRA", "amount": 10},
            )
        )
        self.submit_orders_and_tick(orders)

    def create_research_order(self) -> None:
        country = self.choose_country("Pais que investigara")
        if not country:
            return
        available = [tech for tech in self.game_state.world.techs if tech.id not in country.researched_techs]
        tech = self.choose_from("Tecnologia", available, lambda item: f"{item.id} ({item.activation_year})")
        if not tech:
            return
        self.submit_orders_and_tick([Order(OrderType.RESEARCH, country.tag, {"tech_id": tech.id})])

    def create_build_order(self) -> None:
        country = self.choose_country("Pais constructor")
        if not country:
            return
        owned_provinces = [province for province in self.game_state.provinces if province.owner_tag == country.tag]
        province = self.choose_from("Provincia", owned_provinces, lambda item: f"{item.id} - {item.name}")
        if not province:
            return
        building_types = list(self.game_state.world.buildings.values())
        building_type = self.choose_from(
            "Edificio",
            building_types,
            lambda item: f"{item.id} | costo {money(item.construction_cost)} | tech {item.required_technology or 'none'}",
        )
        if not building_type:
            return
        self.submit_orders_and_tick(
            [
                Order(
                    OrderType.BUILD,
                    country.tag,
                    {"building_type_id": building_type.id, "province_id": province.id},
                )
            ]
        )

    def create_army_move_order(self) -> None:
        army = self.choose_from(
            "Ejercito",
            self.game_state.armies,
            lambda item: f"{item.id} - {item.name} ({item.owner_tag}) en provincia {item.province_id}",
        )
        if not army:
            return
        world_province = self.game_state.world.get_province(army.province_id)
        adjacent_ids = world_province.adjacent_provinces if world_province else []
        destinations = [self.game_state.get_province_state(pid) for pid in adjacent_ids]
        destinations = [province for province in destinations if province is not None]
        province = self.choose_from("Destino adyacente", destinations, lambda item: f"{item.id} - {item.name}")
        if not province:
            return
        self.submit_orders_and_tick(
            [
                Order(
                    OrderType.ARMY_MOVE,
                    army.owner_tag,
                    {"army_id": army.id, "to_province_id": province.id},
                )
            ]
        )

    def create_diplomacy_order(self) -> None:
        country = self.choose_country("Pais origen")
        if not country:
            return
        targets = [candidate for candidate in self.game_state.countries if candidate.tag != country.tag]
        target = self.choose_from("Pais objetivo", targets, lambda item: f"{item.tag} - {item.name}")
        if not target:
            return
        action = self.choose_from(
            "Accion",
            ["improve_relations", "worsen_relations"],
            lambda item: item,
        )
        if not action:
            return
        amount_text = input("Cambio de relacion [25]: ").strip()
        amount = int(amount_text) if amount_text.isdigit() else 25
        self.submit_orders_and_tick(
            [
                Order(
                    OrderType.DIPLOMACY,
                    country.tag,
                    {"action": action, "target_tag": target.tag, "amount": amount},
                )
            ]
        )

    def choose_country(self, label: str):
        return self.choose_from(label, self.game_state.countries, lambda item: f"{item.tag} - {item.name}")

    def choose_from(self, label: str, items: list, describe):
        if not items:
            self.status = f"No hay opciones para {label}."
            return None
        print(rule(label))
        for index, item in enumerate(items, 1):
            print(f"  {index}) {describe(item)}")
        print("  0) Cancelar")
        raw = input(f"{label}> ").strip()
        if raw in {"", "0"}:
            self.status = "Accion cancelada."
            return None
        if not raw.isdigit() or not (1 <= int(raw) <= len(items)):
            self.status = "Seleccion invalida."
            return None
        return items[int(raw) - 1]

    def show_event_log(self) -> None:
        clear_screen()
        print(rule("Event log"))
        events = self.game_state.get_event_log(limit=24)
        if not events:
            print("No hay eventos registrados todavia.")
        for event in events:
            print(
                f"tick={event.get('tick'):<4} date={event.get('date'):<10} "
                f"{event.get('type'):<18} {event.get('data')}"
            )
        input("\nEnter para volver al playtest...")

    def switch_world(self) -> None:
        next_world_id = choose_world_id(TEMPLATE_NAME, self.world_id)
        if next_world_id == self.world_id:
            self.status = f"Sigues en {self.game_state.world.name}."
            return
        self.load_world(next_world_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Playtest de consola para ToVIC.")
    parser.add_argument("--world", help="ID del mundo a cargar dentro del template victoria2.")
    parser.add_argument("--list-worlds", action="store_true", help="Lista mundos disponibles y sale.")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()
        if args.list_worlds:
            for option in WorldLoader.list_worlds(TEMPLATE_NAME):
                print(option_label(option))
            raise SystemExit(0)
        ConsolePlaytest(args.world or choose_world_id(TEMPLATE_NAME)).run()
    except KeyboardInterrupt:
        clear_screen()
        print("Playtest cerrado.")
