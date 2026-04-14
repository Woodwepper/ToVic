from dataclasses import dataclass, field, asdict
from model.world.government import Government
from model.world.modifier import Modifier
from model.world.province import Province
from model.world.technology import Technologies
from model.world.resource import Resource
from model.world.terrain import Terrain
from model.world.unit_type import UnitType
from model.world.building import Building
from model.world.factory_type import FactoryType
@dataclass
class World:
    id: str
    name: str
    provinces: list[Province] = field(default_factory=Province)
    resources: list[Resource] = field(default_factory=Resource)
    techs: list[Technologies] = field(default_factory=Technologies)
    terrains: list[Terrain] = field(default_factory=Terrain)
    unit_types: dict[str, UnitType] = field(default_factory=dict)  
    governments: list[Government] = field(default_factory=list)
    modifiers: list[Modifier] = field(default_factory=list)
    casus_belli_types: list[dict[str, str]] = field(default_factory=list)  # {id: description}
    buildings: list[Building] = field(default_factory=list)  # {id: {name, category, description, construction_cost, maintenance_cost, construction_time, modifiers, required_technology, requires_port}}
    factory_types: list[FactoryType] = field(default_factory=list)  # {id: {name, input_goods, output_goods, needed_workers, production_capacity, maintenance_cost}}
    template_id: str | None = None  # ID de plantilla base, si aplica

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'World':
        return cls(
            id=data["id"],
            name=data["name"],
            provinces=[Province(**p) for p in data.get("provinces", [])],
            resources=[Resource(**r) for r in data.get("resources", [])],
            techs=[Technologies(**t) for t in data.get("techs", [])],
            terrains=[Terrain(**t) for t in data.get("terrains", [])],
            unit_types={k: UnitType.from_dict(v) for k, v in data.get("unit_types", {}).items()},
            governments=[Government.from_dict(g) for g in data.get("governments", [])],
            modifiers=[Modifier.from_dict(m) for m in data.get("modifiers", [])],
            casus_belli_types=[cb for cb in data.get("casus_belli_types", [])],
            buildings=[Building.from_dict(b) for b in data.get("buildings", [])],
            factory_types=[FactoryType.from_dict(f) for f in data.get("factory_types", [])],
            template_id=data.get("template_id"),
        )
    
    def get_name(self) -> str:
        """Obtiene el nombre del mundo"""
        return self.name

    def get_province(self, province_id: int) -> Province | None:
        """Obtiene una provincia por su ID"""
        return next((p for p in self.provinces if p.id == province_id), None)

    def get_resource(self, resource_id: str) -> Resource | None:
        """Obtiene un tipo de recurso por su ID"""
        return next((r for r in self.resources if r.id == resource_id), None)

    def get_tech(self, tech_id: str) -> Technologies | None:
        """Obtiene un tipo de tecnología por su ID"""
        return next((t for t in self.techs if t.id == tech_id), None)

    def get_terrain(self, terrain_id: str) -> Terrain | None:
        """Obtiene un tipo de terreno por su ID"""
        return next((t for t in self.terrains if t.id == terrain_id), None)

    def get_army_unit_type(self, army_id: int) -> UnitType | None:
        """Obtiene un tipo de ejército por su ID"""
        return self.unit_types.get(army_id)

    def get_government(self, government_id: str) -> Government | None:
        """Obtiene un tipo de gobierno por su ID"""
        return next((g for g in self.governments if g.id == government_id), None)

    def get_modifier(self, modifier_id: str) -> Modifier | None:
        """Obtiene un modificador por su ID"""
        return next((m for m in self.modifiers if m.id == modifier_id), None)

    def get_casus_belli_type(self, cb_id: str) -> dict[str, str] | None:
        """Obtiene un tipo de casus belli por su ID"""
        return next((cb for cb in self.casus_belli_types if cb["id"] == cb_id), None)

    def get_building(self, building_id: str) -> Building | None:
        """Obtiene un tipo de edificio por su ID"""
        return next((b for b in self.buildings if b.id == building_id), None)

    def get_factory_type(self, factory_type_id: str) -> FactoryType | None:
        """Obtiene un tipo de fábrica por su ID"""
        return next((f for f in self.factory_types if f.id == factory_type_id), None)

    def get_template_id(self) -> str | None:
        """Obtiene el ID de plantilla base, si existe"""
        return self.template_id