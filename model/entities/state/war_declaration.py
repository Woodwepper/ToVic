from dataclasses import dataclass, field
from model.scenario.war_declaration import WarDeclaration as WarDeclarationScenario

@dataclass
class WarDeclaration(WarDeclarationScenario):
    """State: guerra activa con full tracking (hereda de Scenario)
    
    Agrega allies, casualties, ending date y victor tracking.
    """
    country_from_allies: list[str] = field(default_factory=list)  # Aliados del atacante
    country_to_allies: list[str] = field(default_factory=list)  # Aliados del defensor
    ended_tick: int | None = None  # None si sigue activa
    casualties: dict[str, int] = field(default_factory=dict)  # {country_tag: damage}
    victor: str | None = None  # Quién ganó (tag), None si sigue
    
    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict["country_from_allies"] = list(self.country_from_allies)
        base_dict["country_to_allies"] = list(self.country_to_allies)
        base_dict["ended_tick"] = self.ended_tick
        base_dict["casualties"] = dict(self.casualties)
        base_dict["victor"] = self.victor
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WarDeclaration':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            creation_tick=data.get("creation_tick", data.get("creation_date", 0)),
            initial_war_goal=data.get("initial_war_goal", ""),
            history=data.get("history", {}),
            country_from_allies=data.get("country_from_allies", []),
            country_to_allies=data.get("country_to_allies", []),
            ended_tick=data.get("ended_tick"),
            casualties=data.get("casualties", {}),
            victor=data.get("victor"),
        )
    
    def is_active(self) -> bool:
        """Verifica si la guerra sigue activa"""
        return self.ended_tick is None
    
    def end_war(self, victor: str, current_tick: int) -> None:
        """Termina la guerra con un ganador"""
        self.victor = victor
        self.ended_tick = current_tick
    
    def add_casualty(self, country_tag: str, damage: int) -> None:
        """Registra casualties"""
        self.casualties[country_tag] = self.casualties.get(country_tag, 0) + damage
