from dataclasses import dataclass

@dataclass
class BuildingSnapshot:
    """Snapshot inicial de un edificio en el scenario.
    
    El dueño se infiere siempre del owner de la provincia (province_id).
    """
    id: str
    building_type_id: str  # Referencia a World/BuildingType.id
    province_id: str  # Referencia a World/Province.id
    level: int = 1

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "building_type_id": self.building_type_id,
            "province_id": self.province_id,
            "level": self.level,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildingSnapshot':
        return cls(
            id=str(data["id"]),
            building_type_id=data["building_type_id"],
            province_id=str(data["province_id"]),
            level=data.get("level", 1),
        )