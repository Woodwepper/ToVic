from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OrderType(str, Enum):
    RESEARCH    = "research"      # payload: {"tech_id": str}
    BUILD       = "build"         # payload: {"building_type_id": str, "province_id": str}
    ARMY_MOVE   = "army_move"     # payload: {"army_id": str, "to_province_id": str}
    DIPLOMACY   = "diplomacy"     # payload: {"action": str, "target_tag": str}


@dataclass
class Order:
    """Comando emitido por un cliente (bot o web) para el engine.

    Solo el engine puede ejecutarlo; el cliente nunca muta el GameState
    directamente.
    """
    type: OrderType
    country_tag: str
    payload: dict[str, Any] = field(default_factory=dict)
    submitted_tick: int = 0
