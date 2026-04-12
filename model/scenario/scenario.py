from dataclasses import dataclass, field
from typing import Optional, List
from model.entities.state.army import Army
from model.entities.state.country_state import CountryState
from model.entities.state.province_state import ProvinceState


@dataclass
class Scenario:
    id: str
    name: str
    year: int = 1
    month: int = 1
    day: int = 1
    country_states: List[CountryState] = field(default_factory=list)
    province_states: List[ProvinceState] = field(default_factory=list)
    armies: List[Army] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "description": self.description,
            "country_states": [s.to_dict() for s in self.country_states],
            "province_states": [s.to_dict() for s in self.province_states],
            "armies": [a.to_dict() for a in self.armies]
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
            country_states=[CountryState.from_dict(c) for c in data.get("country_states", [])],
            province_states=[ProvinceState.from_dict(p) for p in data.get("province_states", [])],
            armies=[Army.from_dict(a) for a in data.get("armies", [])]
        )

    def get_country(self, country_tag: str) -> Optional[CountryState]:
        """Obtiene el estado de un país"""
        for country in self.country_states:
            if country.tag == country_tag:
                return country
        return None

    def get_province(self, province_id: int) -> ProvinceState | None:
        """Obtiene el estado de una provincia"""
        for province in self.province_states:
            if province.province_id == province_id:
                return province
        return None

    def get_army(self, army_id: int) -> Army | None:
        """Obtiene el estado de un ejército"""
        for army in self.armies:
            if army.army_id == army_id:
                return army
        return None

    def advance_year(self) -> None:
        """Avanza un año en el escenario"""
        self.year += 1

    def get_info(self) -> str:
        """Retorna información del escenario"""
        country_count = len(self.country_states)
        province_count = len(self.province_states)
        army_count = len(self.armies)
        return f"{self.name} ({self.year}) - {country_count} países, {province_count} provincias, {army_count} ejércitos"
