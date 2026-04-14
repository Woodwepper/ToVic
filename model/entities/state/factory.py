from dataclasses import asdict, dataclass

@dataclass
class Factory:
    """State: instancia de fábrica en una provincia, con su estado actual"""
    id: str
    factory_type_id: str
    country_tag: str
    province_id: int
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
from dataclasses import asdict, dataclass

@dataclass
class Factory:
    """State: instancia de fábrica en una provincia, con su estado actual"""
    id: str
    factory_type_id: str
    country_tag: str
    province_id: int
    level: int = 1
    active: bool = True  # False si está en construcción
    construction_progress: int = 0  # 0-100, solo relevante si active=False
    current_workers: int = 0
    efficiency: float = 1.0  # 0.0-1.0, afecta producción
    last_production_time: int = 0

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
            last_production_time=data.get("last_production_time", 0),
        )

    def increment_level(self):
        self.level += 1
        self.production_capacity = int(self.production_capacity * 1.5) # Incrementa la capacidad de producción al subir de nivel
        self.maintenance_cost = int(self.maintenance_cost * 1.5) # Incrementa el costo de mantenimiento al subir de nivel
        self.needed_workers = int(self.needed_workers * 1.5) # Aumenta la cantidad de trabajadores necesarios al subir de nivel
        self.efficiency *= 1.1 # Incrementa la eficiencia en un 10% al subir de nivel
    
    def decrement_level(self):
        if self.level > 1:
            self.level -= 1
            self.production_capacity = int(self.production_capacity / 1.5) # Decrementa la capacidad de producción al bajar de nivel
            self.maintenance_cost = int(self.maintenance_cost / 1.5) # Decrementa el costo de mantenimiento al bajar de nivel
            self.needed_workers = int(self.needed_workers / 1.5) # Disminuye la cantidad de trabajadores necesarios al bajar de nivel
            self.efficiency /= 1.1 # Decrementa la eficiencia en un 10% al bajar de nivel

    def produce(self) -> dict:
        """Realiza la producción de la fábrica, consumiendo los bienes de entrada y generando los bienes de salida"""
        if not self.active:
            return
        
        # Verificar si hay suficientes bienes de entrada
        for good, amount in self.input_goods.items():
            if self.get_good_amount(good) < amount:
                return  # No hay suficientes bienes de entrada, no se produce
        
        # Consumir los bienes de entrada
        for good, amount in self.input_goods.items():
            self.consume_good(good, amount)
        
        # Generar los bienes de salida
        for good, amount in self.output_goods.items():
            self.produce_good(good, int(amount * self.efficiency))
    
    def get_good_amount(self, good: str) -> int:
        """Obtiene la cantidad actual de un bien específico en la fábrica"""
        return self.input_goods.get(good, 0)
    
    def consume_good(self, good: str, amount: int):
        """Consume una cantidad específica de un bien en la fábrica"""
        if good in self.input_goods:
            self.input_goods[good] = max(0, self.input_goods[good] - amount)
        
    def produce_good(self, good: str, amount: int):
        """Genera una cantidad específica de un bien en la fábrica"""
        if good in self.output_goods:
            self.output_goods[good] += amount
        else:
            self.output_goods[good] = amount

    def add_workers(self, amount: int):
        """Agrega trabajadores a la fábrica, hasta el máximo permitido por la capacidad de producción"""
        self.current_workers = min(self.needed_workers, self.current_workers + amount)

    def remove_workers(self, amount: int):
        """Elimina trabajadores de la fábrica, sin permitir que el número de trabajadores sea negativo"""
        self.current_workers = max(0, self.current_workers - amount)
    
    def is_construction_complete(self) -> bool:
        """Verifica si la construcción de la fábrica está completa"""
        return self.construction_progress >= 100