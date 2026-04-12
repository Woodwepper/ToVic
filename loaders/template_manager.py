import json
from pathlib import Path
from model.world.world import World
from model.world.province import Province
from model.world.technology import Technologies
from model.world.unit_type import UnitType
from model.world.terrain import Terrain
from model.world.resource import Resource


def list_available_worlds() -> list[str]:
    path = Path("templates/default_templates").iterdir()
    path2 = Path("templates/guild_templates").iterdir()
    return [p.name for p in path if p.is_dir()] + [p.name for p in path2 if p.is_dir()]

def list_available_scenarios(template_name: str) -> list[str]:
    path1 = Path(f"templates/default_templates/{template_name}/scenario")
    path2 = Path(f"templates/guild_templates/{template_name}/scenario")

    scenarios = []

    if path1.exists():
        scenarios.extend(item.name for item in path1.iterdir())

    if path2.exists():
        scenarios.extend(item.name for item in path2.iterdir())

    return scenarios

def pick_template_file(template: str, filename: str) -> Path:
    default_path = Path(f"templates/default_templates/{template}/world/{filename}")
    guild_path = Path(f"templates/guild_templates/{template}/world/{filename}")

    if default_path.exists():
        return default_path
    if guild_path.exists():
        return guild_path

    raise FileNotFoundError(f"No se encontró '{filename}' en la plantilla '{template}'")

def load_world_data(template: str) -> World:
    provinces_path= pick_template_file(template, "provinces.json")
    resources_path = pick_template_file(template, "resources.json")
    techs_path = pick_template_file(template, "techs.json")
    terrains_path = pick_template_file(template, "terrains.json")
    units_path = pick_template_file(template, "unit_types.json")

    with provinces_path.open() as f:
        provinces_data = json.load(f)

    with resources_path.open() as f:
        resources_data = json.load(f)

    with techs_path.open() as f:
        techs_data = json.load(f)

    with terrains_path.open() as f:
        terrains_data = json.load(f)
    
    with units_path.open() as f:
        units_data = json.load(f)

    return World(
        id=template,
        name=template.capitalize(),
        provinces=[Province.from_dict(p) for p in provinces_data.get("provinces", [])],
        resources=[Resource.from_dict(r) for r in resources_data.get("resources", [])],
        techs=[Technologies.from_dict(t) for t in techs_data.get("technologies", [])],
        terrains=[Terrain.from_dict(t) for t in terrains_data.get("terrains", [])],
        unit_types={u["id"]: UnitType.from_dict(u) for u in units_data.get("unit_types", [])}
    )



