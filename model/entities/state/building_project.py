from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BuildingProject:
    """Runtime construction project stored in GameState."""

    id: str
    country_tag: str
    province_id: str
    building_type_id: str
    building_id: str
    started_tick: int
    duration_ticks: int
    elapsed_ticks: int = 0
    progress: int = 0
    status: str = "active"
    factory_type_id: Optional[str] = None

    def is_active(self) -> bool:
        return self.status == "active"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def is_cancelled(self) -> bool:
        return self.status == "cancelled"

    def advance(self, ticks: int = 1) -> None:
        """Advance project progress by a number of simulation ticks."""
        if not self.is_active():
            return

        self.elapsed_ticks += max(0, ticks)
        if self.duration_ticks <= 0:
            self.progress = 100
        else:
            self.progress = min(100, int((self.elapsed_ticks / self.duration_ticks) * 100))

        if self.progress >= 100:
            self.complete()

    def complete(self) -> None:
        self.elapsed_ticks = max(self.elapsed_ticks, self.duration_ticks)
        self.progress = 100
        self.status = "completed"

    def cancel(self) -> None:
        if self.status == "completed":
            return
        self.status = "cancelled"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "country_tag": self.country_tag,
            "province_id": self.province_id,
            "building_type_id": self.building_type_id,
            "building_id": self.building_id,
            "started_tick": self.started_tick,
            "duration_ticks": self.duration_ticks,
            "elapsed_ticks": self.elapsed_ticks,
            "progress": self.progress,
            "status": self.status,
            "factory_type_id": self.factory_type_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BuildingProject":
        return cls(
            id=str(data["id"]),
            country_tag=data["country_tag"],
            province_id=str(data["province_id"]),
            building_type_id=data["building_type_id"],
            building_id=str(data["building_id"]),
            started_tick=int(data["started_tick"]),
            duration_ticks=int(data["duration_ticks"]),
            elapsed_ticks=int(data.get("elapsed_ticks", 0)),
            progress=int(data.get("progress", 0)),
            status=data.get("status", "active"),
            factory_type_id=data.get("factory_type_id"),
        )
