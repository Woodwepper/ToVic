import json
from pathlib import Path

from model.world.world import World
from model.world.building_type import BuildingType
from model.world.casus_belli import CasusBelli
from model.world.factory_type import FactoryType
from model.world.government import Government
from model.world.modifier import Modifier
from model.world.province import Province
from model.world.resource import Resource
from model.world.technology import Technology
from model.world.terrain import Terrain
from model.world.unit_type import UnitType


class WorldLoader:
    """Lee los archivos JSON de un template y construye un objeto World."""

    @staticmethod
    def _find_world_dir(template_name: str) -> Path:
        candidates = [
            Path(f"templates/default_templates/{template_name}/world"),
            Path(f"templates/guild_templates/{template_name}/world"),
        ]
        for path in candidates:
            if path.exists():
                return path
        searched = "\n".join(f"  - {p}" for p in candidates)
        raise FileNotFoundError(
            f"Directorio world no encontrado para template='{template_name}'.\n"
            f"Rutas buscadas:\n{searched}"
        )

    @staticmethod
    def _load_json(directory: Path, filename: str) -> list:
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Archivo '{filename}' no encontrado en '{directory}'"
            )
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_world(template_name: str, world_id: str | None = None, world_name: str | None = None) -> World:
        """Carga un World completo desde los JSON de un template.
        
        Args:
            template_name: nombre del template (ej: 'victoria2', 'hoi4')
            world_id: ID del world (por defecto igual al template_name)
            world_name: nombre del world (por defecto igual al template_name)
        """
        world_dir = WorldLoader._find_world_dir(template_name)
        load = lambda filename: WorldLoader._load_json(world_dir, filename)

        buildings_data    = load("buildings.json")
        cb_types_data     = load("casus_belli_types.json")
        factory_types_data = load("factory_types.json")
        governments_data  = load("governments.json")
        modifiers_data    = load("modifiers.json")
        provinces_data    = load("provinces.json")
        resources_data    = load("resources.json")
        techs_data        = load("techs.json")
        terrains_data     = load("terrains.json")
        unit_types_data   = load("unit_types.json")

        buildings    = {b["id"]: BuildingType.from_dict(b) for b in buildings_data}
        factory_types = {k: FactoryType.from_dict(v) for k, v in factory_types_data.items()}
        unit_types   = {k: UnitType.from_dict(v) for k, v in unit_types_data.items()}

        return World(
            id=world_id or template_name,
            name=world_name or template_name,
            template_id=template_name,
            buildings=buildings,
            casus_belli_types=[CasusBelli.from_dict(cb) for cb in cb_types_data],
            factory_types=factory_types,
            governments=[Government.from_dict(g) for g in governments_data],
            modifiers=[Modifier.from_dict(m) for m in modifiers_data],
            provinces=[Province.from_dict(p) for p in provinces_data],
            resources=[Resource.from_dict(r) for r in resources_data],
            techs=[Technology.from_dict(t) for t in techs_data],
            terrains=[Terrain.from_dict(t) for t in terrains_data],
            unit_types=unit_types,
        )
