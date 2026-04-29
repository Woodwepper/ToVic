import unittest

from loaders.game_loader import GameLoader
from loaders.managers.scenario_loader import ScenarioLoader
from loaders.managers.world_loader import WorldLoader
from loaders.validators.scenario_data_validator import ScenarioDataValidator
from model.entities.state.building_state import BuildingState
from model.entities.state.factory import Factory
from model.entities.state.building_project import BuildingProject
from simulation import Order, OrderResult, OrderType, SimulationEngine
from simulation.simple_simulation import SimpleSimulation


TEMPLATE_NAME = "victoria2"
SCENARIO_NAME = "1836"
TEMPLATE_SCENARIOS = [
    ("victoria2", "1836"),
    ("hoi4", "1936"),
    ("medieval_empires", "1066"),
    ("mars_frontier", "2150"),
]


def load_game():
    """Carga una partida limpia para cada test.

    El loader actual no lee metadata de fecha desde archivos del scenario, asi
    que fijamos el anio esperado por el template 1836 para probar tecnologias.
    """
    game_state = GameLoader.load(TEMPLATE_NAME, SCENARIO_NAME)
    game_state.scenario.year = 1836
    return game_state


def event_types(events):
    return [event["type"] for event in events]


class SimulationEngineTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = SimulationEngine()

    def test_public_simulation_api_exports_engine_orders_and_compat_alias(self):
        self.assertIs(SimpleSimulation, SimulationEngine)

        order = Order(OrderType.RESEARCH, "ENG", {"tech_id": "railroad"})
        result = OrderResult(order=order, accepted=True)

        self.assertEqual(order.type, OrderType.RESEARCH)
        self.assertEqual(order.country_tag, "ENG")
        self.assertEqual(result.events, [])

    def test_game_loader_creates_mutable_game_state(self):
        game_state = load_game()

        self.assertEqual(game_state.scenario.id, SCENARIO_NAME)
        self.assertEqual(game_state.world.template_id, TEMPLATE_NAME)
        self.assertGreaterEqual(len(game_state.countries), 3)
        self.assertGreaterEqual(len(game_state.provinces), 6)
        self.assertGreaterEqual(len(game_state.armies), 4)
        self.assertEqual(game_state.current_tick, 0)

        england = game_state.get_country_state("ENG")
        self.assertIsNotNone(england)
        self.assertIsNot(england, game_state.scenario.get_country("ENG"))

        prussian_factory = next((factory for factory in game_state.factories if factory.id == "bld_5"), None)
        province = game_state.get_province_state("5")
        self.assertIsNotNone(prussian_factory)
        self.assertIsNotNone(province)
        self.assertEqual(prussian_factory.factory_type_id, "steel_factory")
        self.assertIn("bld_5", province.factories)

    def test_templates_load_with_factory_bindings(self):
        for template_name, scenario_name in TEMPLATE_SCENARIOS:
            with self.subTest(template=template_name, scenario=scenario_name):
                game_state = GameLoader.load(template_name, scenario_name)
                factory_buildings = [
                    building
                    for building in game_state.buildings
                    if building.building_type_id == "factory"
                ]

                self.assertTrue(factory_buildings)
                self.assertEqual(len(game_state.factories), len(factory_buildings))
                self.assertTrue(all(building.factory_type_id for building in factory_buildings))

    def test_scenario_validator_requires_valid_factory_type_binding(self):
        world = WorldLoader.load_world(TEMPLATE_NAME)
        scenario = ScenarioLoader.load_scenario_from_file(TEMPLATE_NAME, SCENARIO_NAME)
        factory_building = next(building for building in scenario.buildings if building.building_type_id == "factory")
        factory_building.factory_type_id = None

        errors = ScenarioDataValidator(scenario, world).validate()

        self.assertTrue(any("factory_type_id" in error for error in errors))

    def test_game_state_tracks_and_serializes_building_projects(self):
        game_state = load_game()
        project = BuildingProject(
            id="project_eng_factory_1",
            country_tag="ENG",
            province_id="1",
            building_type_id="factory",
            building_id="building_eng_factory_1",
            started_tick=game_state.current_tick,
            duration_ticks=10,
            factory_type_id="steel_factory",
        )

        game_state.building_projects.append(project)
        project.advance(5)

        self.assertEqual(game_state.get_building_project("project_eng_factory_1"), project)
        self.assertEqual(game_state.list_active_building_projects(), [project])
        self.assertEqual(project.progress, 50)

        restored = game_state.__class__.from_dict(game_state.to_dict())
        restored_project = restored.get_building_project("project_eng_factory_1")

        self.assertIsNotNone(restored_project)
        self.assertEqual(restored_project.progress, 50)
        self.assertEqual(restored_project.factory_type_id, "steel_factory")

    def test_tick_processor_advances_date_expires_casus_belli_and_recovers_armies(self):
        game_state = load_game()
        army = game_state.get_army_state("1")
        casus_belli = game_state.get_casus_belli("cb_eng_vs_fra")

        self.assertIsNotNone(army)
        self.assertIsNotNone(casus_belli)

        army.morale = 0.50
        army.organization = 0.40
        casus_belli.expiration_tick = 1
        casus_belli.active = True

        events, results = self.engine.tick_forward(game_state)

        self.assertEqual(results, [])
        self.assertEqual(game_state.current_tick, 1)
        self.assertEqual(game_state.get_date(), "1836-01-02")
        self.assertAlmostEqual(army.morale, 0.505)
        self.assertAlmostEqual(army.organization, 0.405)
        self.assertFalse(casus_belli.active)
        self.assertIn("TICK_ADVANCED", event_types(events))
        self.assertIn("CB_EXPIRED", event_types(events))
        self.assertEqual(game_state.get_event_statistics()["TICK_ADVANCED"], 1)

    def test_economy_processor_produces_rgo_resources(self):
        game_state = load_game()
        province = game_state.get_province_state("1")
        england = game_state.get_country_state("ENG")

        self.assertIsNotNone(province)
        self.assertIsNotNone(england)

        england.workers_pool = 10
        coal_before = england.stockpile.get_amount("coal")

        events, _ = self.engine.tick_forward(game_state)

        self.assertAlmostEqual(england.stockpile.get_amount("coal"), coal_before + 1.0)
        self.assertEqual(province.rgo_workers, 10)
        self.assertIn("LABOR_ALLOCATED", event_types(events))
        self.assertIn("RGO_PRODUCED", event_types(events))

    def test_economy_processor_runs_active_factory_when_inputs_are_available(self):
        game_state = load_game()
        prussia = game_state.get_country_state("PRU")

        self.assertIsNotNone(prussia)

        game_state.factories = []
        prussia.workers_pool = 200
        prussia.stockpile.set_amount("iron", 100)
        prussia.stockpile.set_amount("coal", 100)
        prussia.stockpile.set_amount("steel", 0)
        factory = Factory(
            id="factory_pru_steel_test",
            factory_type_id="steel_factory",
            country_tag="PRU",
            province_id="5",
            level=1,
            active=True,
            efficiency=1.0,
        )
        game_state.factories.append(factory)

        events, _ = self.engine.tick_forward(game_state)

        self.assertAlmostEqual(prussia.stockpile.get_amount("iron"), 80)
        self.assertAlmostEqual(prussia.stockpile.get_amount("coal"), 85)
        self.assertAlmostEqual(prussia.stockpile.get_amount("steel"), 30)
        self.assertEqual(factory.current_workers, 200)
        self.assertEqual(factory.last_production_tick, 1)
        self.assertIn("LABOR_ALLOCATED", event_types(events))
        self.assertIn("FACTORY_RAN", event_types(events))

    def test_labor_allocation_scales_factory_output_by_available_workers(self):
        game_state = load_game()
        prussia = game_state.get_country_state("PRU")

        self.assertIsNotNone(prussia)

        game_state.factories = []
        prussia.workers_pool = 100
        prussia.stockpile.set_amount("iron", 100)
        prussia.stockpile.set_amount("coal", 100)
        prussia.stockpile.set_amount("steel", 0)
        factory = Factory(
            id="factory_pru_steel_half_staffed",
            factory_type_id="steel_factory",
            country_tag="PRU",
            province_id="5",
            level=1,
            active=True,
            efficiency=1.0,
        )
        game_state.factories.append(factory)

        events, _ = self.engine.tick_forward(game_state)

        self.assertEqual(factory.current_workers, 100)
        self.assertAlmostEqual(prussia.stockpile.get_amount("iron"), 90)
        self.assertAlmostEqual(prussia.stockpile.get_amount("coal"), 92.5)
        self.assertAlmostEqual(prussia.stockpile.get_amount("steel"), 15)
        self.assertIn("FACTORY_RAN", event_types(events))

    def test_economy_processor_does_not_consume_inputs_when_factory_cannot_run(self):
        game_state = load_game()
        prussia = game_state.get_country_state("PRU")

        self.assertIsNotNone(prussia)

        prussia.stockpile.set_amount("iron", 19)
        prussia.stockpile.set_amount("coal", 100)
        prussia.stockpile.set_amount("steel", 0)
        game_state.factories.append(
            Factory(
                id="factory_pru_steel_missing_inputs",
                factory_type_id="steel_factory",
                country_tag="PRU",
                province_id="5",
            )
        )

        events, _ = self.engine.tick_forward(game_state)

        self.assertAlmostEqual(prussia.stockpile.get_amount("iron"), 19)
        self.assertAlmostEqual(prussia.stockpile.get_amount("coal"), 100)
        self.assertAlmostEqual(prussia.stockpile.get_amount("steel"), 0)
        self.assertNotIn("FACTORY_RAN", event_types(events))

    def test_order_pipeline_accepts_all_supported_order_types(self):
        game_state = load_game()
        france = game_state.get_country_state("FRA")
        england = game_state.get_country_state("ENG")
        army = game_state.get_army_state("1")

        self.assertIsNotNone(france)
        self.assertIsNotNone(england)
        self.assertIsNotNone(army)

        building_count_before = len(game_state.buildings)
        project_count_before = len(game_state.building_projects)
        english_money_before = england.money
        relation_eng_to_fra_before = england.get_relation("FRA")
        relation_fra_to_eng_before = france.get_relation("ENG")

        orders = [
            Order(OrderType.RESEARCH, "FRA", {"tech_id": "military_science"}),
            Order(OrderType.BUILD, "ENG", {"building_type_id": "factory", "province_id": "1", "factory_type_id": "steel_factory"}),
            Order(OrderType.ARMY_MOVE, "ENG", {"army_id": "1", "to_province_id": "2"}),
            Order(OrderType.DIPLOMACY, "ENG", {"action": "improve_relations", "target_tag": "FRA", "amount": 12}),
        ]

        for order in orders:
            game_state.submit_order(order)
            self.assertEqual(order.submitted_tick, 0)

        events, results = self.engine.tick_forward(game_state)

        self.assertEqual(len(results), len(orders))
        self.assertTrue(all(result.accepted for result in results))
        self.assertEqual(len(game_state.pending_orders), 0)

        self.assertIn("military_science", france.researched_techs)
        self.assertEqual(len(game_state.buildings), building_count_before + 1)
        self.assertEqual(game_state.buildings[-1].building_type_id, "factory")
        self.assertEqual(game_state.buildings[-1].factory_type_id, "steel_factory")
        self.assertFalse(game_state.buildings[-1].active)
        self.assertEqual(len(game_state.building_projects), project_count_before + 1)
        self.assertEqual(game_state.building_projects[-1].building_id, game_state.buildings[-1].id)
        self.assertEqual(game_state.building_projects[-1].duration_ticks, 1000)
        self.assertTrue(game_state.building_projects[-1].is_active())
        self.assertEqual(england.money, english_money_before - 5000)
        self.assertEqual(army.province_id, "2")
        self.assertEqual(england.get_relation("FRA"), relation_eng_to_fra_before + 12)
        self.assertEqual(france.get_relation("ENG"), relation_fra_to_eng_before + 6)

        emitted = event_types(events)
        self.assertIn("TECH_RESEARCHED", emitted)
        self.assertIn("BUILD_STARTED", emitted)
        self.assertIn("ARMY_MOVED", emitted)
        self.assertIn("DIPLOMACY_ACTION", emitted)

    def test_construction_processor_advances_and_completes_build_projects(self):
        game_state = load_game()
        england = game_state.get_country_state("ENG")
        province = game_state.get_province_state("1")

        self.assertIsNotNone(england)
        self.assertIsNotNone(province)

        game_state.world.buildings["farm"].construction_time = 2
        game_state.submit_order(Order(OrderType.BUILD, "ENG", {"building_type_id": "farm", "province_id": "1"}))

        events, results = self.engine.tick_forward(game_state)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].accepted)
        self.assertIn("BUILD_STARTED", event_types(events))
        self.assertEqual(len(game_state.building_projects), 1)
        project = game_state.building_projects[0]
        building = game_state.get_building_state(project.building_id)

        self.assertIsNotNone(building)
        self.assertFalse(building.active)
        self.assertEqual(project.progress, 0)

        events, _ = self.engine.tick_forward(game_state)

        self.assertEqual(project.progress, 50)
        self.assertEqual(building.construction_progress, 50)
        self.assertTrue(project.is_active())
        self.assertNotIn("BUILD_COMPLETED", event_types(events))

        events, _ = self.engine.tick_forward(game_state)

        self.assertTrue(project.is_completed())
        self.assertTrue(building.active)
        self.assertEqual(building.construction_progress, 100)
        self.assertEqual(province.get_building_level("farm"), 1)
        self.assertIn("BUILD_COMPLETED", event_types(events))

    def test_construction_processor_creates_factory_when_project_has_factory_type(self):
        game_state = load_game()
        province = game_state.get_province_state("5")

        self.assertIsNotNone(province)

        building = BuildingState(
            id="building_pru_steel_project",
            building_type_id="factory",
            province_id="5",
            level=1,
            factory_type_id="steel_factory",
            active=False,
            construction_progress=0,
        )
        project = BuildingProject(
            id="project_pru_steel",
            country_tag="PRU",
            province_id="5",
            building_type_id="factory",
            building_id=building.id,
            started_tick=game_state.current_tick,
            duration_ticks=1,
            factory_type_id="steel_factory",
        )
        game_state.buildings.append(building)
        game_state.building_projects.append(project)

        events, _ = self.engine.tick_forward(game_state)

        factory = next((item for item in game_state.factories if item.id == building.id), None)
        self.assertIsNotNone(factory)
        self.assertEqual(factory.factory_type_id, "steel_factory")
        self.assertTrue(factory.active)
        self.assertIn(factory.id, province.factories)
        self.assertTrue(building.active)
        self.assertTrue(project.is_completed())
        self.assertIn("BUILD_COMPLETED", event_types(events))

    def test_order_pipeline_rejects_invalid_orders_without_mutating_state(self):
        game_state = load_game()
        england = game_state.get_country_state("ENG")
        army = game_state.get_army_state("1")

        self.assertIsNotNone(england)
        self.assertIsNotNone(army)

        money_before = england.money
        building_count_before = len(game_state.buildings)
        project_count_before = len(game_state.building_projects)
        army_province_before = army.province_id
        relation_before = england.get_relation("FRA")

        orders = [
            Order(OrderType.RESEARCH, "ENG", {"tech_id": "coal_power"}),
            Order(OrderType.BUILD, "ENG", {"building_type_id": "factory", "province_id": "2"}),
            Order(OrderType.BUILD, "ENG", {"building_type_id": "farm", "province_id": "1", "factory_type_id": "steel_factory"}),
            Order(OrderType.ARMY_MOVE, "ENG", {"army_id": "1", "to_province_id": "6"}),
            Order(OrderType.DIPLOMACY, "ENG", {"action": "unknown_action", "target_tag": "FRA"}),
        ]
        for order in orders:
            game_state.submit_order(order)

        _, results = self.engine.tick_forward(game_state)

        self.assertEqual(len(results), len(orders))
        self.assertFalse(any(result.accepted for result in results))
        self.assertTrue(all(result.reason for result in results))
        self.assertEqual(england.money, money_before)
        self.assertEqual(len(game_state.buildings), building_count_before)
        self.assertEqual(len(game_state.building_projects), project_count_before)
        self.assertEqual(army.province_id, army_province_before)
        self.assertEqual(england.get_relation("FRA"), relation_before)
        self.assertEqual(len(game_state.pending_orders), 0)

    def test_run_executes_multiple_ticks_and_aggregates_events(self):
        game_state = load_game()

        events, results = self.engine.run(game_state, ticks=3)

        self.assertEqual(results, [])
        self.assertEqual(game_state.current_tick, 3)
        self.assertEqual(event_types(events).count("TICK_ADVANCED"), 3)
        self.assertEqual(game_state.get_event_statistics()["TICK_ADVANCED"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
