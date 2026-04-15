from dataclasses import dataclass, asdict

@dataclass
class CasusBelli:
    """Scenario snapshot: contenedor mínimo de datos para casus belli iniciales
    
    Solo almacena datos, sin lógica. La lógica vive en State (casus_belli_state.py).
    """
    id: str  # ID único de este CB activo
    country_from: str
    country_to: str
    casus_belli_type: str  # Referencia a World/CasusBelli.id
    creation_tick: int
    expiration_tick: int
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelli':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            casus_belli_type=data["casus_belli_type"],
            creation_tick=data.get("creation_tick", 0),
            expiration_tick=data.get("expiration_tick", 0),
        )
