from dataclasses import dataclass, field
from typing import Optional
from model.scenario.country import Country
from model.scenario.stockpile import Stockpile

@dataclass
class CountryState(Country):
    """Estado MUTABLE de un país durante gameplay.
    
    Hereda de Scenario/Country y agrega tracking de workers para economía.
    """
    workers_pool: int = 0  # Workers disponibles para RGO/factories

    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict["workers_pool"] = self.workers_pool
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> 'CountryState':
        return cls(
            tag=data.get("tag", ""),
            name=data.get("name", ""),
            capital=data.get("capital", 0),
            population=data.get("population", 0),
            money=data.get("money", 0.0),
            manpower=data.get("manpower", 0),
            stockpile=Stockpile.from_dict(data.get("stockpile", {})),
            researched_techs=data.get("researched_techs", []),
            actual_research=data.get("actual_research"),
            relations=data.get("relations", {}),
            generals=data.get("generals", []),
            armies=data.get("armies", []),
            workers_pool=data.get("workers_pool", 0),
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

    # MANPOWER
    
    def add_manpower(self, amount: int) -> None:
        """Agrega manpower (personal militar)"""
        if amount < 0:
            raise ValueError("El manpower no puede ser negativo")
        self.manpower += amount

    def remove_manpower(self, amount: int) -> bool:
        """Remueve manpower si hay suficiente"""
        if amount < 0:
            raise ValueError("El manpower no puede ser negativo")
        if self.manpower >= amount:
            self.manpower -= amount
            return True
        return False

    # WORKERS (para economía)

    def add_workers(self, amount: int) -> None:
        """Agrega workers al pool disponible"""
        if amount < 0:
            raise ValueError("Los workers no pueden ser negativos")
        self.workers_pool += amount

    def remove_workers(self, amount: int) -> bool:
        """Remueve workers del pool si hay suficientes"""
        if amount < 0:
            raise ValueError("Los workers no pueden ser negativos")
        if self.workers_pool >= amount:
            self.workers_pool -= amount
            return True
        return False

    # TECHNOLOGIES

    def has_tech(self, tech_id: str) -> bool:
        """Verifica si el país ha investigado una tecnología"""
        return tech_id in self.researched_techs

    def research_tech(self, tech_id: str) -> bool:
        """Agrega una tecnología como investigada (si no está ya)"""
        if not self.has_tech(tech_id):
            self.researched_techs.append(tech_id)
            return True
        return False

    def set_research(self, tech_id: Optional[str]) -> None:
        """Establece la tecnología en investigación actual"""
        self.actual_research = tech_id

    def clear_research(self) -> None:
        """Cancela la investigación actual"""
        self.actual_research = None

    def list_researched_techs(self) -> list[str]:
        """Retorna lista de tecnologías investigadas"""
        return list(self.researched_techs)

    # GENERALS

    def add_general(self, general_id: str) -> None:
        """Agrega un general al país (si no está ya)"""
        if general_id not in self.generals:
            self.generals.append(general_id)

    def remove_general(self, general_id: str) -> bool:
        """Remueve un general del país"""
        if general_id in self.generals:
            self.generals.remove(general_id)
            return True
        return False

    def has_general(self, general_id: str) -> bool:
        """Verifica si el país tiene un general específico"""
        return general_id in self.generals

    def list_generals(self) -> list[str]:
        """Retorna lista de generales"""
        return list(self.generals)

    # ARMIES

    def add_army(self, army_id: str) -> None:
        """Agrega un ejército al país (si no está ya)"""
        if army_id not in self.armies:
            self.armies.append(army_id)

    def remove_army(self, army_id: str) -> bool:
        """Remueve un ejército del país"""
        if army_id in self.armies:
            self.armies.remove(army_id)
            return True
        return False

    def has_army(self, army_id: str) -> bool:
        """Verifica si el país posee un ejército específico"""
        return army_id in self.armies

    def list_armies(self) -> list[str]:
        """Retorna lista de ejércitos"""
        return list(self.armies)
