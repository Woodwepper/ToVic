from dataclasses import dataclass, field
from typing import Optional
from .units import Units

@dataclass
class Army:
    army_id: int
    owner_tag: str
    name: str
    general: Optional[str] = None
    units: Units = field(default_factory=Units)
    morale: float = 1.0
    organization: float = 1.0
    province_id: Optional[int] = None
    experience: float = 0.0
    unit_type: Optional[str] = None
    attack: float = 1.0
    defense: float = 1.0

    def to_dict(self) -> dict:
        return {
            "army_id": self.army_id,
            "owner_tag": self.owner_tag,
            "name": self.name,
            "general": self.general,
            "units": self.units.to_dict(),
            "morale": self.morale,
            "organization": self.organization,
            "province_id": self.province_id,
            "experience": self.experience,
            "unit_type": self.unit_type,
            "attack": self.attack,
            "defense": self.defense
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Army':
        return cls(
            army_id=data.get("army_id") or data.get("id", 0),
            owner_tag=data.get("owner_tag", ""),
            name=data.get("name", ""),
            general=data.get("general"),
            units=Units.from_dict(data.get("units", {})),
            morale=data.get("morale", 1.0),
            organization=data.get("organization", 1.0),
            province_id=data.get("province_id"),
            experience=data.get("experience", 0.0),
            unit_type=data.get("unit_type"),
            attack=data.get("attack", 1.0),
            defense=data.get("defense", 1.0)
        )

    def damage_morale(self, amount: float) -> None:
        """Reduce la moral del ejército"""
        if amount < 0:
            raise ValueError("El daño no puede ser negativo")
        self.morale = max(0.0, self.morale - amount)

    def restore_morale(self, amount: float) -> None:
        """Restaura la moral del ejército"""
        if amount < 0:
            raise ValueError("La restauración no puede ser negativa")
        self.morale = min(1.0, self.morale + amount)

    def damage_organization(self, amount: float) -> None:
        """Reduce la organización del ejército"""
        if amount < 0:
            raise ValueError("El daño no puede ser negativo")
        self.organization = max(0.0, self.organization - amount)

    def restore_organization(self, amount: float) -> None:
        """Restaura la organización del ejército"""
        if amount < 0:
            raise ValueError("La restauración no puede ser negativa")
        self.organization = min(1.0, self.organization + amount)

    def add_experience(self, amount: float) -> None:
        """Agrega experiencia al ejército"""
        if amount < 0:
            raise ValueError("La experiencia no puede ser negativa")
        self.experience += amount
