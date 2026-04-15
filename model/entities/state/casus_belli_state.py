from dataclasses import dataclass
from model.world.casus_belli import CasusBelli as WorldCasusBelli


@dataclass
class CasusBelli(WorldCasusBelli):
    """State: instancia mutable de casus belli durante el gameplay
    
    Hereda de World y agrega campos de instancia (country_from/to, ticks, active).
    """
    # Campos de instancia
    country_from: str = ""
    country_to: str = ""
    casus_belli_type: str = ""
    creation_tick: int = 0
    expiration_tick: int = 0
    active: bool = True
    
    def to_dict(self) -> dict:
        base_dict = super().to_dict()
        base_dict.update({
            "country_from": self.country_from,
            "country_to": self.country_to,
            "casus_belli_type": self.casus_belli_type,
            "creation_tick": self.creation_tick,
            "expiration_tick": self.expiration_tick,
            "active": self.active,
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelli':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", data.get("casus_belli_type", "")),  # Usar tipo como nombre si no existe
            description=data.get("description", ""),
            validity_days=data.get("validity_days", 365),
            war_goal=data.get("war_goal", "conquest"),
            requirements=data.get("requirements", {}),
            country_from=data.get("country_from", ""),
            country_to=data.get("country_to", ""),
            casus_belli_type=data.get("casus_belli_type", ""),
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
