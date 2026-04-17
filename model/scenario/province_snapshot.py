from dataclasses import dataclass, field
from typing import Optional
from model.scenario.stockpile import Stockpile

@dataclass
class ProvinceSnapshot:
    """Snapshot inicial de una provincia en el scenario.
    
    Contiene el estado inicial de una provincia (owner, population, forts)
    en el momento del start del juego.
    """
    id: str
    name: str
    owner_tag: Optional[str] = "neutral"  # Country tag
    population: int = 0
    fort_level: int = 0
    stockpile: Stockpile = field(default_factory=Stockpile)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "owner_tag": self.owner_tag,
            "population": self.population,
            "fort_level": self.fort_level,
            "stockpile": self.stockpile.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProvinceSnapshot':
        return cls(
            id=str(data.get("id") or data.get("province_id", "")),
            name=data.get("name", ""),
            owner_tag=data.get("owner_tag"),
            population=data.get("population", 0),
            fort_level=data.get("fort_level", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {})),
        )

    @property
    def province_id(self) -> str:
        """Alias de compatibilidad para código legacy."""
        return self.id
