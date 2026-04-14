from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Province:
    """Definición estática de una provincia en el mundo.
    
    Contiene únicamente propiedades que se definen en el editor y no cambian
    durante el gameplay (después que el mundo deja estado DRAFT).
    """
    id: int
    name: str
    terrain_id: str  # Referencia a World/Terrain
    resource_id: Optional[str] = None  # Referencia a World/Resource
    adjacent_provinces: list[int] = field(default_factory=list)  # IDs de provincias adyacentes
    # TODO: coordinates (lat, lng o polygon para mapa visual)
    # TODO: base_buildings (dict[building_id, bool] - qué buildings PUEDEN estar)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "terrain_id": self.terrain_id,
            "resource_id": self.resource_id,
            "adjacent_provinces": list(self.adjacent_provinces),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Province':
        return cls(
            id=data["id"],
            name=data["name"],
            terrain_id=data["terrain_id"],
            resource_id=data.get("resource_id"),
            adjacent_provinces=data.get("adjacent_provinces", []),
        )