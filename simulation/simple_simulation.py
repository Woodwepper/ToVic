from model.entities.state.game_state import GameState


class SimpleSimulation:
    def __init__(self, game_state: GameState, max_ticks: int = 1000):
        self.game_state = game_state
        self.running = False
        self.max_ticks = max_ticks

    def run_simulation(self, max_ticks: int = None):
        """Ejecuta la simulación hasta max_ticks o hasta que se detiene manualmente"""
        if max_ticks is None:
            max_ticks = self.max_ticks
        
        while self.running and self.game_state.current_tick < max_ticks:
            self._process_tick()

    def _process_tick(self) -> None:
        """Procesa un tick de simulación"""
        self.game_state.advance_tick()
        print(f"Tick {self.game_state.current_tick}: {self.game_state.get_date()}")

    def start(self) -> None:
        """Inicia la simulación"""
        self.running = True

    def stop(self) -> None:
        """Detiene la simulación"""
        self.running = False

    def get_status(self) -> dict:
        """Retorna el estado actual de la simulación"""
        return {
            "running": self.running,
            "current_tick": self.game_state.current_tick,
            "current_date": self.game_state.get_date(),
            "year": self.game_state.scenario.year,
            "month": self.game_state.scenario.month,
            "day": self.game_state.scenario.day,
            "scenario": self.game_state.scenario.name
        }

    def run_n_ticks(self, n: int) -> None:
        """Ejecuta exactamente n ticks"""
        for _ in range(n):
            if not self.running:
                break
            self._process_tick()
