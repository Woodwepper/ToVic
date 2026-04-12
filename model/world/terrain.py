from dataclasses import dataclass, asdict
@dataclass
class Terrain:
    id: str
    display_name: str
    supply_limit: int
    defense_bonus: int
    icon: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Terrain':
        return cls(
            id=data["id"],
            display_name=data.get("display_name", data.get("name", "")),
            supply_limit=data["supply_limit"],
            defense_bonus=data["defense_bonus"],
            icon=data.get("image")
        )
    
