from dataclasses import dataclass
from model.scenario.casus_belli import CasusBelli as CasusBelliScenario

@dataclass
class CasusBelli(CasusBelliScenario):
    """State: instancia activa de casus belli entre dos países (hereda de Scenario)
    
    Agrega tracking de estado activo y métodos para gestionar expiración.
    """
    active: bool = True
    
    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict["active"] = self.active
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelli':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            casus_belli_type=data["casus_belli_type"],
            creation_tick=data.get("creation_tick", data.get("creation_date", 0)),
            expiration_tick=data.get("expiration_tick", data.get("expiration_date", 0)),
            active=data.get("active", True),
        )
    
    def is_expired(self, current_tick: int) -> bool:
        """Verifica si el CB ha expirado"""
        return current_tick >= self.expiration_tick
    
    def expire(self) -> None:
        """Marca el CB como inactivo"""
        self.active = False
