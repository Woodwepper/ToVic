import json
from pathlib import Path
from model.world.world import World
from model.world.province import Province
from model.world.technology import Technology
from model.world.unit_type import UnitType
from model.world.terrain import Terrain
from model.world.resource import Resource
from model.world.building import Building
from model.world.factory_type import FactoryType
from model.world.government import Government
from model.world.modifier import Modifier
from model.world.casus_belli import CasusBelli


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
    provinces_path = pick_template_file(template, "provinces.json")
    resources_path = pick_template_file(template, "resources.json")
    techs_path = pick_template_file(template, "techs.json")
    terrains_path = pick_template_file(template, "terrains.json")
    units_path = pick_template_file(template, "unit_types.json")
    buildings_path = pick_template_file(template, "buildings.json")
    factory_types_path = pick_template_file(template, "factory_types.json")
    governments_path = pick_template_file(template, "governments.json")
    modifiers_path = pick_template_file(template, "modifiers.json")
    casus_belli_path = pick_template_file(template, "casus_belli_types.json")

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
    with buildings_path.open() as f:
        buildings_data = json.load(f)
    with factory_types_path.open() as f:
        factory_types_data = json.load(f)
    with governments_path.open() as f:
        governments_data = json.load(f)
    with modifiers_path.open() as f:
        modifiers_data = json.load(f)
    with casus_belli_path.open() as f:
        casus_belli_data = json.load(f)

    # JSONs are direct arrays, not objects with keys
    return World(
        id=template,
        name=template.capitalize(),
        provinces=[Province.from_dict(p) for p in (provinces_data if isinstance(provinces_data, list) else provinces_data.get("provinces", []))],
        resources=[Resource.from_dict(r) for r in (resources_data if isinstance(resources_data, list) else resources_data.get("resources", []))],
        techs=[Technology.from_dict(t) for t in (techs_data if isinstance(techs_data, list) else techs_data.get("technologies", []))],
        terrains=[Terrain.from_dict(t) for t in (terrains_data if isinstance(terrains_data, list) else terrains_data.get("terrains", []))],
        unit_types={u["id"]: UnitType.from_dict(u) for u in (units_data if isinstance(units_data, list) else units_data.get("unit_types", []))},
        buildings={b["id"]: Building.from_dict(b) for b in (buildings_data if isinstance(buildings_data, list) else buildings_data.get("buildings", []))},
        factory_types={f["id"]: FactoryType.from_dict(f) for f in (factory_types_data if isinstance(factory_types_data, list) else factory_types_data.get("factory_types", []))},
        governments=[Government.from_dict(g) for g in (governments_data if isinstance(governments_data, list) else governments_data.get("governments", []))],
        modifiers=[Modifier.from_dict(m) for m in (modifiers_data if isinstance(modifiers_data, list) else modifiers_data.get("modifiers", []))],
        casus_belli_types=[CasusBelli.from_dict(c) for c in (casus_belli_data if isinstance(casus_belli_data, list) else casus_belli_data.get("casus_belli", []))],
    )



