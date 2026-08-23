"""Runtime inspection domain contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RuntimeProcessSnapshot:
    """Operator-friendly process details for a managed project."""

    pid: int
    name: str
    cpu_seconds: float | None
    memory_bytes: int | None
    started_at: datetime | None


@dataclass(frozen=True, slots=True)
class RuntimeInspectionSnapshot:
    """Runtime inspection result for a managed project."""

    project_id: int
    status: str
    known_port: int | None
    application_url: str | None
    uptime_seconds: float | None
    process_snapshots: tuple[RuntimeProcessSnapshot, ...]
    inspected_at: datetime
