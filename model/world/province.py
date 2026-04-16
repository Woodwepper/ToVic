from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Province:
    """Definición estática de una provincia en el mundo.
    
    Contiene únicamente propiedades que se definen en el editor y no cambian
    durante el gameplay (después que el mundo deja estado DRAFT).
    """
    id: str
    name: str
    terrain_id: str  # Referencia a World/Terrain
    icon: Optional[str] = None
    owner: Optional[str] = "neutral"
    population: int = 0
    fort_level: int = 0
    resource_id: Optional[str] = None  # Referencia a World/Resource
    adjacent_provinces: list[str] = field(default_factory=list)  # IDs de provincias adyacentes
    center: Optional[float] = None  # Latitud y longitud del centro de la provincia (para mapas)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    base_buildings: dict[str, bool] = field(default_factory=dict)  # Qué buildings PUEDEN estar (building_id -> puede_estar)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "owner": self.owner,
            "population": self.population,
            "fort_level": self.fort_level,
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
            icon=data.get("icon"),
            owner=data.get("owner", "neutral"),
            population=data.get("population", 0),
            fort_level=data.get("fort_level", 0),
            resource_id=data.get("resource_id"),
            adjacent_provinces=data.get("adjacent_provinces", []),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            base_buildings=data.get("base_buildings", {}),
        )