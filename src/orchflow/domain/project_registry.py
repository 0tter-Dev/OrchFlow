"""Project registry domain contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class CanonicalLifecycleAction(StrEnum):
    """Canonical lifecycle actions used internally by OrchFlow."""

    STATUS = "status"
    START = "start"
    STOP = "stop"
    RESTART = "restart"


class MappingSource(StrEnum):
    """Supported sources for lifecycle action mappings."""

    USER_DEFINED = "user_defined"
    IMPORTED = "imported"
    AI_APPROVED = "ai_approved"


@dataclass(frozen=True, slots=True)
class LifecycleActionMapping:
    """Persisted canonical-to-script action mapping."""

    id: int
    project_id: int
    canonical_action: CanonicalLifecycleAction
    script_label: str
    source: MappingSource
    configured_by_user_id: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class Project:
    """Persisted OrchFlow project definition."""

    id: int
    reference_name: str
    description: str | None
    project_root_path: str
    lifecycle_script_path: str
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    owner_user_ids: tuple[int, ...]
    action_mappings: tuple[LifecycleActionMapping, ...]
