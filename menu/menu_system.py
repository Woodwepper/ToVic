from loaders.managers.scenario_loader import load_scenario
from loaders.managers.world_loader import list_available_worlds, list_available_scenarios, load_world_data
from loaders.validators.world_data_validator import WorldDataValidator
from model import world
from model.entities.state.game_state import GameState
from simulation.simple_simulation import SimpleSimulation


class MenuSystem:
    def __init__(self, simulation = None, running: bool = True):
        self.selected_world = None
        self.selected_scenario = None
        self.simulation = simulation
        self.running = running

    def main_menu(self):
        while self.running:
            print("=== Menú Principal ===")
            print("1. Seleccionar Mundo")
            print("2. Seleccionar Escenario")
            print("3. Validar Datos")
            print("4. Iniciar Simulación")
            print("5. Ver Estado de la Simulación")
            print("6. Salir")

            choice = input("Seleccione una opción: ")
            if choice not in ["1", "2", "3", "4", "5", "6"]:
                print("Opción no válida. Intente de nuevo.")
                continue

            if choice == "1":

                print("Mundos disponibles:")

                worlds = list_available_worlds()
                for i, world in enumerate(worlds, start=1):
                    print(f"- {i} {world}")
                
                temp_choice = input("Seleccione un mundo: ")
                
                if temp_choice.isdigit() and 1 <= int(temp_choice) <= len(worlds):
                    selected_world = worlds[int(temp_choice) - 1]
                    self.selected_world = selected_world
                    print(f"Mundo '{selected_world}' seleccionado.")
                
                else:
                    print("Mundo no válido.")

            elif choice == "2":
                if not self.selected_world:
                    print("Primero seleccione un mundo.")
                    continue
                scenarios = list_available_scenarios(self.selected_world)
                print(f"Escenarios disponibles para '{self.selected_world}':")
                for i, scenario in enumerate(scenarios, start=1):
                    print(f"- {i} {scenario}")
                
                temp_choice = input("Seleccione un escenario: ")

                if temp_choice.isdigit() and 1 <= int(temp_choice) <= len(scenarios):
                    selected_scenario = scenarios[int(temp_choice) - 1]
                    self.selected_scenario = load_scenario(self.selected_world, selected_scenario)
                    print(f"Escenario '{selected_scenario}' seleccionado.")
                else:
                    print("Escenario no válido.")

            elif choice == "3":
                if not self.selected_world or not self.selected_scenario:
                    print("Primero seleccione un mundo y un escenario.")
                    continue

                world = load_world_data(self.selected_world)
                scenario = self.selected_scenario
                validator = WorldDataValidator(world, scenario)
                is_valid, errors = validator.validate(world, scenario)

                print("\n" + "="*60)
                print("VALIDACION DE DATOS")
                print("="*60)
                if not is_valid:
                    print(f"[ERROR] Se encontraron {len(errors)} errores:")
                    for error in errors:
                        print(f"  - {error}")
                else:
                    print("[OK] Todos los datos son validos")

            elif choice == "4":
                if not self.selected_world or not self.selected_scenario:
                    print("Primero seleccione un mundo y un escenario.")
                    continue
                world = load_world_data(self.selected_world) 
                game_state = GameState(world, self.selected_scenario)
                self.simulation = SimpleSimulation(game_state)
                self.simulation.start()
                n_ticks = input("¿Cuántos ticks ejecutar? ")
                if n_ticks.isdigit():
                    self.simulation.run_n_ticks(int(n_ticks))

            elif choice == "5":
                if not self.simulation:
                    print("Primero inicie la simulación.")
                    continue
                status = self.simulation.get_status()
                print("\nEstado de la Simulación:")
                for key, value in status.items():
                    print(f"{key}: {value}")
            
            elif choice == "6":
                print("Saliendo del programa...")
                self.running = False