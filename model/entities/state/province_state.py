from dataclasses import dataclass, field
from model.scenario.stockpile import Stockpile

@dataclass
class ProvinceState:
    province_id: int
    owner: str | None = None
    population: int = 0
    fort_level: int = 0
    stockpile: Stockpile = field(default_factory=Stockpile)

    def to_dict(self) -> dict:
        return {
            "province_id": self.province_id,
            "owner": self.owner,
            "population": self.population,
            "fort_level": self.fort_level,
            "stockpile": self.stockpile.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProvinceState':
        return cls(
            province_id=data.get("province_id") or data.get("id", 0),
            owner=data.get("owner"),
            population=data.get("population", 0),
            fort_level=data.get("fort_level", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {}))
        )

    def change_owner(self, new_owner: str | None) -> None:
        """Cambia el dueño de la provincia"""
        self.owner = new_owner

    def add_population(self, amount: int) -> None:
        """Agrega población a la provincia"""
        if amount < 0:
            raise ValueError("La población no puede ser negativa")
        self.population += amount

    def remove_population(self, amount: int) -> bool:
        """Remueve población de la provincia si hay suficiente"""
        if amount < 0:
            raise ValueError("La población no puede ser negativa")
        if self.population >= amount:
            self.population -= amount
            return True
        return False

    def upgrade_fort(self) -> bool:
        """Mejora el nivel de fortificación (máximo 10)"""
        if self.fort_level < 10:
            self.fort_level += 1
            return True
        return False

    def downgrade_fort(self) -> bool:
        """Reduce el nivel de fortificación (mínimo 0)"""
        if self.fort_level > 0:
            self.fort_level -= 1
            return True
        return False

    def get_defense_bonus(self) -> float:
        """Retorna el bonificador de defensa basado en las fortificaciones"""
        return self.fort_level * 0.1  # 0-10% de bonificación
