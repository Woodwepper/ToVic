from dataclasses import dataclass, asdict

@dataclass
class CasusBelliSnapshot:
    """Scenario snapshot: contenedor mínimo de datos para casus belli iniciales
    
    Solo almacena datos, sin lógica. La lógica vive en State (casus_belli_state.py).
    casus_belli_type es el ID de referencia a World/CasusBelli (se resuelve en runtime).
    """
    id: str  # ID único de este CB activo
    country_from: str
    country_to: str
    casus_belli_type: str  # Referencia a World/CasusBelli.id
    expiration_tick: int
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CasusBelliSnapshot':
        return cls(
            id=data["id"],
            country_from=data["country_from"],
            country_to=data["country_to"],
            casus_belli_type=data["casus_belli_type"],
            expiration_tick=data.get("expiration_tick", 0),
        )
