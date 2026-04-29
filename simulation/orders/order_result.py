from dataclasses import dataclass
from typing import Optional
from simulation.orders.order import Order


@dataclass
class OrderResult:
    """Resultado de procesar una Order.

    El engine rellena este objeto después de validar y (si aplica) ejecutar
    la orden. El API lo devuelve al cliente como respuesta.
    """
    order: Order
    accepted: bool
    reason: Optional[str] = None   # Motivo de rechazo si accepted=False
    events: list[dict] = None      # Eventos emitidos si accepted=True

    def __post_init__(self):
        if self.events is None:
            self.events = []
