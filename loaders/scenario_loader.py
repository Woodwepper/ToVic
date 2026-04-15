import json
from pathlib import Path
from model.scenario.army import Army
from model.scenario.country import Country
from model.scenario.province import Province
from model.scenario.scenario import Scenario
from model.scenario.casus_belli_snapshot import CasusBelli

def load_json(name: str, year: str) -> dict:
    """Carga los JSONs del scenario"""
    path = f"templates/default_templates/{name}/scenario/{year}"
    data = {
        "armies": json.load(open(Path(path) / "armies.json")),
        "casus_belli": json.load(open(Path(path) / "casus_belli.json")),
        "countries": json.load(open(Path(path) / "countries.json")),
        "provinces": json.load(open(Path(path) / "provinces.json")),
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




