from dataclasses import dataclass, asdict, field

@dataclass
class WarDeclaration:
    """State: guerra activa con histórico de participantes"""
    id: str
    country_from: str  # Lado atacante
    country_to: str  # Lado defensor
    country_from_allies: list[str] = field(default_factory=list)  # Aliados del atacante
    country_to_allies: list[str] = field(default_factory=list)  # Aliados del defensor
    creation_tick: int = 0
    ended_tick: int | None = None  # None si sigue activa
    casualties: dict[str, int] = field(default_factory=dict)  # {country_tag: damage}
    victor: str | None = None  # Quién ganó (tag), None si sigue
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WarDeclaration':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            country_from_allies=data.get("country_from_allies", []),
            country_to_allies=data.get("country_to_allies", []),
            creation_tick=data.get("creation_tick", 0),
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
