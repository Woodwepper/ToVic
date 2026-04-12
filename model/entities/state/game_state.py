from model.entities.state.country_state import CountryState
from model.entities.state.province_state import ProvinceState
from model.entities.state.army import Army
from model.scenario.scenario import Scenario
from model.world.world import World

class GameState:
    def __init__(self, world, scenario, current_tick: int = 0):
        self.scenario = scenario
        self.world = world
        self.current_tick = current_tick

# GET FUNCTIONS

    def get_date(self) -> str:
        """Retorna la fecha actual en formato Year-Month-Day"""
        return f"{self.scenario.year}-{self.scenario.month:02d}-{self.scenario.day:02d}"

    def get_info(self) -> str:
        """Retorna información del estado del juego"""
        return f"Date: {self.get_date()}, Current Tick: {self.current_tick}, Scenario: {self.scenario.name}"
    
    def get_country_state(self, country_tag: str) -> CountryState | None:
        """Obtiene el estado de un país por su tag"""
        for country in self.scenario.country_states:
            if country.country_tag == country_tag:
                return country
        return None
    
    def get_province_state(self, province_id: int) -> ProvinceState | None:
        """Obtiene el estado de una provincia por su ID"""
        for province in self.scenario.province_states:
            if province.province_id == province_id:
                return province
        return None
    
    def get_army_state(self, army_id: int) -> Army | None:
        for army in self.scenario.armies:
            if army.army_id == army_id:
                return army
        return None
    
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

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario.to_dict(),
            "world": self.world.to_dict(),
            "current_tick": self.current_tick
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        return cls(
            scenario=Scenario.from_dict(data["scenario"]),
            world=World.from_dict(data["world"]),
            current_tick=data.get("current_tick", 0)
        )
