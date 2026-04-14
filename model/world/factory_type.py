from dataclasses import asdict, dataclass, field

@dataclass
class FactoryType:
    id: str
    name: str
    input_goods: dict[str, int] = field(default_factory=dict)
    output_goods: dict[str, int] = field(default_factory=dict)
    needed_workers: int
    production_capacity: int
    maintenance_cost: int

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FactoryType':
        return cls(
            id=data["id"],
            name=data["name"],
            input_goods=data.get("input_goods", {}),
            output_goods=data.get("output_goods", {}),
            needed_workers=data["needed_workers"],
            production_capacity=data["production_capacity"],
            maintenance_cost=data["maintenance_cost"],
        )
