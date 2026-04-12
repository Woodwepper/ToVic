from dataclasses import dataclass, asdict, field
from model.scenario.general import General
from model.entities.state.units import Units
@dataclass
class Army:
    id: int
    owner_tag: str
    name: str
    general: General | None = None
    units: Units = field(default_factory=Units)
    unit_type: str = "infantry"  # ej "infantry", "cavalry", "artillery"
    province_id: int | None = None
    attack: float = 0.0
    defense: float = 0.0
    morale: float = 1.0
    organization: float = 1.0
    

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "owner_tag": self.owner_tag,
            "name": self.name,
            "general": self.general.to_dict() if self.general else None,
            "units": self.units.to_dict(),
            "unit_type": self.unit_type,
            "province_id": self.province_id,
            "attack": self.attack,
            "defense": self.defense,
            "morale": self.morale,
            "organization": self.organization
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Army':
        return cls(
            id=data["id"],
            owner_tag=data["owner_tag"],
            name=data["name"],
            general=General.from_dict(data["general"]) if data.get("general") else None,
            units=Units.from_dict(data.get("units", {})),
            unit_type=data.get("unit_type", "infantry"),
            province_id=data.get("province_id"),
            attack=data.get("attack", 0.0),
            defense=data.get("defense", 0.0),
            morale=data.get("morale", 1.0),
            organization=data.get("organization", 1.0)
        )