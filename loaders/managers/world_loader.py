import json
from pathlib import Path
from typing import NamedTuple

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


class WorldOption(NamedTuple):
    id: str
    name: str
    path: Path
    is_default: bool = False


class WorldLoader:
    """Lee los archivos JSON de un template y construye un objeto World."""

    WORLD_FILES = (
        "buildings.json",
        "casus_belli_types.json",
        "factory_types.json",
        "governments.json",
        "modifiers.json",
        "provinces.json",
        "resources.json",
        "techs.json",
        "terrains.json",
        "unit_types.json",
    )

    @staticmethod
    def _template_roots(template_name: str) -> list[Path]:
        return [
            Path(f"templates/default_templates/{template_name}"),
            Path(f"templates/guild_templates/{template_name}"),
        ]

    @staticmethod
    def _find_world_dir(template_name: str) -> Path:
        candidates = [root / "world" for root in WorldLoader._template_roots(template_name)]
        for path in candidates:
            if path.exists():
                return path
        searched = "\n".join(f"  - {p}" for p in candidates)
        raise FileNotFoundError(
            f"Directorio world no encontrado para template='{template_name}'.\n"
            f"Rutas buscadas:\n{searched}"
        )

    @staticmethod
    def _find_variant_world_dir(template_name: str, world_id: str) -> Path:
        candidates = [root / "worlds" / world_id for root in WorldLoader._template_roots(template_name)]
        for path in candidates:
            if path.exists():
                return path
        searched = "\n".join(f"  - {p}" for p in candidates)
        raise FileNotFoundError(
            f"Directorio world_id='{world_id}' no encontrado para template='{template_name}'.\n"
            f"Rutas buscadas:\n{searched}"
        )

    @staticmethod
    def _resolve_world_dirs(template_name: str, world_id: str | None) -> tuple[Path, list[Path]]:
        base_world_dir = WorldLoader._find_world_dir(template_name)
        if world_id in (None, "", template_name, "default", "base"):
            return base_world_dir, []

        variant_dir = WorldLoader._find_variant_world_dir(template_name, world_id)
        return variant_dir, [base_world_dir]

    @staticmethod
    def _load_json(directory: Path, filename: str, fallback_directories: list[Path] | None = None) -> list:
        search_dirs = [directory, *(fallback_directories or [])]
        for search_dir in search_dirs:
            path = search_dir / filename
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        searched = "\n".join(f"  - {path / filename}" for path in search_dirs)
        raise FileNotFoundError(
            f"Archivo '{filename}' no encontrado.\n"
            f"Rutas buscadas:\n{searched}"
        )

    @staticmethod
    def _display_name(world_id: str) -> str:
        return world_id.replace("_", " ").replace("-", " ").title()

    @staticmethod
    def list_worlds(template_name: str) -> list[WorldOption]:
        """Lista el mundo base y las variantes disponibles para un template."""
        worlds: list[WorldOption] = []
        seen_ids: set[str] = set()

        try:
            base_world_dir = WorldLoader._find_world_dir(template_name)
        except FileNotFoundError:
            base_world_dir = None

        if base_world_dir:
            worlds.append(
                WorldOption(
                    id=template_name,
                    name=f"{WorldLoader._display_name(template_name)} Base",
                    path=base_world_dir,
                    is_default=True,
                )
            )
            seen_ids.add(template_name)

        for root in WorldLoader._template_roots(template_name):
            variants_dir = root / "worlds"
            if not variants_dir.exists():
                continue
            for path in sorted(p for p in variants_dir.iterdir() if p.is_dir()):
                world_id = path.name
                if world_id in seen_ids:
                    continue
                if not any((path / filename).exists() for filename in WorldLoader.WORLD_FILES):
                    continue
                worlds.append(
                    WorldOption(
                        id=world_id,
                        name=WorldLoader._display_name(world_id),
                        path=path,
                    )
                )
                seen_ids.add(world_id)

        return worlds

    @staticmethod
    def load_world(template_name: str, world_id: str | None = None, world_name: str | None = None) -> World:
        """Carga un World completo desde los JSON de un template.
        
        Args:
            template_name: nombre del template (ej: 'victoria2', 'hoi4')
            world_id: ID del world (por defecto igual al template_name)
            world_name: nombre del world (por defecto igual al template_name)
        """
        world_dir, fallback_dirs = WorldLoader._resolve_world_dirs(template_name, world_id)
        resolved_world_id = world_id or template_name
        load = lambda filename: WorldLoader._load_json(world_dir, filename, fallback_dirs)

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
            id=resolved_world_id,
            name=world_name or WorldLoader._display_name(resolved_world_id),
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
