from pathlib import Path
from model.world.world import World
from model.scenario.scenario import Scenario
from model.entities.state.game_state import GameState
from model.scenario.casus_belli_snapshot import CasusBelliSnapshot
from loaders.managers.scenario_loader import ScenarioLoader

class WorldLoader:
    """Esta clase es la responsable de cargar un escenario y convertirlo en un GameState inicial."""
    
    @staticmethod
    def load_world(name: str, scenario_name: str) -> GameState:
        scenario = ScenarioLoader.load_scenario_from_file(name, scenario_name)
        world = World()  # Aquí podríamos cargar datos globales del mundo si los tuviéramos
        return GameState(scenario=scenario, world=world)