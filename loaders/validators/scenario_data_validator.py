from model.scenario.scenario import Scenario
from model.world.world import World
class ScenarioDataValidator:
    """Esta clase valida los datos de un escenario para asegurarse de que sean correctos y completos antes de cargarlos en el juego"""

    def __init__(self, scenario_data: Scenario, world: World):
        self.scenario_data = scenario_data
        self.world_data = world

    def validate(self) -> tuple[bool, list[str]]:
        errors = []

        # Validaciones generales del escenario
        if not self.scenario_data.id:
            errors.append("El escenario debe tener un ID único.")
        
        # validar el año del escenario
        if self.scenario_data.year < 1:
            errors.append("El año del escenario no puede ser menor a 1.")

        # validar que cada país tenga un tag único
        tags = set()
        for country in self.scenario_data.countries:
            if country.tag in tags:
                errors.append(f"El país con tag '{country.tag}' no es único.")
            else:
                tags.add(country.tag)

        # Construir sets de IDs válidos desde el inicio
        province_ids = {p.province_id for p in self.scenario_data.provinces}
        all_generals = set()
        all_armies = set()
        for country in self.scenario_data.countries:
            all_generals.update(country.generals)
            all_armies.update(country.armies)
        for country in self.scenario_data.countries:
            if country.capital not in province_ids:
                errors.append(f"El país '{country.tag}' tiene una capital con ID {country.capital} que no existe en las provincias.")

        # validar que pop, money y manpower sean no negativos
        for country in self.scenario_data.countries:
            if country.population < 0:
                errors.append(f"El país '{country.tag}' tiene una población negativa.")
            if country.money < 0:
                errors.append(f"El país '{country.tag}' tiene dinero negativo.")
            if country.manpower < 0:
                errors.append(f"El país '{country.tag}' tiene manpower negativo.")

        # validar que researched_techs y actual_research sean validas (no pueden tener techs que no existan en el world)
        valid_techs = {tech.id for tech in self.world_data.techs}
        for country in self.scenario_data.countries:
            for tech in country.researched_techs:
                if tech not in valid_techs:
                    errors.append(f"El país '{country.tag}' tiene una tecnología investigada '{tech}' que no existe en el mundo.")
            if country.actual_research and country.actual_research not in valid_techs:
                errors.append(f"El país '{country.tag}' tiene una tecnología en investigación '{country.actual_research}' que no existe en el mundo.")

        # validar que resources en stockpile sean válidos
        valid_resources = {resource.id for resource in self.world_data.resources}
        for country in self.scenario_data.countries:
            for resource_name in country.stockpile.resources.keys():
                if resource_name not in valid_resources:
                    errors.append(f"El país '{country.tag}' tiene un recurso en stockpile '{resource_name}' que no existe en el mundo.")

        # validar que relations tienen keys con tags de países válidos
        for country in self.scenario_data.countries:
            for tag in country.relations.keys():
                if tag not in tags:
                    errors.append(f"El país '{country.tag}' tiene una relación con un país '{tag}' que no existe en el escenario.")
            
            # validar que generals y armies lists referencien IDs válidos
            for general_id in country.generals:
                if general_id not in all_generals:
                    errors.append(f"El país '{country.tag}' tiene una referencia a general '{general_id}' que no existe.")
            for army_id in country.armies:
                if army_id not in all_armies:
                    errors.append(f"El país '{country.tag}' tiene una referencia a ejército '{army_id}' que no existe.")


        # Validaciones de provincias


        # validar que cada provincia tenga un ID único
        province_ids = set()
        for province in self.scenario_data.provinces:
            if province.province_id in province_ids:
                errors.append(f"La provincia con ID '{province.province_id}' no es única.")
            else:
                province_ids.add(province.province_id)

        # validar que cada provincia tenga un owner_tag válido
        for province in self.scenario_data.provinces:
            if province.owner is not None and province.owner not in tags:
                errors.append(f"La provincia con ID '{province.province_id}' tiene un owner '{province.owner}' que no existe en el escenario.")
        
        # validar que fort_level y population no sean negativos
        for province in self.scenario_data.provinces:
            if province.fort_level < 0:
                errors.append(f"La provincia con ID '{province.province_id}' tiene un fort_level negativo.")
            if province.population < 0:
                errors.append(f"La provincia con ID '{province.province_id}' tiene una población negativa.")
            
            # validar que resources en stockpile sean válidos
            for resource_name in province.stockpile.resources.keys():
                if resource_name not in valid_resources:
                    errors.append(f"La provincia con ID '{province.province_id}' tiene un recurso en stockpile '{resource_name}' que no existe en el mundo.")


        # Validaciones de ejércitos

        # validar que cada ejército tenga un ID único
        army_ids = set()
        for army in self.scenario_data.armies:
            if army.army_id in army_ids:
                errors.append(f"El ejército con ID '{army.army_id}' no es único.")
            else:
                army_ids.add(army.army_id)

        # validar que cada ejército tenga un owner_tag y province_id válidos
        for army in self.scenario_data.armies:
            if army.owner_tag not in tags:
                errors.append(f"El ejército con ID '{army.army_id}' tiene un owner_tag '{army.owner_tag}' que no existe en el escenario.")
            if army.province_id is not None and army.province_id not in province_ids:
                errors.append(f"El ejército con ID '{army.army_id}' tiene una province_id '{army.province_id}' que no existe en el escenario.")
            if army.general_id is not None and army.general_id not in all_generals:
                errors.append(f"El ejército con ID '{army.army_id}' tiene un general_id '{army.general_id}' que no existe en el escenario.")

        # validar que morale y organization estén entre 0 y 1
        for army in self.scenario_data.armies:
            if not (0 <= army.morale <= 1):
                errors.append(f"El ejército con ID '{army.army_id}' tiene un morale '{army.morale}' que no está entre 0 y 1.")
            if not (0 <= army.organization <= 1):
                errors.append(f"El ejército con ID '{army.army_id}' tiene una organization '{army.organization}' que no está entre 0 y 1.")

        # validar que las unidades del ejército tengan cantidades no negativas
        for army in self.scenario_data.armies:
            for unit_type, amount in army.units.units.items():
                if amount < 0:
                    errors.append(f"El ejército con ID '{army.army_id}' tiene una unidad '{unit_type}' con cantidad negativa.")
        
        # validar que units no sea vacio
        for army in self.scenario_data.armies:
            if not army.units.units:
                errors.append(f"El ejército con ID '{army.army_id}' no tiene unidades.")


        # Validaciones de casus belli


        # validar que country_from y country_to sean tags de países válidos
        for cb in self.scenario_data.casus_belli:
            if cb.country_from not in tags:
                errors.append(f"El casus belli con ID '{cb.id}' tiene un country_from '{cb.country_from}' que no existe en el escenario.")
            if cb.country_to not in tags:
                errors.append(f"El casus belli con ID '{cb.id}' tiene un country_to '{cb.country_to}' que no existe en el escenario.")

        # validar que el CB tenga un tipo válido (debe existir en el world)
        valid_cb_types = {cb_type.id for cb_type in self.world_data.casus_belli_types}
        for cb in self.scenario_data.casus_belli:
            if cb.casus_belli_type not in valid_cb_types:
                errors.append(f"El casus belli con ID '{cb.id}' tiene un tipo '{cb.casus_belli_type}' que no existe en el mundo.")

        # validar que creation tick sea menor a expiration tick
        for cb in self.scenario_data.casus_belli:
            if cb.creation_tick >= cb.expiration_tick:
                errors.append(f"El casus belli con ID '{cb.id}' tiene un creation_tick '{cb.creation_tick}' que no es menor a expiration_tick '{cb.expiration_tick}'.")
        
        return (len(errors) == 0, errors)
