from model.scenario.scenario import Scenario
from model.world.world import World

class ScenarioDataValidator:
    """Esta clase es la responsable de validar los datos del escenario antes de cargarlos."""
    def __init__(self, scenario: Scenario, world: World | None = None):
        self.scenario = scenario
        self.world = world

    def validate(self) -> list[str]:
        """Valida el escenario y devuelve una lista de errores encontrados."""
        errors = []
        country_tags = {c.tag for c in self.scenario.countries}
        province_ids = {p.id for p in self.scenario.provinces}
        general_ids = {g.id for g in self.scenario.generals}
        army_ids = {a.id for a in self.scenario.armies}
        building_ids = {b.id for b in self.scenario.buildings}
        cb_ids = {cb.id for cb in self.scenario.casus_belli}
        building_type_ids = set(self.world.buildings.keys()) if self.world else set()
        factory_type_ids = set(self.world.factory_types.keys()) if self.world else set()

        ## validaciones de ids unicas

        seen_tags = set()
        for country in self.scenario.countries:
            if country.tag in seen_tags:
                errors.append(f"Tag de país duplicado '{country.tag}'")
            seen_tags.add(country.tag)

        seen_ids = set()
        for province in self.scenario.provinces:
            if province.id in seen_ids:
                errors.append(f"ID de provincia duplicado '{province.id}'")
            seen_ids.add(province.id)

        seen_ids = set()
        for general in self.scenario.generals:
            if general.id in seen_ids:
                errors.append(f"ID de general duplicado '{general.id}'")
            seen_ids.add(general.id)

        seen_ids = set()
        for army in self.scenario.armies:
            if army.id in seen_ids:
                errors.append(f"ID de ejército duplicado '{army.id}'")
            seen_ids.add(army.id)

        seen_ids = set()
        for building in self.scenario.buildings:
            if building.id in seen_ids:
                errors.append(f"ID de edificio duplicado '{building.id}'")
            seen_ids.add(building.id)

        seen_ids = set()
        for cb in self.scenario.casus_belli:
            if cb.id in seen_ids:
                errors.append(f"ID de casus belli duplicado '{cb.id}'")
            seen_ids.add(cb.id)


        ## validaciones unicas por categoria

        # Countries

        # Validar que capital existe en province.ids
        for country in self.scenario.countries:
            if country.capital and country.capital not in province_ids:
                errors.append(f"País '{country.tag}' tiene capital '{country.capital}' que no existe en las provincias")

        # validar que ids en c.generals existen en el set de general ids
        for country in self.scenario.countries:
            for general_id in country.generals:
                if general_id not in general_ids:
                    errors.append(f"País '{country.tag}' tiene general_id '{general_id}' que no existe en los generales")
        
        # ids en c.armies existen en el set de army ids
        for country in self.scenario.countries:
            for army_id in country.armies:
                if army_id not in army_ids:
                    errors.append(f"País '{country.tag}' tiene army_id '{army_id}' que no existe en los ejércitos")

        # cada key de relations es un tag de country
        for country in self.scenario.countries:
            for related_tag in country.relations.keys():
                if related_tag not in country_tags:
                    errors.append(f"País '{country.tag}' tiene relación con '{related_tag}' que no existe en los países")
        
        # money
        for country in self.scenario.countries:
            if not country.money >= 0:
                errors.append(f"País '{country.tag}' tiene dinero negativo ({country.money})")

        # manpower
        for country in self.scenario.countries:
            if not country.manpower >= 0:
                errors.append(f"País '{country.tag}' tiene manpower negativo ({country.manpower})")

        # population
        for country in self.scenario.countries:
            if not country.population >= 0:
                errors.append(f"País '{country.tag}' tiene población negativa ({country.population})")


        # Generals


        # Validar que owner_tag existe en country.tags
        for general in self.scenario.generals:
            if general.owner_tag not in country_tags:
                errors.append(f"General '{general.id}' tiene owner_tag '{general.owner_tag}' que no existe en los países")
        

        # Armies

        # Validar que owner_tag existe en country.tags
        for army in self.scenario.armies:
            if army.owner_tag not in country_tags:
                errors.append(f"Ejército '{army.id}' tiene owner_tag '{army.owner_tag}' que no existe en los países")
        
        # Validar que general_id existe en general.ids o es None
        for army in self.scenario.armies:
            if army.general_id is not None and army.general_id not in general_ids:
                errors.append(f"Ejército '{army.id}' tiene general_id '{army.general_id}' que no existe en los generales")

        # province_id existe en province_ids (si no es None)
        for army in self.scenario.armies:
            if army.province_id is not None and army.province_id not in province_ids:
                errors.append(f"Ejército '{army.id}' tiene province_id '{army.province_id}' que no existe en las provincias")

        # morale entre 0.0 y 1.0
        for army in self.scenario.armies:
            if not (0.0 <= army.morale <= 1.0):
                errors.append(f"Ejército '{army.id}' tiene morale {army.morale} fuera del rango 0.0-1.0")

        # organization entre 0.0 y 1.0
        for army in self.scenario.armies:
            if not (0.0 <= army.organization <= 1.0):
                errors.append(f"Ejército '{army.id}' tiene organization {army.organization} fuera del rango 0.0-1.0")

        
        # Building snapshots

        # building_type_id existe en el world, cuando el validador tiene world
        if self.world:
            for building in self.scenario.buildings:
                if building.building_type_id not in building_type_ids:
                    errors.append(f"Edificio '{building.id}' tiene building_type_id '{building.building_type_id}' que no existe")

        # Validar que province_id existe en province.ids
        for building in self.scenario.buildings:
            if building.province_id not in province_ids:
                errors.append(f"Edificio '{building.id}' tiene province_id '{building.province_id}' que no existe en las provincias")
        
        # level >= 1 
        for building in self.scenario.buildings:
            if not building.level >= 1:
                errors.append(f"Edificio '{building.id}' tiene level {building.level} menor que 1")

        if self.world:
            for building in self.scenario.buildings:
                if building.building_type_id == "factory":
                    if not building.factory_type_id:
                        errors.append(f"Edificio factory '{building.id}' no define factory_type_id")
                    elif building.factory_type_id not in factory_type_ids:
                        errors.append(f"Edificio factory '{building.id}' tiene factory_type_id '{building.factory_type_id}' que no existe")
                elif building.factory_type_id:
                    errors.append(f"Edificio '{building.id}' define factory_type_id pero no es factory")

        
        # Casus belli snapshots

        # validar que country from y countrg to existen en country.tags
        for cb in self.scenario.casus_belli:
            if cb.country_from not in country_tags:
                errors.append(f"Casus belli '{cb.id}' tiene country_from '{cb.country_from}' que no existe en los países")
            if cb.country_to not in country_tags:
                errors.append(f"Casus belli '{cb.id}' tiene country_to '{cb.country_to}' que no existe en los países")

        # country from != country to
        for cb in self.scenario.casus_belli:
            if cb.country_from == cb.country_to:
                errors.append(f"Casus belli '{cb.id}' tiene country_from igual a country_to ('{cb.country_from}')")
        
        # expiration_tick >= 0
        for cb in self.scenario.casus_belli:
            if not cb.expiration_tick >= 0:
                errors.append(f"Casus belli '{cb.id}' tiene expiration_tick {cb.expiration_tick} menor que 0")

        return errors
