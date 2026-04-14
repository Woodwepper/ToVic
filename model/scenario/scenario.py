from dataclasses import dataclass, field
from typing import Optional, List
from model.scenario.country import Country
from model.scenario.province import Province
from model.scenario.army import Army
from model.scenario.casus_belli import CasusBelli
from model.scenario.war_declaration import WarDeclaration


@dataclass
class Scenario:
    id: str
    name: str
    year: int = 1
    month: int = 1
    day: int = 1
    countries: List[Country] = field(default_factory=list)
    provinces: List[Province] = field(default_factory=list)
    armies: List[Army] = field(default_factory=list)
    casus_belli: List[CasusBelli] = field(default_factory=list)
    wars: List[WarDeclaration] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "description": self.description,
            "countries": [c.to_dict() for c in self.countries],
            "provinces": [p.to_dict() for p in self.provinces],
            "armies": [a.to_dict() for a in self.armies],
            "casus_belli": [cb.to_dict() for cb in self.casus_belli],
            "wars": [w.to_dict() for w in self.wars],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Scenario':
        return cls(
            id=data["id"],
            name=data["name"],
            year=data["year"],
            month=data.get("month", 1),
            day=data.get("day", 1),
            description=data.get("description", ""),
            countries=[Country.from_dict(c) for c in data.get("countries", [])],
            provinces=[Province.from_dict(p) for p in data.get("provinces", [])],
            armies=[Army.from_dict(a) for a in data.get("armies", [])],
            casus_belli=[CasusBelli.from_dict(cb) for cb in data.get("casus_belli", [])],
            wars=[WarDeclaration.from_dict(w) for w in data.get("wars", [])],
        )

    def get_country(self, country_tag: str) -> Optional[Country]:
        """Obtiene el estado de un país"""
        for country in self.countries:
            if country.tag == country_tag:
                return country
        return None

    def get_province(self, province_id: int) -> Optional[Province]:
        """Obtiene el estado de una provincia"""
        for province in self.provinces:
            if province.province_id == province_id:
                return province
        return None

    def get_army(self, army_id: int) -> Optional[Army]:
        """Obtiene el estado de un ejército"""
        for army in self.armies:
            if army.army_id == army_id:
                return army
        return None

    def get_casus_belli(self, cb_id: str) -> Optional[CasusBelli]:
        """Obtiene un casus belli por su ID"""
        for cb in self.casus_belli:
            if cb.id == cb_id:
                return cb
        return None

    def get_war(self, war_id: str) -> Optional[WarDeclaration]:
        """Obtiene una guerra por su ID"""
        for war in self.wars:
            if war.id == war_id:
                return war
        return None

    def has_country(self, country_tag: str) -> bool:
        """Verifica si existe un país"""
        return any(c.tag == country_tag for c in self.countries)

    def has_province(self, province_id: int) -> bool:
        """Verifica si existe una provincia"""
        return any(p.province_id == province_id for p in self.provinces)

    def has_army(self, army_id: int) -> bool:
        """Verifica si existe un ejército"""
        return any(a.army_id == army_id for a in self.armies)

    def has_casus_belli(self, cb_id: str) -> bool:
        """Verifica si existe un CB"""
        return any(cb.id == cb_id for cb in self.casus_belli)

    def has_war(self, war_id: str) -> bool:
        """Verifica si existe una guerra"""
        return any(w.id == war_id for w in self.wars)

    def list_casus_belli(self) -> List[CasusBelli]:
        """Retorna lista de CBs"""
        return self.casus_belli

    def list_wars(self) -> List[WarDeclaration]:
        """Retorna lista de guerras"""
        return self.wars

    def advance_year(self) -> None:
        """Avanza un año"""
        self.year += 1

    def advance_month(self) -> None:
        """Avanza un mes"""
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.advance_year()

    def advance_day(self) -> None:
        """Avanza un día"""
        self.day += 1
        if self.day > 30:
            self.day = 1
            self.advance_month()

    def get_date(self) -> str:
        """Retorna fecha en formato Year-Month-Day"""
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

    def get_info(self) -> str:
        """Retorna info del escenario"""
        return f"{self.name} ({self.get_date()}) - {len(self.country_states)} países, {len(self.province_states)} provincias, {len(self.armies)} ejércitos"