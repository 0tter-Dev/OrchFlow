"""Application service for authenticated user web preferences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orchflow.application.access_control import AccessControlService
from orchflow.domain.user_preferences import (
    DEFAULT_LOCALE,
    DEFAULT_PROJECT_VIEW_MODE,
    DEFAULT_STATUS_REFRESH_INTERVAL_SECONDS,
    MAX_STATUS_REFRESH_INTERVAL_SECONDS,
    MIN_STATUS_REFRESH_INTERVAL_SECONDS,
    ProjectViewMode,
    UserLocale,
    UserPreferences,
)


class UserPreferencesError(Exception):
    """Raised when user preference inputs are invalid."""


@dataclass(frozen=True, slots=True)
class UpdateUserPreferencesCommand:
    """Partial update for the authenticated user's persisted preferences."""

    token: str
    locale: UserLocale | None = None
    project_view_mode: ProjectViewMode | None = None
    status_refresh_interval_seconds: int | None = None


class UserPreferencesRepository(Protocol):
    """Repository boundary for user-owned interface preferences."""

    def get_preferences_by_user_id(self, user_id: int) -> UserPreferences | None: ...

    def upsert_preferences(self, preferences: UserPreferences) -> UserPreferences: ...

    def record_audit_event(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None: ...


class UserPreferencesService:
    """Manage preferences for authenticated users."""

    def __init__(
        self,
        repository: UserPreferencesRepository,
        access_control_service: AccessControlService,
    ) -> None:
        self._repository = repository
        self._access_control_service = access_control_service

    def get_preferences(self, token: str) -> UserPreferences:
        """Return persisted preferences or default values for the current user."""
        user = self._access_control_service.get_current_user(token)
        existing_preferences = self._repository.get_preferences_by_user_id(user.id)
        if existing_preferences is not None:
            return existing_preferences
        return self._default_preferences_for_user(user.id)

    def update_preferences(self, command: UpdateUserPreferencesCommand) -> UserPreferences:
        """Persist a partial preference update for the current user."""
        user = self._access_control_service.get_current_user(command.token)
        current_preferences = (
            self._repository.get_preferences_by_user_id(user.id)
            or self._default_preferences_for_user(user.id)
        )
        next_preferences = UserPreferences(
            user_id=user.id,
            locale=command.locale or current_preferences.locale,
            project_view_mode=command.project_view_mode or current_preferences.project_view_mode,
            status_refresh_interval_seconds=(
                command.status_refresh_interval_seconds
                if command.status_refresh_interval_seconds is not None
                else current_preferences.status_refresh_interval_seconds
            ),
        )
        self._validate_preferences(next_preferences)
        updated_preferences = self._repository.upsert_preferences(next_preferences)
        details = self._build_change_details(current_preferences, updated_preferences)
        if details:
            self._repository.record_audit_event(
                actor_user_id=user.id,
                action="user.preferences.update",
                target_type="user_preferences",
                target_id=str(user.id),
                details=details,
            )
        return updated_preferences

    @staticmethod
    def _default_preferences_for_user(user_id: int) -> UserPreferences:
        return UserPreferences(
            user_id=user_id,
            locale=DEFAULT_LOCALE,
            project_view_mode=DEFAULT_PROJECT_VIEW_MODE,
            status_refresh_interval_seconds=DEFAULT_STATUS_REFRESH_INTERVAL_SECONDS,
        )

    @staticmethod
    def _validate_preferences(preferences: UserPreferences) -> None:
        interval = preferences.status_refresh_interval_seconds
        if (
            interval < MIN_STATUS_REFRESH_INTERVAL_SECONDS
            or interval > MAX_STATUS_REFRESH_INTERVAL_SECONDS
        ):
            raise UserPreferencesError(
                "status_refresh_interval_seconds must be between "
                f"{MIN_STATUS_REFRESH_INTERVAL_SECONDS} and "
                f"{MAX_STATUS_REFRESH_INTERVAL_SECONDS}."
            )

    @staticmethod
    def _build_change_details(
        previous: UserPreferences,
        current: UserPreferences,
    ) -> str | None:
        changes: list[str] = []
        if previous.locale is not current.locale:
            changes.append(f"locale:{previous.locale.value}->{current.locale.value}")
        if previous.project_view_mode is not current.project_view_mode:
            changes.append(
                "project_view_mode:"
                f"{previous.project_view_mode.value}->{current.project_view_mode.value}"
            )
        if (
            previous.status_refresh_interval_seconds
            != current.status_refresh_interval_seconds
        ):
            changes.append(
                "status_refresh_interval_seconds:"
                f"{previous.status_refresh_interval_seconds}->"
                f"{current.status_refresh_interval_seconds}"
            )
        return ";".join(changes) if changes else None
