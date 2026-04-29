from dataclasses import dataclass
from typing import Optional

@dataclass
class BuildingSnapshot:
    """Snapshot inicial de un edificio en el scenario.
    
    El dueño se infiere siempre del owner de la provincia (province_id).
    """
    id: str
    building_type_id: str  # Referencia a World/BuildingType.id
    province_id: str  # Referencia a World/Province.id
    level: int = 1
    factory_type_id: Optional[str] = None

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "building_type_id": self.building_type_id,
            "province_id": self.province_id,
            "level": self.level,
        }
        if self.factory_type_id:
            data["factory_type_id"] = self.factory_type_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildingSnapshot':
        return cls(
            id=str(data["id"]),
            building_type_id=data["building_type_id"],
            province_id=str(data["province_id"]),
            level=data.get("level", 1),
            factory_type_id=data.get("factory_type_id"),
        )
