from dataclasses import dataclass, field

@dataclass
class Units:
    """Representa las unidades militares en un ejército"""
    units: dict = field(default_factory=dict)

    def to_dict(self):
        return dict(self.units)

    @classmethod
    def from_dict(cls, data):
        return cls(units=dict(data) if data else {})

    def get_amount(self, unit_type: str) -> float:
        return self.units.get(unit_type, 0.0)
    
    def add(self, unit_type: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self.units[unit_type] = self.get_amount(unit_type) + amount

    def remove(self, unit_type: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("La cantidad no puede ser negativa")
        current = self.get_amount(unit_type)
        if current < amount:
            raise ValueError(f"No hay suficientes {unit_type}")
        new_amount = current - amount
        if new_amount == 0:
            self.units.pop(unit_type, None)
        else:
            self.units[unit_type] = new_amount

    def has_enough(self, unit_type: str, amount: float) -> bool:
        if amount < 0:
            raise ValueError("La cantidad no puede ser negativa")
        return self.get_amount(unit_type) >= amount
    
    def total_strength(self) -> float:
        return sum(self.units.values())
    
    def set_amount(self, unit_type: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("La cantidad no puede ser negativa")
        if amount == 0:
            self.units.pop(unit_type, None)
        else:
            self.units[unit_type] = amount
