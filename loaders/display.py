"""Display utilities for showing game data"""

def display_provinces(provinces):
    """Muestra información de provincias"""
    print("\n" + "="*60)
    print("PROVINCIAS")
    print("="*60)
    for p in provinces:
        print(f"\n[*] {p.name} (ID: {p.id})")
        print(f"   Dueño: {p.owner or 'Ninguno'}")
        print(f"   Población: {p.population:,}")
        print(f"   Terreno: {p.terrain or 'N/A'}")
        print(f"   Recurso: {p.resource or 'Ninguno'}")
        if p.buildings:
            print(f"   Edificios: {p.buildings}")
        print(f"   Nivel de fortaleza: {p.fort_level}")


def display_resources(resources):
    """Muestra información de recursos"""
    print("\n" + "="*60)
    print("RECURSOS")
    print("="*60)
    for r in resources:
        nat = "[N] Natural" if r.is_natural else "[M] Manufacturado"
        print(f"\n[R] {r.display_name} (ID: {r.id})")
        print(f"   Tipo: {nat}")
        print(f"   Precio base: {r.base_price} de oro")
        if r.description:
            print(f"   Descripción: {r.description}")


def display_technologies(techs):
    """Muestra información de tecnologías"""
    print("\n" + "="*60)
    print("TECNOLOGÍAS")
    print("="*60)
    for t in techs:
        print(f"\n[T] {t.display_name} (ID: {t.id})")
        print(f"   Rama: {t.branch.value}")
        print(f"   Puntos requeridos: {t.required_points}")
        print(f"   Año de activación: {t.activation_year}")
        if t.requirements:
            print(f"   Requiere: {t.requirements}")
        if t.effects:
            print(f"   Efectos: {t.effects}")
        if t.description:
            print(f"   Descripción: {t.description}")


def display_terrains(terrains):
    """Muestra información de terrenos"""
    print("\n" + "="*60)
    print("TERRENOS")
    print("="*60)
    for t in terrains:
        print(f"\n[E] {t.display_name} (ID: {t.id})")
        print(f"   Límite de suministros: {t.supply_limit}")
        print(f"   Bonificación de defensa: +{t.defense_bonus}")


def display_unit_types(unit_types):
    """Muestra información de tipos de unidades"""
    print("\n" + "="*60)
    print("TIPOS DE UNIDADES")
    print("="*60)
    for unit_id, u in unit_types.items():
        print(f"\n[U] {u.display_name} (ID: {u.id})")
        print(f"   Ataque: {u.attack}")
        print(f"   Defensa: {u.defense}")
        print(f"   Costo: {u.cost} de oro")


def display_world_summary(world):
    """Muestra un resumen del mundo"""
    print("\n" + "="*70)
    print(f"[MUNDO] {world.name.upper()}")
    print("="*70)
    print(f"ID: {world.id}")
    print(f"\n[STATS] Estadísticas:")
    print(f"   - Provincias: {len(world.provinces)}")
    print(f"   - Recursos: {len(world.resources)}")
    print(f"   - Tecnologías: {len(world.techs)}")
    print(f"   - Terrenos: {len(world.terrains)}")
    print(f"   - Tipos de unidades: {len(world.unit_types)}")
