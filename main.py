"""
TOVIC - Game alpha version 0.1.0
Desarrollado por: yussixnash! one man army!
"""

"""from menu.menu_system import MenuSystem


def main():
    print("="*45)
    print("  TOVIC - Game alpha version 0.1.0")
    print("="*45)
    
    menu = MenuSystem()
    menu.main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SALIDA] Programa interrumpido.")
"""
from loaders import initialize_game, ScenarioDataValidator, WorldDataValidator

# Cargar game
game = initialize_game("victoria2", "1836")

# Validar
validator = WorldDataValidator(game.world)
is_valid, errors = validator.validate()
if not is_valid:
    print("Errores encontrados en los datos del mundo:")
    for error in errors:
        print(f"- {error}")
else:
    print("Datos del mundo válidos.")

