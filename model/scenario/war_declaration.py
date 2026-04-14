from dataclasses import dataclass, asdict, field

@dataclass
class WarDeclaration:
    """Scenario: instancia inicial de guerra en el snapshot del escenario"""
    id: str
    country_from: str
    country_to: str
    creation_tick: int  # Tick de inicio
    initial_war_goal: str = ""
    history: dict = field(default_factory=dict)  # Histórico de eventos
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WarDeclaration':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            creation_tick=data.get("creation_tick", data.get("creation_date", 0)),
            initial_war_goal=data.get("initial_war_goal", ""),
            history=data.get("history", {}),
        )
