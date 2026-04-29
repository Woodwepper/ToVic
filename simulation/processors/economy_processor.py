from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.entities.state.game_state import GameState

# Ticks por día de producción de RGO (1 = produce cada tick)
_RGO_TICKS_PER_CYCLE = 1
# Producción base por worker asignado a RGO
_RGO_OUTPUT_PER_WORKER = 0.1


class EconomyProcessor:
    """Procesa la economía del mundo por tick.

    Orden interno:
      1. RGO: cada provincia con un recurso natural y workers produce recursos
         y los deposita en el stockpile del país dueño.
      2. Factories: cada fábrica activa consume inputs y produce outputs si hay
         suficiente materia prima en el stockpile del país.
    """

    def process(self, game_state: GameState) -> list[dict]:
        events: list[dict] = []
        events.extend(self._process_rgo(game_state))
        events.extend(self._process_factories(game_state))
        return events

    # ------------------------------------------------------------------
    # RGO
    # ------------------------------------------------------------------

    def _process_rgo(self, game_state: GameState) -> list[dict]:
        events: list[dict] = []

        # Índice rápido: world_province_id → world Province (para resource_id)
        world_province_map = {wp.id: wp for wp in game_state.world.provinces}

        for province_state in game_state.provinces:
            if province_state.rgo_workers <= 0:
                continue

            owner_tag = province_state.owner_tag
            if not owner_tag:
                continue

            # Obtener resource_id desde la definición del mundo
            world_province = world_province_map.get(province_state.id)
            if not world_province or not world_province.resource_id:
                continue

            resource_id = world_province.resource_id
            amount = round(province_state.rgo_workers * _RGO_OUTPUT_PER_WORKER, 4)

            country = game_state.get_country_state(owner_tag)
            if not country:
                continue

            country.stockpile.add(resource_id, amount)

            event_data = {
                "province_id": province_state.id,
                "resource_id": resource_id,
                "amount": amount,
                "owner_tag": owner_tag,
            }
            game_state.log_event("RGO_PRODUCED", event_data)
            events.append({"type": "RGO_PRODUCED", **event_data})

        return events

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    def _process_factories(self, game_state: GameState) -> list[dict]:
        events: list[dict] = []

        for factory in game_state.factories:
            if not factory.active:
                continue

            factory_type = game_state.world.factory_types.get(factory.factory_type_id)
            if not factory_type:
                continue

            country = game_state.get_country_state(factory.country_tag)
            if not country:
                continue

            # Verificar inputs disponibles (escalado por nivel)
            scale = factory.level * factory.efficiency
            required = {res: round(qty * scale, 4) for res, qty in factory_type.input_goods.items()}

            if not all(country.stockpile.has_enough(res, qty) for res, qty in required.items()):
                continue

            # Consumir inputs
            for res, qty in required.items():
                country.stockpile.remove(res, qty)

            # Producir outputs
            produced = {}
            for res, qty in factory_type.output_goods.items():
                amount = round(qty * scale, 4)
                country.stockpile.add(res, amount)
                produced[res] = amount

            factory.last_production_tick = game_state.current_tick

            event_data = {
                "factory_id": factory.id,
                "factory_type_id": factory.factory_type_id,
                "country_tag": factory.country_tag,
                "consumed": required,
                "produced": produced,
            }
            game_state.log_event("FACTORY_RAN", event_data)
            events.append({"type": "FACTORY_RAN", **event_data})

        return events
