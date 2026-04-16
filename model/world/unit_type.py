from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class UnitType:
    id: str
    name: str
    icon: Optional[str] = None
    attack: float
    defense: float
    cost: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UnitType':
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            attack=data["attack"],
            defense=data["defense"],
            cost=data.get("cost", 0.0),
            icon=data.get("icon"),
        )