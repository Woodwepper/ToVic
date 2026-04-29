from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.entities.state.country_state import CountryState
    from model.entities.state.factory import Factory
    from model.entities.state.game_state import GameState
    from model.entities.state.province_state import ProvinceState


_POPULATION_PER_WORKER = 100_000


class LaborAllocationProcessor:
    """Assigns workers automatically to factories and RGOs before production."""

    def process(self, game_state: GameState) -> list[dict]:
        events: list[dict] = []

        for province in game_state.provinces:
            province.rgo_workers = 0
        for factory in game_state.factories:
            factory.current_workers = 0

        world_provinces = {province.id: province for province in game_state.world.provinces}

        for country in game_state.countries:
            available = self._available_workers(country)
            country.workers_pool = available

            factories = [
                factory
                for factory in game_state.factories
                if factory.country_tag == country.tag and factory.active
            ]
            rgo_provinces = [
                province
                for province in game_state.provinces
                if province.owner_tag == country.tag
                and world_provinces.get(province.id)
                and world_provinces[province.id].resource_id
            ]

            factory_workers = self._assign_factories(game_state, country, factories, available)
            available -= factory_workers
            rgo_workers = self._assign_rgos(rgo_provinces, available)
            available -= rgo_workers

            if factory_workers or rgo_workers:
                event_data = {
                    "country_tag": country.tag,
                    "factory_workers": factory_workers,
                    "rgo_workers": rgo_workers,
                    "unassigned_workers": max(0, available),
                }
                game_state.log_event("LABOR_ALLOCATED", event_data)
                events.append({"type": "LABOR_ALLOCATED", **event_data})

        return events

    def _available_workers(self, country: CountryState) -> int:
        derived_workers = max(0, int(country.population // _POPULATION_PER_WORKER))
        return max(0, country.workers_pool or derived_workers)

    def _assign_factories(
        self,
        game_state: GameState,
        country: CountryState,
        factories: list[Factory],
        available_workers: int,
    ) -> int:
        assigned = 0

        def can_run(factory: Factory) -> bool:
            factory_type = game_state.world.factory_types.get(factory.factory_type_id)
            if not factory_type:
                return False
            scale = max(1, factory.level)
            return all(
                country.stockpile.has_enough(resource_id, amount * scale)
                for resource_id, amount in factory_type.input_goods.items()
            )

        for factory in sorted(factories, key=lambda item: (not can_run(item), item.id)):
            if available_workers <= 0:
                break

            factory_type = game_state.world.factory_types.get(factory.factory_type_id)
            if not factory_type or not can_run(factory):
                continue

            needed = max(0, int(factory_type.needed_workers * max(1, factory.level)))
            workers = min(available_workers, needed)
            factory.current_workers = workers
            assigned += workers
            available_workers -= workers

        return assigned

    def _assign_rgos(self, provinces: list[ProvinceState], available_workers: int) -> int:
        assigned = 0
        for province in sorted(provinces, key=lambda item: item.id):
            if available_workers <= 0:
                break

            capacity = max(1, int(province.population // _POPULATION_PER_WORKER))
            workers = min(available_workers, capacity)
            province.rgo_workers = workers
            assigned += workers
            available_workers -= workers

        return assigned
