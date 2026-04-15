from dataclasses import dataclass, field
from model.scenario.province import Province
from model.scenario.stockpile import Stockpile

@dataclass
class ProvinceState(Province):
    """Estado MUTABLE de una provincia durante gameplay.
    
    Hereda de Scenario/Province y agrega tracking de economía e infraestructura.
    """
    factories: list[str] = field(default_factory=list)  # IDs de factories en esta provincia
    rgo_workers: int = 0  # Workers asignados a RGO (recurso natural)
    building_levels: dict[str, int] = field(default_factory=dict)  # building_id -> nivel

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict["factories"] = list(self.factories)
        base_dict["rgo_workers"] = self.rgo_workers
        base_dict["building_levels"] = dict(self.building_levels)
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> 'ProvinceState':
        return cls(
            province_id=data.get("province_id") or data.get("id", 0),
            owner=data.get("owner"),
            population=data.get("population", 0),
            fort_level=data.get("fort_level", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {})),
            factories=data.get("factories", []),
            rgo_workers=data.get("rgo_workers", 0),
            building_levels=data.get("building_levels", {}),
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
