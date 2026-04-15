"""
TOVIC - Game Engine v0.1.0
Desarrollado por: yussixnash! one man army!

Sistema de validacion y carga del juego.
"""

from loaders import initialize_game, WorldDataValidator, ScenarioDataValidator, ScenarioWorldValidator


def print_section(title: str):
    """Imprime un separador de seccion"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def validate_and_summary(template: str, year: str):
    """Carga game, valida todos los datos, y muestra resumen"""
    
    print_section(f"INICIALIZANDO JUEGO: {template.upper()} - {year}")
    
    try:
        # Cargar game (World + Scenario + GameState)
        print(f"\n[CARGANDO] Game desde plantilla '{template}' - Ano {year}...")
        game = initialize_game(template, year)
        print("[OK] Game cargado exitosamente")
        
    except FileNotFoundError as e:
        print(f"[ERROR] Plantilla no encontrada - {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error al cargar game: {e}")
        return False
    
    # =================================================================
    # VALIDAR WORLD
    # =================================================================
    print_section("VALIDACION DE MUNDO (DEFINICIONES)")
    
    world_validator = WorldDataValidator(game.world)
    world_valid, world_errors = world_validator.validate()
    
    if world_valid:
        print("[OK] Mundo: VALIDO")
    else:
        print(f"[FALLO] Mundo: {len(world_errors)} ERRORES ENCONTRADOS:")
        for error in world_errors:
            print(f"  - {error}")
        return False
    
    # =================================================================
    # VALIDAR SCENARIO
    # =================================================================
    print_section("VALIDACION DE ESCENARIO (ESTADO INICIAL)")
    
    scenario_validator = ScenarioDataValidator(game.scenario, game.world)
    scenario_valid, scenario_errors = scenario_validator.validate()
    
    if scenario_valid:
        print("[OK] Escenario: VALIDO")
    else:
        print(f"[FALLO] Escenario: {len(scenario_errors)} ERRORES ENCONTRADOS:")
        for error in scenario_errors:
            print(f"  - {error}")
        return False
    
    # =================================================================
    # VALIDAR INTEGRIDAD SCENARIO-WORLD
    # =================================================================
    print_section("VALIDACION DE INTEGRIDAD SCENARIO <-> MUNDO")
    
    scenario_world_validator = ScenarioWorldValidator(game.scenario, game.world)
    sw_valid, sw_errors = scenario_world_validator.validate()
    
    if sw_valid:
        print("[OK] Integridad: VALIDO")
    else:
        print(f"[FALLO] Integridad: {len(sw_errors)} ERRORES ENCONTRADOS:")
        for error in sw_errors:
            print(f"  - {error}")
        return False
    
    # =================================================================
    # RESUMEN DEL MUNDO
    # =================================================================
    print_section("RESUMEN DEL MUNDO")
    
    print(f"\n[MUNDO]")
    print(f"  ID: {game.world.id}")
    print(f"  Nombre: {game.world.name}")
    print(f"  Provincias: {len(game.world.provinces)}")
    print(f"  Terrenos: {len(game.world.terrains)}")
    print(f"  Recursos: {len(game.world.resources)}")
    print(f"  Tecnologias: {len(game.world.techs)}")
    print(f"  Tipos de Unidades: {len(game.world.unit_types)}")
    print(f"  Edificios: {len(game.world.buildings)}")
    print(f"  Fabricas: {len(game.world.factory_types)}")
    print(f"  Gobiernos: {len(game.world.governments)}")
    print(f"  Modificadores: {len(game.world.modifiers)}")
    print(f"  Tipos de Casus Belli: {len(game.world.casus_belli_types)}")
    
    # =================================================================
    # RESUMEN DEL ESCENARIO
    # =================================================================
    print_section("RESUMEN DEL ESCENARIO")
    
    print(f"\n[ESCENARIO]")
    print(f"  ID: {game.scenario.id}")
    print(f"  Nombre: {game.scenario.name}")
    print(f"  Ano: {game.scenario.year}")
    print(f"  Mes: {game.scenario.month}")
    print(f"  Dia: {game.scenario.day}")
    print(f"  Paises: {len(game.scenario.countries)}")
    print(f"  Provincias: {len(game.scenario.provinces)}")
    print(f"  Ejercitos: {len(game.scenario.armies)}")
    print(f"  Casus Belli: {len(game.scenario.casus_belli)}")
    
    # Detalles de paises
    print(f"\n[PAISES]")
    for country in game.scenario.countries:
        capital = game.world.get_province(country.capital)
        capital_name = capital.name if capital else "DESCONOCIDA"
        print(f"  {country.tag}: {country.name}")
        print(f"    - Capital: {capital_name} (ID {country.capital})")
        print(f"    - Poblacion: {country.population:,}")
        print(f"    - Dinero: {country.money:,.2f}")
        print(f"    - Manpower: {country.manpower:,}")
        print(f"    - Tecnologias: {len(country.researched_techs)}")
        print(f"    - Ejercitos: {len(country.armies)}")
    
    # Detalles de provincias
    print(f"\n[PROVINCIAS]")
    for province in game.scenario.provinces:
        world_prov = game.world.get_province(province.province_id)
        owner_country = next((c.tag for c in game.scenario.countries if c.tag == province.owner), "NEUTRAL")
        terrain = game.world.get_terrain(world_prov.terrain_id) if world_prov else None
        terrain_name = terrain.display_name if terrain else "DESCONOCIDA"
        
        print(f"  ID {province.province_id}: {world_prov.name if world_prov else '?'}")
        print(f"    - Propietario: {owner_country}")
        print(f"    - Terreno: {terrain_name}")
        print(f"    - Poblacion: {province.population:,}")
        print(f"    - Nivel de Fuertes: {province.fort_level}")
    
    # Detalles de ejercitos
    print(f"\n[EJERCITOS]")
    for army in game.scenario.armies:
        owner_country = army.owner_tag
        province = game.world.get_province(army.province_id) if army.province_id else None
        province_name = province.name if province else "MOVIENDOSE"
        
        print(f"  Ejercito ID {army.army_id}: {army.name}")
        print(f"    - Propietario: {owner_country}")
        print(f"    - Provincia: {province_name} (ID {army.province_id})")
        print(f"    - Moral: {army.morale:.2%}")
        print(f"    - Organizacion: {army.organization:.2%}")
        print(f"    - Unidades: {len(army.units.units)} tipos")
        for unit_type, amount in army.units.units.items():
            print(f"      * {unit_type}: {amount}")
    
    # =================================================================
    # RESUMEN DE GAME STATE
    # =================================================================
    print_section("RESUMEN DE GAME STATE")
    
    print(f"\n[GAME STATE]")
    print(f"  Tick actual: {game.current_tick}")
    print(f"  Ano: {game.scenario.year}")
    print(f"  Paises activos: {len(game.countries)}")
    print(f"  Provincias controladas: {len(game.provinces)}")
    print(f"  Ejercitos en campana: {len(game.armies)}")
    print(f"  Casus Belli activos: {len(game.casus_belli_active)}")
    
    # =================================================================
    # RESULTADO FINAL
    # =================================================================
    print_section("RESULTADO FINAL")
    print("\n[OK] TODAS LAS VALIDACIONES PASADAS")
    print("[OK] GAME STATE LISTO PARA SIMULACION")
    print(f"\n-> Sistema listo para ejecutar ticks de simulacion")
    
    return True


if __name__ == "__main__":
    try:
        success = validate_and_summary("victoria2", "1836")
        
        if not success:
            print("\n[FALLO] INICIALIZACION FALLIDA")
            exit(1)
        
    except KeyboardInterrupt:
        print("\n\n[SALIDA] Programa interrumpido por usuario.")
        exit(1)
    except Exception as e:
        print(f"\n[ERROR] ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

