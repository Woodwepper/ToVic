import json
from pathlib import Path
from model.scenario.army import Army
from model.scenario.building_snapshot import BuildingSnapshot
from model.scenario.country import Country
from model.scenario.general import General
from model.scenario.province_snapshot import ProvinceSnapshot
from model.scenario.scenario import Scenario
from model.scenario.casus_belli_snapshot import CasusBelliSnapshot

def pick_scenario_file(template: str, year: str, filename: str) -> Path:
    """Busca archivo de scenario en default o guild templates"""
    default_path = Path(f"templates/default_templates/{template}/scenario/{year}/{filename}")
    guild_path = Path(f"templates/guild_templates/{template}/scenario/{year}/{filename}")
    
    if default_path.exists():
        return default_path
    if guild_path.exists():
        return guild_path
    
    raise FileNotFoundError(f"No se encontró '{filename}' en scenario '{template}/{year}'")

def load_json(name: str, year: str) -> dict:
    """Carga los JSONs del scenario desde default o guild templates"""
    try:
        buildings_data = json.load(open(pick_scenario_file(name, year, "buildings.json")))
    except FileNotFoundError:
        buildings_data = []

    data = {
        "armies": json.load(open(pick_scenario_file(name, year, "armies.json"))),
        "buildings": buildings_data,
        "casus_belli": json.load(open(pick_scenario_file(name, year, "casus_belli.json"))),
        "countries": json.load(open(pick_scenario_file(name, year, "countries.json"))),
        "generals": json.load(open(pick_scenario_file(name, year, "generals.json"))),
        "provinces": json.load(open(pick_scenario_file(name, year, "provinces.json"))),
    }
    return data

def load_scenario(name: str, year: str) -> Scenario:
    """Carga un scenario completo desde JSON"""
    data = load_json(name, year)
    
    # Los JSONs son arrays directamente (no objetos con keys)
    countries = [Country.from_dict(c) for c in data["countries"]]
    generals = [General.from_dict(g) for g in data["generals"]]
    provinces = [ProvinceSnapshot.from_dict(p) for p in data["provinces"]]
    armies = [Army.from_dict(a) for a in data["armies"]]
    buildings = [BuildingSnapshot.from_dict(b) for b in data["buildings"]]
    casus_belli = [CasusBelliSnapshot.from_dict(c) for c in data["casus_belli"]]
    
    # Extraer año del parámetro (string "1836" -> int)
    scenario_year = int(year)
    
    return Scenario(
        id=f"{name}_{year}",
        name=f"{name} - {year}",
        year=scenario_year,
        countries=countries,
        generals=generals,
        provinces=provinces,
        armies=armies,
        buildings=buildings,
        casus_belli=casus_belli,
    )




