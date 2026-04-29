import unittest

from loaders.game_loader import GameLoader
from model.entities.state.factory import Factory
from simulation import Order, OrderResult, OrderType, SimulationEngine
from simulation.simple_simulation import SimpleSimulation


TEMPLATE_NAME = "victoria2"
SCENARIO_NAME = "1836"


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

        province.rgo_workers = 10
        coal_before = england.stockpile.get_amount("coal")

        events, _ = self.engine.tick_forward(game_state)

        self.assertAlmostEqual(england.stockpile.get_amount("coal"), coal_before + 1.0)
        self.assertIn("RGO_PRODUCED", event_types(events))

    def test_economy_processor_runs_active_factory_when_inputs_are_available(self):
        game_state = load_game()
        prussia = game_state.get_country_state("PRU")

        self.assertIsNotNone(prussia)

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
        self.assertEqual(factory.last_production_tick, 1)
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
        english_money_before = england.money
        relation_eng_to_fra_before = england.get_relation("FRA")
        relation_fra_to_eng_before = france.get_relation("ENG")

        orders = [
            Order(OrderType.RESEARCH, "FRA", {"tech_id": "military_science"}),
            Order(OrderType.BUILD, "ENG", {"building_type_id": "factory", "province_id": "1"}),
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
        self.assertFalse(game_state.buildings[-1].active)
        self.assertEqual(england.money, english_money_before - 5000)
        self.assertEqual(army.province_id, "2")
        self.assertEqual(england.get_relation("FRA"), relation_eng_to_fra_before + 12)
        self.assertEqual(france.get_relation("ENG"), relation_fra_to_eng_before + 6)

        emitted = event_types(events)
        self.assertIn("TECH_RESEARCHED", emitted)
        self.assertIn("BUILD_STARTED", emitted)
        self.assertIn("ARMY_MOVED", emitted)
        self.assertIn("DIPLOMACY_ACTION", emitted)

    def test_order_pipeline_rejects_invalid_orders_without_mutating_state(self):
        game_state = load_game()
        england = game_state.get_country_state("ENG")
        army = game_state.get_army_state("1")

        self.assertIsNotNone(england)
        self.assertIsNotNone(army)

        money_before = england.money
        building_count_before = len(game_state.buildings)
        army_province_before = army.province_id
        relation_before = england.get_relation("FRA")

        orders = [
            Order(OrderType.RESEARCH, "ENG", {"tech_id": "coal_power"}),
            Order(OrderType.BUILD, "ENG", {"building_type_id": "factory", "province_id": "2"}),
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
