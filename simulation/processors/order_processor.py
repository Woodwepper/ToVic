from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING

from simulation.orders.order import Order, OrderType
from simulation.orders.order_result import OrderResult
from model.entities.state.factory import Factory

if TYPE_CHECKING:
    from model.entities.state.game_state import GameState


class OrderProcessor:
    """Procesa la cola de órdenes pendientes al cierre de cada tick.

    Para cada Order en game_state.pending_orders:
      1. Valida que el país existe y tiene recursos / condiciones.
      2. Ejecuta la mutación en GameState si es válida.
      3. Produce un OrderResult y emite un evento al log.

    Órdenes soportadas:
      - RESEARCH   : investiga una tecnología
      - BUILD      : construye un edificio en una provincia
      - ARMY_MOVE  : mueve un ejército a una provincia adyacente
      - DIPLOMACY  : modifica relaciones entre países
    """

    def process(self, game_state: GameState) -> list[OrderResult]:
        results: list[OrderResult] = []
        queue: deque[Order] = game_state.pending_orders
        game_state.pending_orders = deque()  # vaciar antes de procesar para evitar re-entradas

        for order in queue:
            if order.type == OrderType.RESEARCH:
                result = self._handle_research(order, game_state)
            elif order.type == OrderType.BUILD:
                result = self._handle_build(order, game_state)
            elif order.type == OrderType.ARMY_MOVE:
                result = self._handle_army_move(order, game_state)
            elif order.type == OrderType.DIPLOMACY:
                result = self._handle_diplomacy(order, game_state)
            else:
                result = OrderResult(order=order, accepted=False, reason=f"OrderType desconocido: {order.type}")

            results.append(result)

        return results

    # ------------------------------------------------------------------
    # RESEARCH
    # ------------------------------------------------------------------

    def _handle_research(self, order: Order, game_state: GameState) -> OrderResult:
        tech_id: str = order.payload.get("tech_id", "")

        country = game_state.get_country_state(order.country_tag)
        if not country:
            return OrderResult(order=order, accepted=False, reason=f"País no encontrado: {order.country_tag}")

        # Buscar tech en definiciones del mundo
        tech = next((t for t in game_state.world.techs if t.id == tech_id), None)
        if not tech:
            return OrderResult(order=order, accepted=False, reason=f"Tecnología no encontrada: {tech_id}")

        if tech_id in country.researched_techs:
            return OrderResult(order=order, accepted=False, reason=f"Tecnología ya investigada: {tech_id}")

        if tech.requirements and tech.requirements not in country.researched_techs:
            return OrderResult(order=order, accepted=False, reason=f"Requisito no cumplido: {tech.requirements}")

        year = game_state.scenario.year
        if year < tech.activation_year:
            return OrderResult(order=order, accepted=False, reason=f"Tecnología no disponible hasta {tech.activation_year}")

        country.researched_techs.append(tech_id)
        country.actual_research = None

        event_data = {"country_tag": order.country_tag, "tech_id": tech_id}
        game_state.log_event("TECH_RESEARCHED", event_data)
        return OrderResult(order=order, accepted=True, events=[{"type": "TECH_RESEARCHED", **event_data}])

    # ------------------------------------------------------------------
    # BUILD
    # ------------------------------------------------------------------

    def _handle_build(self, order: Order, game_state: GameState) -> OrderResult:
        building_type_id: str = order.payload.get("building_type_id", "")
        province_id: str = order.payload.get("province_id", "")

        country = game_state.get_country_state(order.country_tag)
        if not country:
            return OrderResult(order=order, accepted=False, reason=f"País no encontrado: {order.country_tag}")

        province = game_state.get_province_state(province_id)
        if not province:
            return OrderResult(order=order, accepted=False, reason=f"Provincia no encontrada: {province_id}")

        if province.owner_tag != order.country_tag:
            return OrderResult(order=order, accepted=False, reason="El país no controla esta provincia")

        building_type = game_state.world.buildings.get(building_type_id)
        if not building_type:
            return OrderResult(order=order, accepted=False, reason=f"Tipo de edificio no encontrado: {building_type_id}")

        if building_type.required_technology and building_type.required_technology not in country.researched_techs:
            return OrderResult(order=order, accepted=False, reason=f"Se requiere tecnología: {building_type.required_technology}")

        cost = float(building_type.construction_cost)
        if not country.remove_money(cost):
            return OrderResult(order=order, accepted=False, reason=f"Fondos insuficientes (requiere {cost}, tiene {country.money:.1f})")

        import time
        new_building_id = f"building_{province_id}_{building_type_id}_{int(time.time())}"
        from model.entities.state.building_state import BuildingState
        new_building = BuildingState(
            id=new_building_id,
            building_type_id=building_type_id,
            province_id=province_id,
            level=1,
            active=False,
            construction_progress=0,
        )
        game_state.buildings.append(new_building)

        event_data = {
            "country_tag": order.country_tag,
            "building_id": new_building_id,
            "building_type_id": building_type_id,
            "province_id": province_id,
            "cost": cost,
        }
        game_state.log_event("BUILD_STARTED", event_data)
        return OrderResult(order=order, accepted=True, events=[{"type": "BUILD_STARTED", **event_data}])

    # ------------------------------------------------------------------
    # ARMY_MOVE
    # ------------------------------------------------------------------

    def _handle_army_move(self, order: Order, game_state: GameState) -> OrderResult:
        army_id: str = order.payload.get("army_id", "")
        to_province_id: str = order.payload.get("to_province_id", "")

        army = game_state.get_army_state(army_id)
        if not army:
            return OrderResult(order=order, accepted=False, reason=f"Ejército no encontrado: {army_id}")

        if army.owner_tag != order.country_tag:
            return OrderResult(order=order, accepted=False, reason="El país no controla este ejército")

        # Validar adyacencia usando las definiciones del mundo
        world_province = next((p for p in game_state.world.provinces if p.id == army.province_id), None)
        if world_province and to_province_id not in world_province.adjacent_provinces:
            return OrderResult(order=order, accepted=False, reason=f"Provincia {to_province_id} no es adyacente a {army.province_id}")

        from_province_id = army.province_id
        army.province_id = to_province_id

        event_data = {
            "country_tag": order.country_tag,
            "army_id": army_id,
            "from_province_id": from_province_id,
            "to_province_id": to_province_id,
        }
        game_state.log_event("ARMY_MOVED", event_data)
        return OrderResult(order=order, accepted=True, events=[{"type": "ARMY_MOVED", **event_data}])

    # ------------------------------------------------------------------
    # DIPLOMACY
    # ------------------------------------------------------------------

    def _handle_diplomacy(self, order: Order, game_state: GameState) -> OrderResult:
        action: str = order.payload.get("action", "")
        target_tag: str = order.payload.get("target_tag", "")

        country = game_state.get_country_state(order.country_tag)
        if not country:
            return OrderResult(order=order, accepted=False, reason=f"País no encontrado: {order.country_tag}")

        target = game_state.get_country_state(target_tag)
        if not target:
            return OrderResult(order=order, accepted=False, reason=f"País objetivo no encontrado: {target_tag}")

        if action == "improve_relations":
            change = int(order.payload.get("amount", 25))
            country.modify_relation(target_tag, change)
            target.modify_relation(order.country_tag, change // 2)
        elif action == "worsen_relations":
            change = int(order.payload.get("amount", 25))
            country.modify_relation(target_tag, -change)
        else:
            return OrderResult(order=order, accepted=False, reason=f"Acción diplomática desconocida: {action}")

        event_data = {
            "country_tag": order.country_tag,
            "target_tag": target_tag,
            "action": action,
            "relation": country.get_relation(target_tag),
        }
        game_state.log_event("DIPLOMACY_ACTION", event_data)
        return OrderResult(order=order, accepted=True, events=[{"type": "DIPLOMACY_ACTION", **event_data}])
