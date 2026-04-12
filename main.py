"""
TOVIC - Game alpha version 0.1.0
Desarrollado por: yussixnash! one man army!
"""

from menu.menu_system import MenuSystem


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