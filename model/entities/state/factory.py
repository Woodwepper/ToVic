from dataclasses import asdict, dataclass

@dataclass
class Factory:
    """State: instancia de fábrica en una provincia, con su estado actual"""
    id: str
    factory_type_id: str
    country_tag: str
    province_id: str
    level: int = 1
    active: bool = True  # False si está en construcción
    construction_progress: int = 0  # 0-100, solo relevante si active=False
    current_workers: int = 0
    efficiency: float = 1.0  # 0.0-1.0, afecta producción
    last_production_tick: int = 0

    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Factory':
        return cls(
            id=data["id"],
            factory_type_id=data["factory_type_id"],
            country_tag=data["country_tag"],
            province_id=data["province_id"],
            level=data.get("level", 1),
            active=data.get("active", True),
            construction_progress=data.get("construction_progress", 0),
            current_workers=data.get("current_workers", 0),
            efficiency=data.get("efficiency", 1.0),
            last_production_tick=data.get("last_production_tick", 0),
        )
    
    def is_constructing(self) -> bool:
        """Retorna True si está en construcción"""
        return not self.active and self.construction_progress < 100
    
    def increment_level(self) -> None:
        """Aumenta un nivel (upgrade)"""
        self.level += 1
        self.efficiency = min(self.efficiency * 1.1, 1.0)  # Bonus de 10% en eficiencia, máximo 1.0
    
    def decrement_level(self) -> None:
        """Reduce un nivel (por pérdida en guerra)"""
        if self.level > 1:
            self.level -= 1
        else:
            self.active = False  # Si nivel llega a 0, cierra
    
    def add_workers(self, amount: int) -> None:
        """Agrega trabajadores"""
        self.current_workers += amount
    
    def remove_workers(self, amount: int) -> None:
        """Elimina trabajadores"""
        self.current_workers = max(0, self.current_workers - amount)
