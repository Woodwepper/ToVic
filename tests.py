from loaders.scenario_loader import ScenarioLoader
from loaders.validators.scenario_data_validator import ScenarioDataValidator
from loaders.validators.world_data_validator import WorldDataValidator


scenario = ScenarioLoader.load_scenario_from_file("victoria2", "1836")

print(scenario.get_country("FRA"))

validator = ScenarioDataValidator(scenario)
errors = validator.validate()
if errors:
    print(f"\n[SCENARIO VALIDATOR] {len(errors)} error(s) encontrado(s):")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

world_validator = WorldDataValidator(scenario.world)
world_errors = world_validator.validate()
if world_errors:
    print(f"\n[WORLD VALIDATOR] {len(world_errors)} error(s) encontrado(s):")
    for i, error in enumerate(world_errors, 1):
        print(f"  {i}. {error}")
else:
    print("\n[WORLD VALIDATOR] OK — sin errores")

# interfaz visual para testeos

print("Provincias:")
for province in scenario.provinces:
    print(f"ID: {province.id}, Name: {province.name}, Owner: {province.owner_tag}")
print("\nArmies:")
for army in scenario.armies:
    print(f"ID: {army.id}, Name: {army.name}, Owner: {army.owner_tag}, General ID: {army.general_id}")
print("\nGenerals:")
for general in scenario.generals:
    print(f"ID: {general.id}, Name: {general.name}, Owner Tag: {general.owner_tag}")
print("\nCountries:")
for country in scenario.countries:
    print(f"Tag: {country.tag}, Name: {country.name}, Capital: {country.capital}")
print("\nCasus Belli:")
for cb in scenario.casus_belli:
    print(f"ID: {cb.id}")
for building in scenario.buildings:
    print(f"ID: {building.id}, Province ID: {building.province_id}")

print("WORLD BUILDINGS:")
for building in scenario.world.buildings.values():
    print(f"ID: {building.id}, Province ID: {building.province_id}")

print("WORLD CASUS BELLI:")
for cb in scenario.world.casus_belli_types:
    print(f"ID: {cb.id}")

print("WORLD FACTORY TYPES:")
for factory in scenario.world.factory_types.values():
    print(f"ID: {factory.id}")

print("WORLD GOVERNMENTS:")
for gov in scenario.world.governments.values():
    print(f"ID: {gov.id}")

print("WORLD MODIFIERS:")
for mod in scenario.world.modifiers.values():
    print(f"ID: {mod.id}")

print("WORLD PROVINCES:")
for province in scenario.world.provinces.values():
    print(f"ID: {province.id}, Name: {province.name}, Owner: {province.owner_tag}")

print("WORLD RESOURCES:")
for resource in scenario.world.resources.values():
    print(f"ID: {resource.id}, Name: {resource.name}")

print("WORLD TECHNOLOGIES:")
for tech in scenario.world.technologies.values():
    print(f"ID: {tech.id}, Name: {tech.name}")

print("WORLD TERRAIN TYPES:")
for terrain in scenario.world.terrains.values():
    print(f"ID: {terrain.id}, Name: {terrain.name}")

print("WORLD UNIT TYPES:")
for unit in scenario.world.unit_types.values():
    print(f"ID: {unit.id}, Name: {unit.name}")

