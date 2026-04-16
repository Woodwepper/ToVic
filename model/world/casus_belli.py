from dataclasses import dataclass, asdict, field
from typing import Optional

@dataclass
class CasusBelli:
    """World definition: tipo de casus belli (justificación para guerra)"""
    id: str
    name: str
    icon: Optional[str] = None  # Icono representativo del casus belli
    description: str = ""
    validity_days: int = 365  # Cuántos días dura antes de expirar
    war_goal: str = "conquest"  # "conquest", "vassal", "independence", etc.
    requirements: dict[str, object] = field(default_factory=dict)  # Requisitos para validez
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelli':
        return cls(
            id=data["id"],
            name=data["name"],
            icon=data.get("icon", ""),
            description=data.get("description", ""),
            validity_days=data.get("validity_days", 365),
            war_goal=data.get("war_goal", "conquest"),
            requirements=data.get("requirements", {}),
        )
