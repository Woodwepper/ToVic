from dataclasses import dataclass, asdict
from model.enums.tech_branch import TechBranch

@dataclass
class Technology:
    id: str
    display_name: str
    branch: TechBranch
    required_points: int
    effects: dict[str, float]
    activation_year: int
    requirements: str | None = None
    image: str | None = None
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Technology':
        return cls(
            id=data["id"],
            display_name=data.get("display_name", data.get("name", "")),
            branch=TechBranch(data["branch"]),
            required_points=data["required_points"],
            effects=data.get("effects", {}),
            activation_year=data["activation_year"],
            requirements=data.get("requirements"),
            image=data.get("image", data.get("icon")),
            description=data.get("description", "")
        )