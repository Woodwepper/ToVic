from dataclasses import dataclass, field
from model.scenario.building_snapshot import BuildingSnapshot

@dataclass
class BuildingState(BuildingSnapshot):
    """Estado MUTABLE de un edificio durante gameplay.
    
    Hereda de BuildingSnapshot. El dueño se infiere del owner de la provincia.
    """
    active: bool = True  # False si está destruido o en construcción
    construction_progress: int = 0  # 0-100, relevante si active=False

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["active"] = self.active
        base["construction_progress"] = self.construction_progress
        return base

    @classmethod
    def from_dict(cls, data: dict) -> 'BuildingState':
        return cls(
            id=str(data["id"]),
            building_type_id=data["building_type_id"],
            province_id=str(data["province_id"]),
            level=data.get("level", 1),
            active=data.get("active", True),
            construction_progress=data.get("construction_progress", 0),
        )

    def is_constructing(self) -> bool:
        return not self.active and self.construction_progress < 100

    def complete_construction(self) -> None:
        self.active = True
        self.construction_progress = 100