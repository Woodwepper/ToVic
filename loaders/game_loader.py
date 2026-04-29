
from model.entities.state.game_state import GameState
from model.world.world import World
from model.scenario.scenario import Scenario
from loaders.managers.world_loader import WorldLoader
from loaders.managers.scenario_loader import ScenarioLoader
from loaders.validators.world_data_validator import WorldDataValidator
from loaders.validators.scenario_data_validator import ScenarioDataValidator


class GameLoader:
    """Orquesta la carga completa de una partida:
    1. Carga el World desde el template (WorldLoader)
    2. Carga el Scenario desde los JSONs (ScenarioLoader)
    3. Valida el World internamente (WorldDataValidator)
    4. Valida el Scenario internamente (ScenarioDataValidator)
    5. Crea y devuelve el GameState inicial
    """

    @staticmethod
    def load(template_name: str, scenario_name: str, world_id: str | None = None) -> GameState:
        world: World = WorldLoader.load_world(template_name, world_id=world_id)
        scenario: Scenario = ScenarioLoader.load_scenario_from_file(template_name, scenario_name)

        errors: list[str] = []

        world_errors = WorldDataValidator(world).validate()
        if world_errors:
            errors.append(f"[WORLD] {len(world_errors)} error(s):")
            errors.extend(f"  - {e}" for e in world_errors)

        scenario_errors = ScenarioDataValidator(scenario).validate()
        if scenario_errors:
            errors.append(f"[SCENARIO] {len(scenario_errors)} error(s):")
            errors.extend(f"  - {e}" for e in scenario_errors)

        if errors:
            raise ValueError("No se puede iniciar la partida, se encontraron errores:\n" + "\n".join(errors))

        return GameState(world=world, scenario=scenario)
