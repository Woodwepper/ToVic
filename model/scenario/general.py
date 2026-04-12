from dataclasses import dataclass, asdict
@dataclass
class General:
    id: int
    name: str
    owner_tag: str
    attack_bonus: int
    defense_bonus: int
    trait: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'General':
        return cls(
            id=data["id"],
            name=data["name"],
            owner_tag=data["owner_tag"],
            attack_bonus=data["attack_bonus"],
            defense_bonus=data["defense_bonus"],
            trait=data.get("trait")
        )