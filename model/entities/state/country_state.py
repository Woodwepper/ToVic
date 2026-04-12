from dataclasses import dataclass, field
from model.scenario.stockpile import Stockpile

@dataclass
class CountryState:
    tag: str
    money: float = 0.0
    population: int = 0
    stockpile: Stockpile = field(default_factory=Stockpile)
    relations: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "country_tag": self.country_tag,
            "money": self.money,
            "population": self.population,
            "stockpile": self.stockpile.to_dict(),
            "relations": dict(self.relations)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CountryState':
        return cls(
            tag=data.get("country_tag") or data.get("tag", ""),
            money=data.get("money", 0.0),
            population=data.get("population", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {})),
            relations=data.get("relations", {})
        )

    def add_money(self, amount: float) -> None:
        """Agrega dinero al país"""
        if amount < 0:
            raise ValueError("El dinero no puede ser negativo")
        self.money += amount

    def remove_money(self, amount: float) -> bool:
        """Remueve dinero del país si hay suficiente"""
        if amount < 0:
            raise ValueError("El dinero no puede ser negativo")
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def set_relation(self, country_tag: str, value: int) -> None:
        """Establece la relación con otro país, limitada al rango [-200, 200]"""
        clamped_value = max(-200, min(200, int(value)))
        self.relations[country_tag] = clamped_value

    def get_relation(self, country_tag: str) -> int:
        """Obtiene la relación con otro país"""
        return self.relations.get(country_tag, 0)

    def modify_relation(self, country_tag: str, change: int) -> int:
        """Modifica la relación con un cambio"""
        current = self.get_relation(country_tag)
        new_value = current + change
        self.set_relation(country_tag, new_value)
        return self.get_relation(country_tag)

    def add_population(self, amount: int) -> None:
        """Agrega población al país"""
        if amount < 0:
            raise ValueError("La población no puede ser negativa")
        self.population += amount

    def remove_population(self, amount: int) -> bool:
        """Remueve población del país si hay suficiente"""
        if amount < 0:
            raise ValueError("La población no puede ser negativa")
        if self.population >= amount:
            self.population -= amount
            return True
        return False
