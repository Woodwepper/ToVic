from dataclasses import dataclass, asdict, field

@dataclass
class Modifier:
    """World definition: bonificador/penalizador aplicable a países o provincias"""
    id: str
    name: str
    description: str = ""
    scope: str = "country"  # "country" o "province"
    effects: dict[str, float] = field(default_factory=dict)  # {production: 0.1, tax: -0.05}
    duration: int | None = None  # Ticks, None = permanente
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Modifier':
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            scope=data.get("scope", "country"),
            effects=data.get("effects", {}),
            duration=data.get("duration"),
        )
