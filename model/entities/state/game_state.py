from __future__ import annotations
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING
from model.scenario.general import General
from model.entities.state.building_state import BuildingState
from model.entities.state.country_state import CountryState
from model.entities.state.factory import Factory
from model.entities.state.province_state import ProvinceState
from model.entities.state.army import ArmyState
from model.entities.state.casus_belli_state import CasusBelli
from model.scenario.scenario import Scenario
from model.world.world import World

if TYPE_CHECKING:
    from simulation.orders.order import Order

class GameState:
    """Estado en vivo del juego durante gameplay.
    
    Contiene instancias MUTABLES (CountryState, ProvinceState, ArmyState, etc.)
    inicializadas a partir del Scenario (snapshot inicial).
    """
    def __init__(self, world: World, scenario: Scenario, current_tick: int = 0):
        self.scenario = scenario
        self.world = world
        self.current_tick = current_tick
        
        # Crear instancias MUTABLES en STATE basadas en Scenario
        self.countries: list[CountryState] = [CountryState.from_dict(c.to_dict()) for c in scenario.countries]
        self.generals: list[General] = [General.from_dict(g.to_dict()) for g in scenario.generals]
        self.provinces: list[ProvinceState] = [ProvinceState.from_dict(p.to_dict()) for p in scenario.provinces]
        self.armies: list[ArmyState] = [ArmyState.from_dict(a.to_dict()) for a in scenario.armies]
        self.buildings: list[BuildingState] = [BuildingState.from_dict(b.to_dict()) for b in scenario.buildings]
        self.factories: list[Factory] = []  # Se puebla via submit_order BUILD o al cargar desde DB

        # Cola de órdenes pendientes para el próximo tick
        self.pending_orders: deque[Order] = deque()
        
        # Instancias activas durante jugabilidad
        self.casus_belli_active: list[CasusBelli] = [CasusBelli.from_dict(cb.to_dict()) for cb in scenario.casus_belli]
        
        # Sistema de logging de eventos (máximo 10000 eventos en memoria)
        self.event_log: deque = deque(maxlen=10000)
        self.event_cache: dict = {}  # Para estadísticas rápidas por tipo

    # GET FUNCTIONS

    def get_date(self) -> str:
        """Retorna la fecha actual en formato Year-Month-Day"""
        return f"{self.scenario.year}-{self.scenario.month:02d}-{self.scenario.day:02d}"

    def get_info(self) -> str:
        """Retorna información del estado del juego"""
        return f"Date: {self.get_date()}, Current Tick: {self.current_tick}, Scenario: {self.scenario.name}"
    
    def get_country_state(self, country_tag: str) -> CountryState | None:
        """Obtiene el estado MUTABLE de un país por su tag"""
        for country in self.countries:
            if country.tag == country_tag:
                return country
        return None
    
    def get_province_state(self, province_id: str) -> ProvinceState | None:
        """Obtiene el estado MUTABLE de una provincia por su ID"""
        for province in self.provinces:
            if province.id == province_id:
                return province
        return None

    def get_general(self, general_id: str) -> General | None:
        """Obtiene un general por su ID"""
        for general in self.generals:
            if general.id == general_id:
                return general
        return None
    
    def get_army_state(self, army_id: str) -> ArmyState | None:
        """Obtiene el estado MUTABLE de un ejército por su ID"""
        for army in self.armies:
            if army.id == army_id:
                return army
        return None

    def get_building_state(self, building_id: str) -> BuildingState | None:
        """Obtiene el estado MUTABLE de un edificio por su ID"""
        for building in self.buildings:
            if building.id == building_id:
                return building
        return None
    
    def get_casus_belli(self, cb_id: str) -> CasusBelli | None:
        """Obtiene un casus belli activo por su ID"""
        for cb in self.casus_belli_active:
            if cb.id == cb_id:
                return cb
        return None
    
    def has_casus_belli(self, cb_id: str) -> bool:
        """Verifica si existe un CB activo"""
        return any(cb.id == cb_id and cb.active for cb in self.casus_belli_active)
    
    def list_casus_belli(self) -> list[CasusBelli]:
        """Retorna la lista de CBs activos"""
        return [cb for cb in self.casus_belli_active if cb.active]
    
