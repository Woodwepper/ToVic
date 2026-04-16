from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class BuildingType:
    id: str
    name: str
    category: str
    icon: Optional[str] = None
    description: str = ""
    construction_cost: int = 0
    maintenance_cost: int = 0
    construction_time: int = 0
    modifiers: list[str] = field(default_factory=list)
    required_technology: Optional[str] = None
    requires_port: bool = False
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BuildingType':
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            icon=data.get("icon"),
            description=data.get("description", ""),
            construction_cost=data.get("construction_cost", 0),
            maintenance_cost=data.get("maintenance_cost", 0),
            construction_time=data.get("construction_time", 0),
            modifiers=data.get("modifiers", []),
            required_technology=data.get("required_technology"),
            requires_port=data.get("requires_port", False),
        )