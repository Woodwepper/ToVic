from model.scenario.scenario import Scenario
from model.world.world import World


class WorldDataValidator:
    """Valida la integridad de las definiciones del mundo (World)."""
    
    def __init__(self, world: World):
        self.world = world

    def validate(self) -> tuple[bool, list[str]]:
        errors = []

        # ═══════════════════════════════════════════════════════════════
        # Validaciones generales del mundo
        # ═══════════════════════════════════════════════════════════════
        if not self.world.id:
            errors.append("El mundo debe tener un ID único.")
        
        if not self.world.name:
            errors.append("El mundo debe tener un nombre.")

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Provincias
        # ═══════════════════════════════════════════════════════════════
        province_ids = set()
        for province in self.world.provinces:
            # Validar ID único
            if province.id in province_ids:
                errors.append(f"Provincia con ID '{province.id}' no es única.")
            province_ids.add(province.id)
            
            # Validar que el terreno exista
            if not self.world.get_terrain(province.terrain_id):
                errors.append(f"Provincia '{province.name}' (ID {province.id}) refiere a terreno '{province.terrain_id}' que no existe.")
            
            # Validar que el recurso exista (si está definido)
            if province.resource_id and not self.world.get_resource(province.resource_id):
                errors.append(f"Provincia '{province.name}' (ID {province.id}) refiere a recurso '{province.resource_id}' que no existe.")
            
            # Validar que provincias adyacentes existan
            for adjacent_id in province.adjacent_provinces:
                if adjacent_id not in province_ids and not any(p.id == adjacent_id for p in self.world.provinces):
                    errors.append(f"Provincia '{province.name}' (ID {province.id}) refiere a provincia adyacente '{adjacent_id}' que no existe.")
            
            # Validar que base_buildings son válidos
            for building_id in province.base_buildings.keys():
                if not self.world.get_building(building_id):
                    errors.append(f"Provincia '{province.name}' (ID {province.id}) refiere a edificio '{building_id}' que no existe.")

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Terrenos
        # ═══════════════════════════════════════════════════════════════
        if len(self.world.terrains) == 0:
            errors.append("El mundo debe tener al menos 1 terreno.")
        
        terrain_ids = set()
        for terrain in self.world.terrains:
            if terrain.id in terrain_ids:
                errors.append(f"Terreno con ID '{terrain.id}' no es único.")
            terrain_ids.add(terrain.id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Recursos
        # ═══════════════════════════════════════════════════════════════
        if len(self.world.resources) == 0:
            errors.append("El mundo debe tener al menos 1 recurso.")
        
        resource_ids = set()
        for resource in self.world.resources:
            if resource.id in resource_ids:
                errors.append(f"Recurso con ID '{resource.id}' no es único.")
            resource_ids.add(resource.id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Tecnologías
        # ═══════════════════════════════════════════════════════════════
        if len(self.world.techs) == 0:
            errors.append("El mundo debe tener al menos 1 tecnología.")
        
        tech_ids = set()
        for tech in self.world.techs:
            if tech.id in tech_ids:
                errors.append(f"Tecnología con ID '{tech.id}' no es única.")
            tech_ids.add(tech.id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Tipos de Unidades
        # ═══════════════════════════════════════════════════════════════
        if len(self.world.unit_types) == 0:
            errors.append("El mundo debe tener al menos 1 tipo de unidad.")
        
        for unit_type_id, unit_type in self.world.unit_types.items():
            if unit_type_id != unit_type.id:
                errors.append(f"Tipo de unidad '{unit_type_id}' tiene ID interno '{unit_type.id}' que no coincide.")

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Gobiernos
        # ═══════════════════════════════════════════════════════════════
        if len(self.world.governments) == 0:
            errors.append("El mundo debe tener al menos 1 gobierno.")
        
        government_ids = set()
        for government in self.world.governments:
            if government.id in government_ids:
                errors.append(f"Gobierno con ID '{government.id}' no es único.")
            government_ids.add(government.id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Modificadores
        # ═══════════════════════════════════════════════════════════════
        modifier_ids = set()
        for modifier in self.world.modifiers:
            if modifier.id in modifier_ids:
                errors.append(f"Modificador con ID '{modifier.id}' no es único.")
            modifier_ids.add(modifier.id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Casus Belli Types
        # ═══════════════════════════════════════════════════════════════
        cb_type_ids = set()
        for cb_type in self.world.casus_belli_types:
            if cb_type.id in cb_type_ids:
                errors.append(f"Tipo de casus belli con ID '{cb_type.id}' no es único.")
            cb_type_ids.add(cb_type.id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Edificios
        # ═══════════════════════════════════════════════════════════════
        building_ids = set()
        for building_id, building in self.world.buildings.items():
            if building_id != building.id:
                errors.append(f"Edificio '{building_id}' tiene ID interno '{building.id}' que no coincide.")
            if building_id in building_ids:
                errors.append(f"Edificio con ID '{building_id}' no es único.")
            building_ids.add(building_id)

        # ═══════════════════════════════════════════════════════════════
        # Validaciones de Tipos de Fábricas
        # ═══════════════════════════════════════════════════════════════
        factory_type_ids = set()
        for factory_type_id, factory_type in self.world.factory_types.items():
            if factory_type_id != factory_type.id:
                errors.append(f"Tipo de fábrica '{factory_type_id}' tiene ID interno '{factory_type.id}' que no coincide.")
            if factory_type_id in factory_type_ids:
                errors.append(f"Tipo de fábrica con ID '{factory_type_id}' no es único.")
            factory_type_ids.add(factory_type_id)

        return (len(errors) == 0, errors)


class ScenarioWorldValidator:
    """Valida integridad referencial entre Escenario y Mundo."""
    
    def __init__(self, scenario: Scenario, world: World):
        self.scenario = scenario
        self.world = world

    def validate(self) -> tuple[bool, list[str]]:
        errors = []

        # ═══════════════════════════════════════════════════════════════
        # Validar que Scenario refiere a World
        # ═══════════════════════════════════════════════════════════════

        # Validar que scenario provinces existan en world provinces
        for scenario_province in self.scenario.provinces:
            world_province = self.world.get_province(scenario_province.province_id)
            if not world_province:
                errors.append(f"Escenario: Provincia con ID {scenario_province.province_id} no existe en mundo.")

        # Validar que scenario armies refieren a unit types válidos
        for army in self.scenario.armies:
            if hasattr(army.units, 'units'):
                for unit_type_id in army.units.units.keys():
                    if unit_type_id not in self.world.unit_types:
                        errors.append(f"Escenario: Ejército ID {army.army_id} refiere a tipo de unidad '{unit_type_id}' que no existe en mundo.")

        # Validar que scenario armies refieren a provincias válidas
        for army in self.scenario.armies:
            if army.province_id is not None and not self.world.get_province(army.province_id):
                errors.append(f"Escenario: Ejército ID {army.army_id} está en provincia ID {army.province_id} que no existe en mundo.")

        # Validar que scenario countries refieren a provincias válidas (capital)
        for country in self.scenario.countries:
            if not self.world.get_province(country.capital):
                errors.append(f"Escenario: País '{country.tag}' tiene capital provincia ID {country.capital} que no existe en mundo.")

        # Validar que scenario country stockpile resources existen en world
        for country in self.scenario.countries:
            for resource_name in country.stockpile.resources.keys():
                if not self.world.get_resource(resource_name):
                    errors.append(f"Escenario: País '{country.tag}' stockpile refiere a recurso '{resource_name}' que no existe en mundo.")

        # Validar que scenario province stockpile resources existen en world
        for province in self.scenario.provinces:
            for resource_name in province.stockpile.resources.keys():
                if not self.world.get_resource(resource_name):
                    errors.append(f"Escenario: Provincia ID {province.province_id} stockpile refiere a recurso '{resource_name}' que no existe en mundo.")

        # Validar que scenario casus belli types existen en world
        for cb in self.scenario.casus_belli:
            if not self.world.get_casus_belli_type(cb.casus_belli_type):
                errors.append(f"Escenario: Casus belli ID {cb.id} refiere a tipo '{cb.casus_belli_type}' que no existe en mundo.")

        return (len(errors) == 0, errors)
    