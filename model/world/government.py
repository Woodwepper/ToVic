from dataclasses import dataclass, asdict, field
from typing import Optional

@dataclass
class Government:
    """World definition: tipo de gobierno con efectos políticos/económicos"""
    id: str
    name: str
    icon: Optional[str] = None
    description: str = ""
    production_efficiency: float = 1.0  # Multiplicador de producción
    tax_efficiency: float = 1.0  # Multiplicador de recaudación
    military_morale_bonus: float = 0.0  # Bonificador de moral militar
    modifiers: list[str] = field(default_factory=list)  # IDs de modificadores aplicables
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Government':
        return cls(
            id=data["id"],
            name=data["name"],
            icon=data.get("icon", None),
            description=data.get("description", ""),
            production_efficiency=data.get("production_efficiency", 1.0),
            tax_efficiency=data.get("tax_efficiency", 1.0),
            military_morale_bonus=data.get("military_morale_bonus", 0.0),
            modifiers=data.get("modifiers", []),
        )
