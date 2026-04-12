from dataclasses import dataclass, field, asdict

@dataclass
class UnitType:
    id: str
    display_name: str
    attack: float
    defense: float
    cost: float = 0.0
    icon: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UnitType':
        return cls(
            id=data["id"],
            display_name=data.get("display_name", data.get("name", "")),
            attack=data["attack"],
            defense=data["defense"],
            cost=data.get("cost", 0.0),
            icon=data.get("icon"),
        )