from dataclasses import dataclass, field, asdict
from model.scenario.stockpile import Stockpile

@dataclass
class Country:
    tag: str
    name: str
    capital: int
    population: int
    money: float = 0.0
    manpower: int = 0
    stockpile: Stockpile = field(default_factory=Stockpile)
    researched_techs: list[str] = field(default_factory=list)
    actual_research: str | None = None
    relations: dict[str, int] = field(default_factory=dict)
    generals: list[str] = field(default_factory=list)
    armies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "tag": self.tag,
            "name": self.name,
            "capital": self.capital,
            "population": self.population,
            "money": self.money,
            "manpower": self.manpower,
            "stockpile": self.stockpile.to_dict(),
            "researched_techs": list(self.researched_techs),
            "actual_research": self.actual_research,
            "relations": dict(self.relations),
            "generals": list(self.generals),
            "armies": list(self.armies),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Country":
        return cls(
            tag=data["tag"],
            name=data["name"],
            capital=data["capital"],
            population=data["population"],
            money=data.get("money", 0.0),
            manpower=data.get("manpower", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {})),
            researched_techs=data.get("researched_techs", []),
            actual_research=data.get("actual_research"),
            relations=data.get("relations", {}),
            generals=data.get("generals", []),
            armies=data.get("armies", []),
        )

    def has_tech(self, tech_id: str) -> bool:
        return tech_id in self.researched_techs

    def add_money(self, amount: float) -> None:
        self.money += amount

    def remove_money(self, amount: float) -> bool:
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def set_relation(self, country_tag: str, value: int) -> None:
        """Establece la relación con otro país, limitada al rango [-200, 200]"""
        if not isinstance(value, int) and not isinstance(value, float):
            raise ValueError("La relación debe ser un número")
        # Limitar al rango [-200, 200]
        clamped_value = max(-200, min(200, int(value)))
        self.relations[country_tag] = clamped_value
    
    def get_relation(self, country_tag: str) -> int:
        """Obtiene la relación con otro país. Retorna 0 si no existe."""
        return self.relations.get(country_tag, 0)
    
    def modify_relation(self, country_tag: str, change: int) -> int:
        """Modifica la relación con un cambio, respetando los límites [-200, 200]"""
        current = self.get_relation(country_tag)
        new_value = current + change
        self.set_relation(country_tag, new_value)
        return self.get_relation(country_tag)