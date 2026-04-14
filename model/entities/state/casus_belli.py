from dataclasses import dataclass, asdict

@dataclass
class CasusBelli:
    """State: instancia activa de casus belli entre dos países"""
    id: str
    country_from: str
    country_to: str
    casus_belli_type: str  # Referencia a World CasusBelli.id
    creation_tick: int
    expiration_tick: int
    active: bool = True
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelli':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            casus_belli_type=data["casus_belli_type"],
            creation_tick=data["creation_tick"],
            expiration_tick=data["expiration_tick"],
            active=data.get("active", True),
        )
    
    def is_expired(self, current_tick: int) -> bool:
        """Verifica si el CB ha expirado"""
        return current_tick >= self.expiration_tick
    
    def expire(self) -> None:
        """Marca el CB como inactivo"""
        self.active = False
