from dataclasses import dataclass, asdict

@dataclass
class CasusBelli:
    """Scenario: instancia inicial de casus belli en el snapshot del escenario"""
    id: str
    country_from: str  # Quién tiene el CB
    country_to: str  # Contra quién
    casus_belli_type: str  # Referencia a World CasusBelli.id
    creation_date: int  # Tick de creación
    expiration_date: int  # Tick de expiración
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelli':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            casus_belli_type=data["casus_belli_type"],
            creation_date=data.get("creation_date", 0),
            expiration_date=data.get("expiration_date", 0),
        )
