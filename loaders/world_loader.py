from model.world.world import World
from model.scenario.scenario import Scenario
from model.entities.state.game_state import GameState
from loaders.managers.template_manager import load_world_data
from loaders.scenario_loader import load_scenario
from loaders.validators.world_data_validator import WorldDataValidator, ScenarioWorldValidator
from loaders.validators.scenario_data_validator import ScenarioDataValidator


def load_world(template: str) -> World:
    """Carga la definición del mundo desde templates"""
    return load_world_data(template)


def load_game(template: str, scenario_year: str) -> tuple[World, Scenario]:
    """Carga World + Scenario juntos"""
    world = load_world_data(template)
    scenario = load_scenario(template, scenario_year)
    return world, scenario


def initialize_game(template: str, scenario_year: str, current_tick: int = 0) -> GameState:
    """Orquestador master: carga World + Scenario + inicializa GameState"""
    world, scenario = load_game(template, scenario_year)

    validation_errors: list[str] = []

    world_ok, world_errors = WorldDataValidator(world).validate()
    if not world_ok:
        validation_errors.extend(world_errors)

    scenario_ok, scenario_errors = ScenarioDataValidator(scenario, world).validate()
    if not scenario_ok:
        validation_errors.extend(scenario_errors)

    cross_ok, cross_errors = ScenarioWorldValidator(scenario, world).validate()
    if not cross_ok:
        validation_errors.extend(cross_errors)

    if validation_errors:
        formatted_errors = "\n - ".join(validation_errors)
        raise ValueError(f"No se pudo inicializar el juego por errores de validación:\n - {formatted_errors}")

    game_state = GameState(world, scenario, current_tick)
    return game_state

