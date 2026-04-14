from dataclasses import dataclass, field
from typing import Optional
from model.scenario.army import Army
from model.entities.state.units import Units

@dataclass
class ArmyState(Army):
    """Estado MUTABLE de un ejército durante gameplay.
    
    Hereda de Scenario/Army y agrega tracking de experiencia y cambios de estado.
    """
    experience: float = 0.0  # Experiencia acumulada en combate
    # attack_bonus y defense_bonus se calculan del general (si existe)

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict["experience"] = self.experience
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ArmyState':
        return cls(
            army_id=data.get("army_id") or data.get("id", 0),
            owner_tag=data.get("owner_tag", ""),
            name=data.get("name", ""),
            general_id=data.get("general_id") or data.get("general"),
            units=Units.from_dict(data.get("units", {})),
            province_id=data.get("province_id"),
            morale=data.get("morale", 1.0),
            organization=data.get("organization", 1.0),
            experience=data.get("experience", 0.0),
        )

    # MORALE

    def damage_morale(self, amount: float) -> None:
        """Reduce la moral del ejército"""
        if amount < 0:
            raise ValueError("El daño no puede ser negativo")
        self.morale = max(0.0, self.morale - amount)

    def restore_morale(self, amount: float) -> None:
        """Restaura la moral del ejército"""
        if amount < 0:
            raise ValueError("La restauración no puede ser negativa")
        self.morale = min(1.0, self.morale + amount)

    # ORGANIZATION

    def damage_organization(self, amount: float) -> None:
        """Reduce la organización del ejército"""
        if amount < 0:
            raise ValueError("El daño no puede ser negativo")
        self.organization = max(0.0, self.organization - amount)

    def restore_organization(self, amount: float) -> None:
        """Restaura la organización del ejército"""
        if amount < 0:
            raise ValueError("La restauración no puede ser negativa")
        self.organization = min(1.0, self.organization + amount)

    # EXPERIENCE

    def add_experience(self, amount: float) -> None:
        """Agrega experiencia al ejército"""
        if amount < 0:
            raise ValueError("La experiencia no puede ser negativa")
        self.experience += amount

    # MOVEMENT

    def move_to(self, province_id: int) -> None:
        """Mueve el ejército a una nueva provincia"""
        self.province_id = province_id

    # UNITS

    def add_units(self, unit_type: str, amount: float) -> None:
        """Agrega unidades de un tipo específico"""
        self.units.add(unit_type, amount)

    def remove_units(self, unit_type: str, amount: float) -> bool:
        """Remueve unidades si hay suficientes"""
        try:
            self.units.remove(unit_type, amount)
            return True
        except ValueError:
            return False

    def get_unit_count(self, unit_type: str) -> float:
        """Obtiene cantidad de unidades de un tipo"""
        return self.units.get_amount(unit_type)

    def total_units(self) -> float:
        """Obtiene cantidad total de unidades"""
        return sum(self.units.units.values())

    # STRENGTH CALCULATION (basado en units + morale + organization)

    def get_strength(self) -> float:
        """Calcula la fuerza general del ejército
        
        Básico: total_units * morale * organization
        (Luego se le suman bonificadores del general)
        """
        return self.total_units() * self.morale * self.organization
