from menu.menu_system import MenuSystem
"""from loaders.scenario_loader import load_scenario
from loaders.template_manager import list_available_worlds, list_available_scenarios, load_world_data
from loaders.display import (
    display_world_summary,
    display_provinces,
    display_resources,
    display_technologies,
    display_terrains,
    display_unit_types,
)
from loaders.world_data_validator import WorldDataValidator
from model.entities.state.game_state import GameState
from simulation.simple_simulation import SimpleSimulation

print("Mundos disponibles:")
worlds = list_available_worlds()

for world in worlds:
    print(f"- {world}")
    scenarios = list_available_scenarios(world)
    print("  Escenarios disponibles:")
    for scenario_year in scenarios:
        print(f"  - {scenario_year}")

print("\nCargando mundo 'victoria2'...")
world_data = load_world_data("victoria2")
scenario_data = load_scenario("victoria2", "1836")

# Mostrar resumen del mundo
display_world_summary(world_data)

# Mostrar detalles de cada aspecto
display_provinces(world_data.provinces)
display_resources(world_data.resources)
display_technologies(world_data.techs)
display_terrains(world_data.terrains)
display_unit_types(world_data.unit_types)

validator = WorldDataValidator(world_data, scenario_data)
is_valid, errors = validator.validate(world_data, scenario_data)

print("\n" + "="*60)
print("VALIDACIÓN DE DATOS")
print("="*60)
if not is_valid:
    print(f"[ERROR] Se encontraron {len(errors)} errores:")
    for error in errors:
        print(f"  - {error}")
else:
    print("[OK] Todos los datos son válidos")

# Crear GameState
game_state = GameState(world_data, scenario_data)

# Crear y ejecutar simulación
sim = SimpleSimulation(game_state)
sim.start()
sim.run_n_ticks(10)  # Ejecuta 10 ticks
print("\nEstado de la simulación:")
print(sim.get_status())"""

menu = MenuSystem()
menu.main_menu()