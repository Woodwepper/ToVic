from model.world.world import World


class WorldDataValidator:
    """Esta clase es la responsable de validar los datos del mundo antes de cargarlos."""

    def __init__(self, world: World):
        self.world = world

    def validate(self) -> list[str]:
        """Valida el mundo y devuelve una lista de errores encontrados."""
        errors = []
        province_ids = {p.id for p in self.world.provinces}
        resource_ids = {r.id for r in self.world.resources}
        terrain_type_ids = {t.id for t in self.world.terrains}
        technology_ids = {t.id for t in self.world.techs}
        building_type_ids = set(self.world.buildings.keys())
        factory_type_ids = set(self.world.factory_types.keys())
        unit_type_ids = set(self.world.unit_types.keys())
        government_type_ids = {g.id for g in self.world.governments}
        modifier_ids = {m.id for m in self.world.modifiers}
        cb_type_ids = {cb.id for cb in self.world.casus_belli_types}

        # Validaciones de IDs únicas

        seen_ids = set()
        for province in self.world.provinces:
            if province.id in seen_ids:
                errors.append(f"ID de provincia duplicado '{province.id}'")
            seen_ids.add(province.id)
        for resource in self.world.resources:
            if resource.id in seen_ids:
                errors.append(f"ID de recurso duplicado '{resource.id}'")
            seen_ids.add(resource.id)
        for terrain in self.world.terrains:
            if terrain.id in seen_ids:
                errors.append(f"ID de tipo de terreno duplicado '{terrain.id}'")
            seen_ids.add(terrain.id)
        for tech in self.world.techs:
            if tech.id in seen_ids:
                errors.append(f"ID de tecnología duplicado '{tech.id}'")
            seen_ids.add(tech.id)
        for building in self.world.buildings.values():
            if building.id in seen_ids:
                errors.append(f"ID de tipo de edificio duplicado '{building.id}'")
            seen_ids.add(building.id)
        for factory in self.world.factory_types.values():
            if factory.id in seen_ids:
                errors.append(f"ID de tipo de fábrica duplicado '{factory.id}'")
            seen_ids.add(factory.id)
        for unit in self.world.unit_types.values():
            if unit.id in seen_ids:
                errors.append(f"ID de tipo de unidad duplicado '{unit.id}'")
            seen_ids.add(unit.id)
        for government in self.world.governments:
            if government.id in seen_ids:
                errors.append(f"ID de tipo de gobierno duplicado '{government.id}'")
            seen_ids.add(government.id)
        for modifier in self.world.modifiers:
            if modifier.id in seen_ids:
                errors.append(f"ID de tipo de modificador duplicado '{modifier.id}'")
            seen_ids.add(modifier.id)
        for cb in self.world.casus_belli_types:
            if cb.id in seen_ids:
                errors.append(f"ID de tipo de casus belli duplicado '{cb.id}'")
            seen_ids.add(cb.id)

        
        ## Validaciones de referencias

        # Provinces
        
        #terrain id exiaste en terrains
        for province in self.world.provinces:
            if province.terrain_id not in terrain_type_ids:
                errors.append(f"Provincia '{province.id}' tiene terrain_id '{province.terrain_id}' que no existe en los tipos de terreno")

        #resource id existe en resources si no es none
        for province in self.world.provinces:
            if province.resource_id is not None and province.resource_id not in resource_ids:
                errors.append(f"Provincia '{province.id}' tiene resource_id '{province.resource_id}' que no existe en los recursos")

        # Cads id en adjacent_provinces existen en province_ids
        for province in self.world.provinces:
            for adj_id in province.adjacent_provinces:
                if adj_id not in province_ids:
                    errors.append(f"Provincia '{province.id}' tiene adjacent_province_id '{adj_id}' que no existe en las provincias")
        
        # adjacent_provinces es simetrico (si A es adjacent a B, entonces B es adjacent a A)
        for province in self.world.provinces:
            for adj_id in province.adjacent_provinces:
                adj_province = next((p for p in self.world.provinces if p.id == adj_id), None)
                if adj_province and province.id not in adj_province.adjacent_provinces:
                    errors.append(f"Provincia '{province.id}' es adjacent a '{adj_id}', pero no es recíproco")

        # cada key en base_buildings existe en building_type_ids
        for province in self.world.provinces:
            for building_type_id in province.base_buildings.keys():
                if building_type_id not in building_type_ids:
                    errors.append(f"Provincia '{province.id}' tiene base_building con building_type_id '{building_type_id}' que no existe en los tipos de edificio")
        
        # pop >= 0
        for province in self.world.provinces:
            if province.population < 0:
                errors.append(f"Provincia '{province.id}' tiene población negativa ({province.population})")
        
        # fort level >= 0
        for province in self.world.provinces:
            if province.fort_level < 0:
                errors.append(f"Provincia '{province.id}' tiene fort_level negativo ({province.fort_level})")


        # BuildingTypes

        # required technology existe en technology_ids
        for building in self.world.buildings.values():
            if building.required_technology and building.required_technology not in technology_ids:
                errors.append(f"BuildingType '{building.id}' tiene required_technology '{building.required_technology}' que no existe en las tecnologías")

        # cada id en modifiers existe en modifier_ids
        for building in self.world.buildings.values():
            for modifier_id in building.modifiers:
                if modifier_id not in modifier_ids:
                    errors.append(f"BuildingType '{building.id}' tiene modifier_id '{modifier_id}' que no existe en los tipos de modificador")

        
        # Technologies

        # requirements existen en technology_ids
        for technology in self.world.techs:
            if technology.requirements is not None and technology.requirements not in technology_ids:
                errors.append(f"Technology '{technology.id}' tiene requirements '{technology.requirements}' que no existe en las tecnologías")
        
        # required points >= 0
        for technology in self.world.techs:
            if technology.required_points < 0:
                errors.append(f"Technology '{technology.id}' tiene required_points negativo ({technology.required_points})")
            
        # activation year >= 0
        for technology in self.world.techs:
            if technology.activation_year < 0:
                errors.append(f"Technology '{technology.id}' tiene activation_year negativo ({technology.activation_year})")
        

        # factory types

        # cada key en input_goods existe en resource_ids
        for factory in self.world.factory_types.values():
            for resource_id in factory.input_goods.keys():
                if resource_id not in resource_ids:
                    errors.append(f"FactoryType '{factory.id}' tiene input_good '{resource_id}' que no existe en los recursos")

        # cada key en output_goods existe en resource_ids
        for factory in self.world.factory_types.values():
            for resource_id in factory.output_goods.keys():
                if resource_id not in resource_ids:
                    errors.append(f"FactoryType '{factory.id}' tiene output_good '{resource_id}' que no existe en los recursos")

        # needed workers >= 0
        for factory in self.world.factory_types.values():
            if factory.needed_workers < 0:
                errors.append(f"FactoryType '{factory.id}' tiene needed_workers negativo ({factory.needed_workers})")
        
        # production capacity >= 0
        for factory in self.world.factory_types.values():
            if factory.production_capacity < 0:
                errors.append(f"FactoryType '{factory.id}' tiene production_capacity negativo ({factory.production_capacity})")
        
        return errors