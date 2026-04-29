from __future__ import annotations

from typing import TYPE_CHECKING

from model.entities.state.factory import Factory

if TYPE_CHECKING:
    from model.entities.state.building_project import BuildingProject
    from model.entities.state.game_state import GameState


class ConstructionProcessor:
    """Advances active BuildingProject instances each simulation tick."""

    def process(self, game_state: GameState) -> list[dict]:
        events: list[dict] = []

        for project in list(game_state.building_projects):
            if not project.is_active():
                continue

            building = game_state.get_building_state(project.building_id)
            if not building:
                project.cancel()
                event_data = self._event_data(project)
                game_state.log_event("BUILD_CANCELLED", event_data)
                events.append({"type": "BUILD_CANCELLED", **event_data})
                continue

            project.advance(1)
            building.construction_progress = project.progress

            if project.is_completed():
                events.extend(self._complete_project(game_state, project))

        return events

    def _complete_project(self, game_state: GameState, project: BuildingProject) -> list[dict]:
        events: list[dict] = []
        building = game_state.get_building_state(project.building_id)
        province = game_state.get_province_state(project.province_id)

        if not building:
            return events

        building.complete_construction()
        if province:
            province.set_building_level(building.building_type_id, building.level)

        factory_id = None
        factory_type_id = project.factory_type_id or building.factory_type_id
        if factory_type_id:
            project.factory_type_id = factory_type_id
            building.factory_type_id = factory_type_id
            factory_id = self._ensure_factory(game_state, project, building.level)
            if province and factory_id not in province.factories:
                province.factories.append(factory_id)

        event_data = self._event_data(project)
        event_data["factory_id"] = factory_id
        game_state.log_event("BUILD_COMPLETED", event_data)
        events.append({"type": "BUILD_COMPLETED", **event_data})

        return events

    def _ensure_factory(self, game_state: GameState, project: BuildingProject, level: int) -> str:
        factory_id = project.building_id
        existing = next((factory for factory in game_state.factories if factory.id == factory_id), None)
        if existing:
            existing.active = True
            existing.construction_progress = 100
            existing.level = max(existing.level, level)
            return existing.id

        game_state.factories.append(
            Factory(
                id=factory_id,
                factory_type_id=project.factory_type_id or "",
                country_tag=project.country_tag,
                province_id=project.province_id,
                level=level,
                active=True,
                construction_progress=100,
            )
        )
        return factory_id

    def _event_data(self, project: BuildingProject) -> dict:
        return {
            "project_id": project.id,
            "country_tag": project.country_tag,
            "province_id": project.province_id,
            "building_id": project.building_id,
            "building_type_id": project.building_type_id,
            "progress": project.progress,
            "elapsed_ticks": project.elapsed_ticks,
            "duration_ticks": project.duration_ticks,
            "factory_type_id": project.factory_type_id,
        }
