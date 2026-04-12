from dataclasses import dataclass, asdict

@dataclass
class Resource:
    id: str
    display_name: str
    is_natural: bool
    base_price: float
    icon: str | None = None
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Resource':
        return cls(
            id=data["id"],
            display_name=data.get("display_name", data.get("name", "")),
            is_natural=data.get("is_natural", data.get("type") == "natural"),
            base_price=data.get("base_price", 100.0),
            icon=data.get("icon", data.get("image")),
            description=data.get("description", "")
        )
