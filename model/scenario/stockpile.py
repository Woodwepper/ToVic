from dataclasses import dataclass, field

@dataclass
class Stockpile:
    resources: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, float]:
        return dict(self.resources)

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> 'Stockpile':
        return cls(resources=dict(data))

    def get_amount(self, resource_id: str) -> float:
        return self.resources.get(resource_id, 0.0)
    
    def add(self, resource_id: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("amount no puede ser negativo")
        self.resources[resource_id] = self.get_amount(resource_id) + amount

    def remove(self, resource_id: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("amount no puede ser negativo")

        current = self.get_amount(resource_id)
        if current < amount:
            raise ValueError(f"No hay suficiente {resource_id}")

        new_amount = current - amount

        if new_amount == 0:
            self.resources.pop(resource_id, None)
        else:
            self.resources[resource_id] = new_amount

    def has_enough(self, resource_id: str, amount: float) -> bool:
        if amount < 0:
            raise ValueError("amount no puede ser negativo")
        return self.get_amount(resource_id) >= amount
    
    def set_amount(self, resource_id: str, amount: float) -> None:
        if amount < 0:
            raise ValueError("amount no puede ser negativo")
        if amount == 0:
            self.resources.pop(resource_id, None)
        else:
            self.resources[resource_id] = amount