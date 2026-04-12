from dataclasses import dataclass, asdict, field

@dataclass
class Province:
    id: int
    name: str
    owner: str | None
    population: int
    buildings: dict[str, int] = field(default_factory=dict)
    colides_with: list[int] = field(default_factory=list)
    terrain: str | None = None
    resource: str | None = None
    fort_level: int = 0

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Province':
        return cls(
            id=data["id"],
            name=data["name"],
            owner=data.get("owner"),
            terrain=data.get("terrain"),
            resource=data.get("resource"),
            population=data.get("population", 0),
            buildings=data.get("buildings", {}),
            fort_level=data.get("fort_level", 0)
        )