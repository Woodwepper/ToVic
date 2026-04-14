from dataclasses import dataclass, field
from typing import Optional
from model.scenario.stockpile import Stockpile


@dataclass
class Province:
    """Snapshot inicial de una provincia en el scenario.
    
    Contiene el estado inicial de una provincia (owner, population, forts)
    en el momento del start del juego.
    """
    province_id: int
    owner: Optional[str] = None  # Country tag
    population: int = 0
    fort_level: int = 0
    stockpile: Stockpile = field(default_factory=Stockpile)

    def to_dict(self) -> dict:
        return {
            "province_id": self.province_id,
            "owner": self.owner,
            "population": self.population,
            "fort_level": self.fort_level,
            "stockpile": self.stockpile.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Province':
        return cls(
            province_id=data.get("province_id") or data.get("id", 0),
            owner=data.get("owner"),
            population=data.get("population", 0),
            fort_level=data.get("fort_level", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {})),
        )
