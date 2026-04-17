from loaders.scenario_loader import ScenarioLoader
from loaders.validators.scenario_data_validator import ScenarioDataValidator

scenario = ScenarioLoader.load_scenario_from_file("victoria2", "1836")

print(scenario.get_country("FRA"))

validator = ScenarioDataValidator(scenario)
errors = validator.validate()
if errors:
    print(f"\n[SCENARIO VALIDATOR] {len(errors)} error(s) encontrado(s):")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
else:
    print("\n[SCENARIO VALIDATOR] OK — sin errores")

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
