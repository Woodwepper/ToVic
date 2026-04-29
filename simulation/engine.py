from __future__ import annotations
from typing import TYPE_CHECKING

from simulation.processors.tick_processor import TickProcessor
from simulation.processors.economy_processor import EconomyProcessor
from simulation.processors.order_processor import OrderProcessor
from simulation.orders.order_result import OrderResult

if TYPE_CHECKING:
    from model.entities.state.game_state import GameState


class SimulationEngine:
    """Orquestador central de la simulación.

    Ejecuta los tres sistemas en orden fijo por tick:
      1. TickProcessor   — abre el día (fecha, expiración de CBs, recuperación)
      2. EconomyProcessor — produce recursos (RGO + fábricas)
      3. OrderProcessor  — aplica las órdenes de los clientes al cierre del día

    Uso básico:
        engine = SimulationEngine()
        events, results = engine.tick_forward(game_state)
    """

    def __init__(self):
        self._tick_processor     = TickProcessor()
        self._economy_processor  = EconomyProcessor()
        self._order_processor    = OrderProcessor()

    def tick_forward(self, game_state: GameState) -> tuple[list[dict], list[OrderResult]]:
        """Avanza el juego un tick completo.

        Returns:
            events  — lista de todos los eventos emitidos en el tick
            results — lista de OrderResult (uno por orden procesada)
        """
        events: list[dict] = []

        # 1. Tick: avanza fecha, expira CBs, recupera ejércitos
        events.extend(self._tick_processor.process(game_state))

        # 2. Economía: RGO + fábricas
        events.extend(self._economy_processor.process(game_state))

        # 3. Órdenes de clientes
        results = self._order_processor.process(game_state)
        for result in results:
            events.extend(result.events)

        return events, results

    def run(self, game_state: GameState, ticks: int) -> tuple[list[dict], list[OrderResult]]:
        """Ejecuta N ticks consecutivos. Útil para tests y simulaciones rápidas."""
        all_events:  list[dict]         = []
        all_results: list[OrderResult]  = []

        for _ in range(ticks):
            events, results = self.tick_forward(game_state)
            all_events.extend(events)
            all_results.extend(results)

        return all_events, all_results
