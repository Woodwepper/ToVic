from __future__ import annotations

from typing import TYPE_CHECKING

from simulation.orders.order_result import OrderResult
from simulation.processors.construction_processor import ConstructionProcessor
from simulation.processors.economy_processor import EconomyProcessor
from simulation.processors.labor_allocation_processor import LaborAllocationProcessor
from simulation.processors.order_processor import OrderProcessor
from simulation.processors.tick_processor import TickProcessor

if TYPE_CHECKING:
    from model.entities.state.game_state import GameState


class SimulationEngine:
    """Central orchestrator for one complete simulation tick.

    Fixed tick order:
      1. TickProcessor
      2. ConstructionProcessor
      3. LaborAllocationProcessor
      4. EconomyProcessor
      5. OrderProcessor
    """

    def __init__(self):
        self._tick_processor = TickProcessor()
        self._construction_processor = ConstructionProcessor()
        self._labor_allocation_processor = LaborAllocationProcessor()
        self._economy_processor = EconomyProcessor()
        self._order_processor = OrderProcessor()

    def tick_forward(self, game_state: GameState) -> tuple[list[dict], list[OrderResult]]:
        """Advance the game by one complete tick."""
        events: list[dict] = []

        events.extend(self._tick_processor.process(game_state))
        events.extend(self._construction_processor.process(game_state))
        events.extend(self._labor_allocation_processor.process(game_state))
        events.extend(self._economy_processor.process(game_state))

        results = self._order_processor.process(game_state)
        for result in results:
            events.extend(result.events)

        return events, results

    def run(self, game_state: GameState, ticks: int) -> tuple[list[dict], list[OrderResult]]:
        """Run multiple ticks and aggregate emitted events and order results."""
        all_events: list[dict] = []
        all_results: list[OrderResult] = []

        for _ in range(ticks):
            events, results = self.tick_forward(game_state)
            all_events.extend(events)
            all_results.extend(results)

        return all_events, all_results
