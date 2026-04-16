from dataclasses import dataclass, field
from model.enums.world_state import WorldState
from model.world.building_type import BuildingType
from model.world.casus_belli import CasusBelli
from model.world.factory_type import FactoryType
from model.world.government import Government
from model.world.modifier import Modifier
from model.world.province import Province
from model.world.resource import Resource
from model.world.technology import Technology
from model.world.terrain import Terrain
from model.world.unit_type import UnitType
@dataclass
class World:
    id: str
    name: str
    state: WorldState = WorldState.DRAFT
    buildings: dict[str, BuildingType] = field(default_factory=dict)
    casus_belli_types: list[CasusBelli] = field(default_factory=list)
    factory_types: dict[str, FactoryType] = field(default_factory=dict)
    governments: list[Government] = field(default_factory=list)
    modifiers: list[Modifier] = field(default_factory=list)
    provinces: list[Province] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    techs: list[Technology] = field(default_factory=list)
    terrains: list[Terrain] = field(default_factory=list)
    unit_types: dict[str, UnitType] = field(default_factory=dict)
    template_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "buildings": {k: v.to_dict() for k, v in self.buildings.items()},
            "casus_belli_types": [cb.to_dict() for cb in self.casus_belli_types],
            "factory_types": {k: v.to_dict() for k, v in self.factory_types.items()},
            "governments": [g.to_dict() for g in self.governments],
            "modifiers": [m.to_dict() for m in self.modifiers],
            "provinces": [p.to_dict() for p in self.provinces],
            "resources": [r.to_dict() for r in self.resources],
            "techs": [t.to_dict() for t in self.techs],
            "terrains": [t.to_dict() for t in self.terrains],
            "unit_types": {k: v.to_dict() for k, v in self.unit_types.items()},
            "template_id": self.template_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'World':
        buildings_data = data.get("buildings", {})
        if isinstance(buildings_data, list):
            buildings_data = {b["id"]: b for b in buildings_data}

        factory_types_data = data.get("factory_types", {})
        if isinstance(factory_types_data, list):
            factory_types_data = {f["id"]: f for f in factory_types_data}

        unit_types_data = data.get("unit_types", {})
        if isinstance(unit_types_data, list):
            unit_types_data = {u["id"]: u for u in unit_types_data}

        return cls(
            id=data["id"],
            name=data["name"],
            state=WorldState(data.get("state", WorldState.DRAFT.value)),
            buildings={k: BuildingType.from_dict(v) for k, v in buildings_data.items()},
            casus_belli_types=[CasusBelli.from_dict(cb) for cb in data.get("casus_belli_types", [])],
            factory_types={k: FactoryType.from_dict(v) for k, v in factory_types_data.items()},
            governments=[Government.from_dict(g) for g in data.get("governments", [])],
            modifiers=[Modifier.from_dict(m) for m in data.get("modifiers", [])],
            provinces=[Province.from_dict(p) for p in data.get("provinces", [])],
            resources=[Resource.from_dict(r) for r in data.get("resources", [])],
            techs=[Technology.from_dict(t) for t in data.get("techs", [])],
            terrains=[Terrain.from_dict(t) for t in data.get("terrains", [])],
            unit_types={k: UnitType.from_dict(v) for k, v in unit_types_data.items()},
            template_id=data.get("template_id"),
        )
    

    # methods getters to access world data by ID or name

    def get_name(self) -> str:
        """Obtiene el nombre del mundo"""
        return self.name

    def get_building(self, building_id: str) -> BuildingType | None:
        """Obtiene un tipo de edificio por su ID"""
        return self.buildings.get(building_id)

    def get_casus_belli_type(self, cb_id: str) -> CasusBelli | None:
        """Obtiene un tipo de casus belli por su ID"""
        return next((cb for cb in self.casus_belli_types if cb.id == cb_id), None)

    def get_factory_type(self, factory_type_id: str) -> FactoryType | None:
        """Obtiene un tipo de fábrica por su ID"""
        return self.factory_types.get(factory_type_id)

    def get_government(self, government_id: str) -> Government | None:
        """Obtiene un tipo de gobierno por su ID"""
        return next((g for g in self.governments if g.id == government_id), None)

    def get_modifier(self, modifier_id: str) -> Modifier | None:
        """Obtiene un modificador por su ID"""
        return next((m for m in self.modifiers if m.id == modifier_id), None)

    def get_province(self, province_id: str) -> Province | None:
        """Obtiene una provincia por su ID"""
        return next((p for p in self.provinces if p.id == province_id), None)

    def get_resource(self, resource_id: str) -> Resource | None:
        """Obtiene un tipo de recurso por su ID"""
        return next((r for r in self.resources if r.id == resource_id), None)

    def get_tech(self, tech_id: str) -> Technology | None:
        """Obtiene un tipo de tecnología por su ID"""
        return next((t for t in self.techs if t.id == tech_id), None)

    def get_terrain(self, terrain_id: str) -> Terrain | None:
        """Obtiene un tipo de terreno por su ID"""
        return next((t for t in self.terrains if t.id == terrain_id), None)

    def get_unit_type(self, unit_type_id: str) -> UnitType | None:
        """Obtiene un tipo de unidad por su ID"""
        return self.unit_types.get(unit_type_id)

    def get_template_id(self) -> str | None:
        """Obtiene el ID de plantilla base, si existe"""
        return self.template_id
    
    # add methods to add new elements to the world definition

    def add_building(self, building: BuildingType) -> None:
        """Agrega un nuevo tipo de edificio al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.buildings[building.id] = building

    def add_casus_belli_type(self, cb_type: CasusBelli) -> None:
        """Agrega un nuevo tipo de casus belli al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.casus_belli_types.append(cb_type)

    def add_factory_type(self, factory_type: FactoryType) -> None:
        """Agrega un nuevo tipo de fábrica al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.factory_types[factory_type.id] = factory_type

    def add_government(self, government: Government) -> None:
        """Agrega un nuevo tipo de gobierno al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.governments.append(government)

    def add_modifier(self, modifier: Modifier) -> None:
        """Agrega un nuevo modificador al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.modifiers.append(modifier)

    def add_province(self, province: Province) -> None:
        """Agrega una nueva provincia al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.provinces.append(province)

    def add_resource(self, resource: Resource) -> None:
        """Agrega un nuevo tipo de recurso al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.resources.append(resource)

    def add_tech(self, tech: Technology) -> None:
        """Agrega una nueva tecnología al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.techs.append(tech)

    def add_terrain(self, terrain: Terrain) -> None:
        """Agrega un nuevo tipo de terreno al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.terrains.append(terrain)

    def add_unit_type(self, unit_type: UnitType) -> None:
        """Agrega un nuevo tipo de unidad al mundo (solo en DRAFT)"""
        self.assert_editable()
        self.unit_types[unit_type.id] = unit_type

    # remove methods to modify existing elements (only in DRAFT)

    def remove_building(self, building_id: str) -> None:
        """Elimina un tipo de edificio del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.buildings.pop(building_id, None)

    def remove_casus_belli_type(self, cb_id: str) -> None:
        """Elimina un tipo de casus belli del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.casus_belli_types = [cb for cb in self.casus_belli_types if cb.id != cb_id]

    def remove_factory_type(self, factory_type_id: str) -> None:
        """Elimina un tipo de fábrica del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.factory_types.pop(factory_type_id, None)

    def remove_government(self, government_id: str) -> None:
        """Elimina un tipo de gobierno del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.governments = [g for g in self.governments if g.id != government_id]

    def remove_modifier(self, modifier_id: str) -> None:
        """Elimina un modificador del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.modifiers = [m for m in self.modifiers if m.id != modifier_id]

    def remove_province(self, province_id: str) -> None:
        """Elimina una provincia del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.provinces = [p for p in self.provinces if p.id != province_id]

    def remove_resource(self, resource_id: str) -> None:
        """Elimina un tipo de recurso del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.resources = [r for r in self.resources if r.id != resource_id]

    def remove_tech(self, tech_id: str) -> None:
        """Elimina un tipo de tecnología del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.techs = [t for t in self.techs if t.id != tech_id]

    def remove_terrain(self, terrain_id: str) -> None:
        """Elimina un tipo de terreno del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.terrains = [t for t in self.terrains if t.id != terrain_id]

    def remove_unit_type(self, unit_type_id: str) -> None:
        """Elimina un tipo de unidad del mundo por su ID (solo en DRAFT)"""
        self.assert_editable()
        self.unit_types.pop(unit_type_id, None)

    # validity checks for world definition

    def has_building(self, building_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de edificio con el ID dado"""
        return building_id in self.buildings

    def has_casus_belli_type(self, cb_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de casus belli con el ID dado"""
        return any(cb.id == cb_id for cb in self.casus_belli_types)

    def has_factory_type(self, factory_type_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de fábrica con el ID dado"""
        return factory_type_id in self.factory_types

    def has_government(self, government_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de gobierno con el ID dado"""
        return any(g.id == government_id for g in self.governments)

    def has_modifier(self, modifier_id: str) -> bool:
        """Verifica si el mundo tiene un modificador con el ID dado"""
        return any(m.id == modifier_id for m in self.modifiers)

    def has_province(self, province_id: str) -> bool:
        """Verifica si el mundo tiene una provincia con el ID dado"""
        return any(p.id == province_id for p in self.provinces)

    def has_resource(self, resource_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de recurso con el ID dado"""
        return any(r.id == resource_id for r in self.resources)

    def has_tech(self, tech_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de tecnología con el ID dado"""
        return any(t.id == tech_id for t in self.techs)

    def has_terrain(self, terrain_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de terreno con el ID dado"""
        return any(t.id == terrain_id for t in self.terrains)

    def has_unit_type(self, unit_type_id: str) -> bool:
        """Verifica si el mundo tiene un tipo de unidad con el ID dado"""
        return unit_type_id in self.unit_types

    #list methods to get all elements of a certain type

    def list_buildings(self) -> list[BuildingType]:
        """Retorna la lista de tipos de edificios del mundo"""
        return list(self.buildings.values())

    def list_casus_belli_types(self) -> list[CasusBelli]:
        """Retorna la lista de tipos de casus belli del mundo"""
        return self.casus_belli_types

    def list_factory_types(self) -> list[FactoryType]:
        """Retorna la lista de tipos de fábricas del mundo"""
        return list(self.factory_types.values())

    def list_governments(self) -> list[Government]:
        """Retorna la lista de tipos de gobiernos del mundo"""
        return self.governments

    def list_modifiers(self) -> list[Modifier]:
        """Retorna la lista de modificadores del mundo"""
        return self.modifiers

    def list_provinces(self) -> list[Province]:
        """Retorna la lista de provincias del mundo"""
        return self.provinces

    def list_resources(self) -> list[Resource]:
        """Retorna la lista de tipos de recursos del mundo"""
        return self.resources

    def list_techs(self) -> list[Technology]:
        """Retorna la lista de tipos de tecnologías del mundo"""
        return self.techs

    def list_terrains(self) -> list[Terrain]:
        """Retorna la lista de tipos de terrenos del mundo"""
        return self.terrains

    def list_unit_types(self) -> list[UnitType]:
        """Retorna la lista de tipos de unidades del mundo"""
        return list(self.unit_types.values())

    # World state management

    def get_state(self) -> WorldState:
        """Obtiene el estado actual del mundo"""
        return self.state
    
    def is_draft(self) -> bool:
        """Verifica si el mundo está en estado DRAFT"""
        return self.state == WorldState.DRAFT
    
    def is_ready(self) -> bool:
        """Verifica si el mundo está READY para jugar"""
        return self.state == WorldState.READY
    
    def is_playable(self) -> bool:
        """Verifica si el mundo es jugable (RUNNING o PAUSED)"""
        return self.state.is_playable()
    
    def is_active(self) -> bool:
        """Verifica si el juego está corriendo activamente"""
        return self.state.is_active()
    
    def is_editable(self) -> bool:
        """Verifica si el mundo puede ser editado"""
        return self.state.is_editable()
    
    def transition_to_ready(self) -> None:
        """Transiciona de DRAFT a READY (congelación de definiciones)"""
        if self.state != WorldState.DRAFT:
            raise ValueError(f"Cannot transition to READY from {self.state.value}")
        self.state = WorldState.READY
    
    def transition_to_running(self) -> None:
        """Transiciona a RUNNING (inicia gameloop)"""
        if self.state not in (WorldState.READY, WorldState.PAUSED):
            raise ValueError(f"Cannot transition to RUNNING from {self.state.value}")
        self.state = WorldState.RUNNING
    
    def transition_to_paused(self) -> None:
        """Transiciona a PAUSED (pausa el juego temporalmente)"""
        if self.state != WorldState.RUNNING:
            raise ValueError(f"Cannot transition to PAUSED from {self.state.value}")
        self.state = WorldState.PAUSED
    
    def transition_to_finished(self) -> None:
        """Transiciona a FINISHED (juego terminó)"""
        if self.state not in (WorldState.RUNNING, WorldState.PAUSED):
            raise ValueError(f"Cannot transition to FINISHED from {self.state.value}")
        self.state = WorldState.FINISHED
    
    def transition_to_archived(self) -> None:
        """Transiciona a ARCHIVED (permanente, solo lectura)"""
        if self.state != WorldState.FINISHED:
            raise ValueError(f"Cannot transition to ARCHIVED from {self.state.value}")
        self.state = WorldState.ARCHIVED
    
    def can_edit(self) -> bool:
        """Verifica si se pueden hacer cambios a definiciones"""
        return self.state == WorldState.DRAFT
    
    def assert_editable(self) -> None:
        """Lanza excepción si no es editable"""
        if not self.can_edit():
            raise ValueError(f"World is not editable (current state: {self.state.value})")
