from dataclasses import dataclass, asdict
from typing import Optional
@dataclass
class Resource:
    id: str
    name: str
    icon: Optional[str] = None
    is_natural: bool
    base_price: float
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Resource':
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            is_natural=data.get("is_natural", data.get("type") == "natural"),
            base_price=data.get("base_price", 100.0),
            icon=data.get("icon", data.get("image")),
            description=data.get("description", "")
        )
