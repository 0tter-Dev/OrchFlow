"""Lifecycle orchestration domain contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from orchflow.domain.project_registry import CanonicalLifecycleAction
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot


@dataclass(frozen=True, slots=True)
class LifecycleExecutionResult:
    """Result of a lifecycle action execution."""

    project_id: int
    canonical_action: CanonicalLifecycleAction
    command_identifier: str
    exit_code: int
    stdout: str
    stderr: str
    succeeded: bool
    started_at: datetime
    finished_at: datetime
    runtime_snapshot: RuntimeInspectionSnapshot | None = None
