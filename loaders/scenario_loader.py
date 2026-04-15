import json
from pathlib import Path
from model.scenario.army import Army
from model.scenario.country import Country
from model.scenario.province import Province
from model.scenario.scenario import Scenario
from model.scenario.casus_belli_snapshot import CasusBelli

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
    data = {
        "armies": json.load(open(pick_scenario_file(name, year, "armies.json"))),
        "casus_belli": json.load(open(pick_scenario_file(name, year, "casus_belli.json"))),
        "countries": json.load(open(pick_scenario_file(name, year, "countries.json"))),
        "provinces": json.load(open(pick_scenario_file(name, year, "provinces.json"))),
    }
    return data

def load_scenario(name: str, year: str) -> Scenario:
    """Carga un scenario completo desde JSON"""
    data = load_json(name, year)
    
    # Los JSONs son arrays directamente (no objetos con keys)
    countries = [Country.from_dict(c) for c in data["countries"]]
    provinces = [Province.from_dict(p) for p in data["provinces"]]
    armies = [Army.from_dict(a) for a in data["armies"]]
    casus_belli = [CasusBelli.from_dict(c) for c in data["casus_belli"]]
    
    # Extraer año del parámetro (string "1836" -> int)
    scenario_year = int(year)
    
    return Scenario(
        id=f"{name}_{year}",
        name=f"{name} - {year}",
        year=scenario_year,
        countries=countries,
        provinces=provinces,
        armies=armies,
        casus_belli=casus_belli,
    )




