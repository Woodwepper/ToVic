import json
from model.entities.state.army import Army
from model.entities.state.country_state import CountryState
from model.entities.state.province_state import ProvinceState
from model.scenario.scenario import Scenario

def load_json(name: str, year: str) -> dict:
    path = f"templates/default_templates/{name}/scenario/{year}"
    return {
        "armies": json.load(open(f"{path}/armies.json")),
        "countries": json.load(open(f"{path}/countries.json")),
        "provinces": json.load(open(f"{path}/provinces.json"))
    }


def load_scenario(name: str, year: str):
    
    data = load_json(name, year)
    
    return Scenario(
        id=f"{name}_{year}",
        name=f"{name.capitalize()} {year}",
        year=int(year),
        country_states=[CountryState.from_dict(c) for c in data["countries"]["countries"]],
        province_states=[ProvinceState.from_dict(p) for p in data["provinces"]["provinces"]],
        armies=[Army.from_dict(a) for a in data["armies"]["armies"]],
        description=f"Escenario de {name.capitalize()} para {year}"
    )

