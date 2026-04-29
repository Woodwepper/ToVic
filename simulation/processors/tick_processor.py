from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.entities.state.game_state import GameState

# Morale/org recovered per tick when not in combat
_MORALE_RECOVERY = 0.005
_ORG_RECOVERY    = 0.005


class TickProcessor:
    """Avanza la fecha del juego y aplica recuperación pasiva por tick.

    Responsabilidades (Opción B — el día ABRE aquí):
      1. Avanzar tick + fecha en GameState.
      2. Expirar Casus Belli cuyo expiration_tick <= current_tick.
      3. Recuperación pasiva de moral y organización de ejércitos.
    """

    def process(self, game_state: GameState) -> list[dict]:
        events: list[dict] = []

        # 1. Avanzar tick y fecha
        game_state.advance_tick()
        tick_event = {"type": "TICK_ADVANCED", "tick": game_state.current_tick, "date": game_state.get_date()}
        game_state.log_event("TICK_ADVANCED", {"tick": game_state.current_tick, "date": game_state.get_date()})
        events.append(tick_event)

        # 2. Expirar CBs
        for cb in game_state.casus_belli_active:
            if cb.active and cb.is_expired(game_state.current_tick):
                cb.expire()
                cb_event = {"type": "CB_EXPIRED", "cb_id": cb.id, "country_from": cb.country_from, "country_to": cb.country_to}
                game_state.log_event("CB_EXPIRED", {"cb_id": cb.id, "country_from": cb.country_from, "country_to": cb.country_to})
                events.append(cb_event)

        # 3. Recuperación pasiva de ejércitos
        for army in game_state.armies:
            if army.morale < 1.0:
                army.restore_morale(_MORALE_RECOVERY)
            if army.organization < 1.0:
                army.restore_organization(_ORG_RECOVERY)

        return events
