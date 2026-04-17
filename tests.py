from loaders.managers.scenario_loader import ScenarioLoader
from loaders.validators.scenario_data_validator import ScenarioDataValidator
from loaders.validators.world_data_validator import WorldDataValidator
from loaders.managers.world_loader import TemplateManager

scenario = ScenarioLoader.load_scenario_from_file("victoria2", "1836")
world = TemplateManager.load_world("victoria2")
print(scenario.get_country("FRA"))

validator = ScenarioDataValidator(scenario)
errors = validator.validate()
if errors:
    print(f"\n[SCENARIO VALIDATOR] {len(errors)} error(s) encontrado(s):")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

world_validator = WorldDataValidator(world)
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

print("\n── WORLD ──────────────────────────────")

print(f"\nBuildings ({len(world.buildings)}):")
for b in world.buildings.values():
    print(f"  [{b.id}] {b.name} | categoria: {b.category} | costo: {b.construction_cost} | tech requerida: {b.required_technology or 'ninguna'}")

print(f"\nCasus Belli Types ({len(world.casus_belli_types)}):")
for cb in world.casus_belli_types:
    print(f"  [{cb.id}] {cb.name} | war_goal: {cb.war_goal} | validez: {cb.validity_days} días")

print(f"\nFactory Types ({len(world.factory_types)}):")
for f in world.factory_types.values():
    print(f"  [{f.id}] {f.name} | workers: {f.needed_workers} | capacidad: {f.production_capacity}")
    print(f"    input:  {f.input_goods}")
    print(f"    output: {f.output_goods}")

print(f"\nGovernments ({len(world.governments)}):")
for g in world.governments:
    print(f"  [{g.id}] {g.name}")

print(f"\nModifiers ({len(world.modifiers)}):")
for m in world.modifiers:
    print(f"  [{m.id}] {m.name} | scope: {m.scope} | effects: {m.effects}")

print(f"\nProvinces ({len(world.provinces)}):")
for p in world.provinces:
    print(f"  [{p.id}] {p.name} | terrain: {p.terrain_id} | resource: {p.resource_id or 'ninguno'} | pop: {p.population}")

print(f"\nResources ({len(world.resources)}):")
for r in world.resources:
    print(f"  [{r.id}] {r.name} | precio base: {r.base_price} | natural: {r.is_natural}")

print(f"\nTechs ({len(world.techs)}):")
for t in world.techs:
    print(f"  [{t.id}] {t.name} | rama: {t.branch.value} | año: {t.activation_year} | puntos: {t.required_points}")

print(f"\nTerrains ({len(world.terrains)}):")
for t in world.terrains:
    print(f"  [{t.id}] {t.name} | defensa: {t.defense_bonus} | supply: {t.supply_limit}")

print(f"\nUnit Types ({len(world.unit_types)}):")
for u in world.unit_types.values():
    print(f"  [{u.id}] {u.name} | ataque: {u.attack} | defensa: {u.defense} | costo: {u.cost}")

