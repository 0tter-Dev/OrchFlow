"""Domain objects for user-owned interface preferences."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class UserLocale(StrEnum):
    """Supported interface locale preferences."""

    PT_BR = "pt-BR"
    EN_US = "en-US"


class ProjectViewMode(StrEnum):
    """Supported project list display preferences."""

    LIST = "list"
    TABLE = "table"


DEFAULT_LOCALE = UserLocale.PT_BR
DEFAULT_PROJECT_VIEW_MODE = ProjectViewMode.LIST
DEFAULT_STATUS_REFRESH_INTERVAL_SECONDS = 30
MIN_STATUS_REFRESH_INTERVAL_SECONDS = 10
MAX_STATUS_REFRESH_INTERVAL_SECONDS = 300


@dataclass(frozen=True, slots=True)
class UserPreferences:
    """Persisted preferences for an authenticated OrchFlow user."""

    user_id: int
    locale: UserLocale
    project_view_mode: ProjectViewMode
    status_refresh_interval_seconds: int
