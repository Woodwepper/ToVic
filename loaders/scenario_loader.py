import json
from pathlib import Path
from model.scenario.army import Army
from model.scenario.country import Country
from model.scenario.province import Province
from model.scenario.scenario import Scenario

def load_json(name: str, year: str) -> dict:
    path = f"templates/default_templates/{name}/scenario/{year}"
    data = {
        "armies": json.load(open(f"{path}/armies.json")),
        "countries": json.load(open(f"{path}/countries.json")),
        "provinces": json.load(open(f"{path}/provinces.json"))
    }
    
    # Cargar generals si existen
    generals_path = Path(f"{path}/generals.json")
    if generals_path.exists():
        with generals_path.open() as f:
            data["generals"] = json.load(f)
    else:
        data["generals"] = {"generals": []}
    
    # Cargar modifiers si existen
    modifiers_path = Path(f"{path}/modifiers.json")
    if modifiers_path.exists():
        with modifiers_path.open() as f:
            data["modifiers"] = json.load(f)
    else:
        data["modifiers"] = {"country_modifiers": [], "province_modifiers": []}
    
    return data


def load_scenario(name: str, year: str):
    
    data = load_json(name, year)
    
    return Scenario(
        id=f"{name}_{year}",
        name=f"{name.capitalize()} {year}",
        year=int(year),
        countries=[Country.from_dict(c) for c in data["countries"]["countries"]],
        provinces=[Province.from_dict(p) for p in data["provinces"]["provinces"]],
        armies=[Army.from_dict(a) for a in data["armies"]["armies"]],
        description=f"Escenario de {name.capitalize()} para {year}"
    )

