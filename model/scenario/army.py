from dataclasses import dataclass, field
from typing import Optional
from model.common.units import Units

@dataclass
class Army:
    """Snapshot inicial de un ejército en el scenario.
    
    Contiene la composición y estado inicial del ejército al empezar el juego.
    """
    id: str
    owner_tag: str
    name: str
    general_id: Optional[str] = None  # Referencia a General por ID
    units: Units = field(default_factory=Units)  # {unit_type -> cantidad}
    province_id: Optional[str] = None
    morale: float = 1.0
    organization: float = 1.0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "owner_tag": self.owner_tag,
            "name": self.name,
            "general_id": self.general_id,
            "units": self.units.to_dict(),
            "province_id": self.province_id,
            "morale": self.morale,
            "organization": self.organization,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Army':
        return cls(
            id=str(data.get("id") or data.get("army_id", "")),
            owner_tag=data.get("owner_tag", ""),
            name=data.get("name", ""),
            general_id=data.get("general_id") or data.get("general"),
            units=Units.from_dict(data.get("units", {})),
            province_id=data.get("province_id"),
            morale=data.get("morale", 1.0),
            organization=data.get("organization", 1.0),
        )