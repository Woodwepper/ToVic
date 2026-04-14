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
    latitude: float = 0.0  # Para visualización en mapa
    longitude: float = 0.0  # Para visualización en mapa
    base_buildings: dict[str, bool] = field(default_factory=dict)  # Qué buildings PUEDEN estar (building_id -> puede_estar)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "terrain_id": self.terrain_id,
            "resource_id": self.resource_id,
            "adjacent_provinces": list(self.adjacent_provinces),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "base_buildings": dict(self.base_buildings),
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Province':
        return cls(
            id=data["id"],
            name=data["name"],
            terrain_id=data["terrain_id"],
            resource_id=data.get("resource_id"),
            adjacent_provinces=data.get("adjacent_provinces", []),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            base_buildings=data.get("base_buildings", {}),
        )