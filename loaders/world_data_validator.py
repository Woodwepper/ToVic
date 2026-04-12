from model.scenario.scenario import Scenario
from model.world.world import World

class WorldDataValidator:
    def __init__(self, world: World, scenario: Scenario):
        self.world = world
        self.scenario = scenario

    def validate(self, world: World, scenario: Scenario) -> tuple[bool, list[str]]:
        errors = []

        # Validar que todas las provincias en el escenario existan en el mundo
        for province_state in scenario.province_states:
            if world.get_province(province_state.province_id) is None:
                errors.append(f"Provincia con ID {province_state.province_id} no existe en el mundo")

        # Validar que la provincia tenga terreno que exista en el mundo
        for province_state in scenario.province_states:
            province = world.get_province(province_state.province_id)
            if province and world.get_terrain(province.terrain) is None:
                errors.append(f"Provincia con ID {province_state.province_id} tiene un terreno con ID {province.terrain} que no existe en el mundo")

        # Validar que la provincia tenga un recurso existente en el mundo
        for province_state in scenario.province_states:
            province = world.get_province(province_state.province_id)
            if province and world.get_resource(province.resource) is None:
                errors.append(f"Provincia con ID {province_state.province_id} tiene un recurso con ID {province.resource} que no existe en el mundo")

        # Validar países
        for country_state in scenario.country_states:
            if country_state.money < 0:
                errors.append(f"País {country_state.tag} tiene dinero negativo: {country_state.money}")
            
            if country_state.population <= 0:
                errors.append(f"País {country_state.tag} tiene población inválida: {country_state.population}")

        # Validar ejércitos
        for army in scenario.armies:
            # Verificar que el owner_tag existe en países
            if scenario.get_country(army.owner_tag) is None:
                errors.append(f"Ejército ID {army.army_id} pertenece a país inexistente: {army.owner_tag}")
            
            # Verificar que la provincia existe
            if world.get_province(army.province_id) is None:
                errors.append(f"Ejército ID {army.army_id} está en provincia inexistente: {army.province_id}")
            
            # Verificar que los unit types existen
            if hasattr(army.units, 'units'):  # Units es un objeto con dict .units
                for unit_type_id in army.units.units.keys():
                    if unit_type_id not in world.unit_types:
                        errors.append(f"Ejército ID {army.army_id} tiene unidad inexistente: {unit_type_id}")
            
            # Verificar ranges de morale y organization (0-100)
            if not (0 <= army.morale <= 100):
                errors.append(f"Ejército ID {army.army_id} tiene moral inválida: {army.morale}")
            
            if not (0 <= army.organization <= 100):
                errors.append(f"Ejército ID {army.army_id} tiene organización inválida: {army.organization}")

        # Validar tecnologías
        if len(world.techs) == 0:
            errors.append("El mundo debe tener al menos 1 tecnología")
        
        # Verificar IDs únicos en techs
        tech_ids = set()
        for tech in world.techs:
            if tech.id in tech_ids:
                errors.append(f"Tecnología duplicada: {tech.id}")
            tech_ids.add(tech.id)

        return (len(errors) == 0, errors)
    