# ADVANCE FUNCTIONS
    
    def advance_tick(self) -> None:
        """Avanza un tick en el juego (1 tick = 1 día internamente)"""
        self.current_tick += 1
        self.advance_day()

    def advance_day(self) -> None:
        """Avanza un día en el escenario"""
        self.scenario.day += 1
        if self.scenario.day > 30:  
            self.scenario.day = 1
            self.advance_month()
    
    def advance_month(self) -> None:
        """Avanza un mes en el escenario"""
        self.scenario.month += 1
        if self.scenario.month > 12:
            self.scenario.month = 1
            self.advance_year()
    
    def advance_year(self) -> None:
        """Avanza un año en el escenario"""
        self.scenario.year += 1

    # EVENT LOGGING & REPLAY

    def log_event(self, event_type: str, event_data: dict) -> None:
        """Registra un evento en el log para auditoría y replay
        
        Cada evento se registra con timestamp y tick actual
        """
        event = {
            'tick': self.current_tick,
            'date': self.get_date(),
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        }
        self.event_log.append(event)
        
        if event_type not in self.event_cache:
            self.event_cache[event_type] = 0
        self.event_cache[event_type] += 1

    def get_event_log(self, event_type: str | None = None, limit: int | None = None) -> list[dict]:
        """Obtiene el historial de eventos
        
        Si event_type es None, retorna todos. Límite opcional.
        """
        events = [e for e in self.event_log]
        
        if event_type:
            events = [e for e in events if e['type'] == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events

    def get_event_statistics(self) -> dict[str, int]:
        """Retorna estadísticas de eventos registrados"""
        return dict(self.event_cache)

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario.to_dict(),
            "world": self.world.to_dict(),
            "current_tick": self.current_tick,
            "countries": [country.to_dict() for country in self.countries],
            "generals": [general.to_dict() for general in self.generals],
            "provinces": [province.to_dict() for province in self.provinces],
            "armies": [army.to_dict() for army in self.armies],
            "buildings": [building.to_dict() for building in self.buildings],
            "casus_belli_active": [cb.to_dict() for cb in self.casus_belli_active],
            "event_log": list(self.event_log)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        instance = cls(
            scenario=Scenario.from_dict(data["scenario"]),
            world=World.from_dict(data["world"]),
            current_tick=data.get("current_tick", 0)
        )

        if "countries" in data:
            instance.countries = [CountryState.from_dict(country) for country in data["countries"]]
        if "generals" in data:
            instance.generals = [General.from_dict(general) for general in data["generals"]]
        if "provinces" in data:
            instance.provinces = [ProvinceState.from_dict(province) for province in data["provinces"]]
        if "armies" in data:
            instance.armies = [ArmyState.from_dict(army) for army in data["armies"]]
        if "buildings" in data:
            instance.buildings = [BuildingState.from_dict(building) for building in data["buildings"]]
        if "casus_belli_active" in data:
            instance.casus_belli_active = [CasusBelli.from_dict(cb) for cb in data["casus_belli_active"]]

        # Restaurar event log si existe
        if "event_log" in data:
            instance.event_log.extend(data["event_log"])
            for event in data["event_log"]:
                event_type = event.get('type', 'unknown')
                if event_type not in instance.event_cache:
                    instance.event_cache[event_type] = 0
                instance.event_cache[event_type] += 1
        return instance

    # ORDER QUEUE

    def submit_order(self, order: "Order") -> None:
        """Encola una orden para ser procesada al final del tick actual."""
        from simulation.orders.order import Order as _Order  # local import evita ciclo
        order.submitted_tick = self.current_tick
        self.pending_orders.append(order)

