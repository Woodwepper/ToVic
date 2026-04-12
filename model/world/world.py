from dataclasses import dataclass, field, asdict
from model.world.province import Province
from model.world.technology import Technologies
from model.world.resource import Resource
from model.world.terrain import Terrain
from model.world.unit_type import UnitType

@dataclass
class World:
    id: str
    name: str
    provinces: list[Province] = field(default_factory=Province)
    resources: list[Resource] = field(default_factory=Resource)
    techs: list[Technologies] = field(default_factory=Technologies)
    terrains: list[Terrain] = field(default_factory=Terrain)
    unit_types: dict[str, UnitType] = field(default_factory=dict)  # ej {"infantry": {"attack": 1.0, "defense": 1.0}}
    template_id: str | None = None

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
            template_id=data.get("template_id"),
        )
    def get_province(self, province_id: int) -> Province | None:
        """Obtiene una provincia por su ID"""
        for province in self.provinces:
            if province.id == province_id:
                return province
        return None

    def get_army_unit_type(self, army_id: int) -> UnitType | None:
        """Obtiene un tipo de ejército por su ID"""
        return self.unit_types.get(army_id)
    
    def get_terrain(self, terrain_id: str) -> Terrain | None:
        """Obtiene un tipo de terreno por su ID"""
        return next((t for t in self.terrains if t.id == terrain_id), None)
    
    def get_resource(self, resource_id: str) -> Resource | None:
        """Obtiene un tipo de recurso por su ID"""
        return next((r for r in self.resources if r.id == resource_id), None)
    
    def get_tech(self, tech_id: str) -> Technologies | None:
        """Obtiene un tipo de tecnología por su ID"""
        return next((t for t in self.techs if t.id == tech_id), None)
