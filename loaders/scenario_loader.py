from pathlib import Path
from model.scenario.army import Army
from model.scenario.building_snapshot import BuildingSnapshot
from model.scenario.casus_belli_snapshot import CasusBelliSnapshot
from model.scenario.country import Country
from model.scenario.general import General
from model.scenario.province_snapshot import ProvinceSnapshot
from model.scenario.scenario import Scenario
import json

class ScenarioLoader:
    """Esta clase es la responsable de deserializar archivos 
    JSON de escenarios y convertirlos en objetos Scenario."""

    @staticmethod
    def _find_file(template_name: str, scenario_name: str, filename: str) -> Path:

        possible_paths = [
            Path(f"templates/default_templates/{template_name}/scenario/{scenario_name}/{filename}"),
            Path(f"templates/guild_templates/{template_name}/scenario/{scenario_name}/{filename}"),
        ]

        for path in possible_paths:
            if path.exists():
                return path
        searched = "\n".join(f"  - {p}" for p in possible_paths)
        raise FileNotFoundError(
            f"Archivo '{filename}' no encontrado para template: '{template_name}', scenario: '{scenario_name}'.\n"
            f"Rutas buscadas:\n{searched}"
        )        

    @staticmethod
    def load_scenario_from_file(name, scenario_name) -> Scenario:

        army_path = ScenarioLoader._find_file(name, scenario_name, "armies.json")
        buildings_path = ScenarioLoader._find_file(name, scenario_name, "buildings.json")
        casus_belli_path = ScenarioLoader._find_file(name, scenario_name, "casus_belli.json")
        country_path = ScenarioLoader._find_file(name, scenario_name, "countries.json")
        general_path = ScenarioLoader._find_file(name, scenario_name, "generals.json")
        province_path = ScenarioLoader._find_file(name, scenario_name, "provinces.json")

        with open(army_path, 'r') as f:
            armies_data = json.load(f)
        with open(buildings_path, 'r') as f:
            buildings_data = json.load(f)
        with open(casus_belli_path, 'r') as f:
            casus_belli_data = json.load(f)
        with open(country_path, 'r') as f:
            countries_data = json.load(f)
        with open(general_path, 'r') as f:
            generals_data = json.load(f)
        with open(province_path, 'r') as f:
            provinces_data = json.load(f)

        scenario = Scenario(
            id=scenario_name,
            name=scenario_name,
            countries=[Country.from_dict(c) for c in countries_data],
            generals=[General.from_dict(g) for g in generals_data],
            provinces=[ProvinceSnapshot.from_dict(p) for p in provinces_data],
            armies=[Army.from_dict(a) for a in armies_data],
            buildings=[BuildingSnapshot.from_dict(b) for b in buildings_data],
            casus_belli=[CasusBelliSnapshot.from_dict(cb) for cb in casus_belli_data]
        )
        return scenario