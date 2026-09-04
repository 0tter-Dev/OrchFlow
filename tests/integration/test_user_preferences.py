"""Integration tests for authenticated user preferences."""

from __future__ import annotations

from sqlalchemy import text

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.services import (
    create_access_control_service,
    create_user_preferences_service,
)
from orchflow.application.user_preferences import UpdateUserPreferencesCommand
from orchflow.domain.user_preferences import ProjectViewMode, UserLocale
from orchflow.infrastructure.config.settings import get_settings
from orchflow.infrastructure.persistence.session import create_engine_from_settings


def test_user_preferences_default_to_web_operator_baseline(
    isolated_environment: None,
) -> None:
    access_control_service = create_access_control_service()
    preferences_service = create_user_preferences_service()
    access_control_service.register_user(
        RegisterUserCommand(username="preferences-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="preferences-user", password="password123")
    )

    preferences = preferences_service.get_preferences(token.access_token)

    assert preferences.locale is UserLocale.PT_BR
    assert preferences.project_view_mode is ProjectViewMode.LIST
    assert preferences.status_refresh_interval_seconds == 30


def test_user_preferences_can_be_updated_partially_and_audited(
    isolated_environment: None,
) -> None:
    access_control_service = create_access_control_service()
    preferences_service = create_user_preferences_service()
    access_control_service.register_user(
        RegisterUserCommand(username="preferences-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="preferences-user", password="password123")
    )

    updated_preferences = preferences_service.update_preferences(
        UpdateUserPreferencesCommand(
            token=token.access_token,
            project_view_mode=ProjectViewMode.TABLE,
            status_refresh_interval_seconds=45,
        )
    )

    assert updated_preferences.locale is UserLocale.PT_BR
    assert updated_preferences.project_view_mode is ProjectViewMode.TABLE
    assert updated_preferences.status_refresh_interval_seconds == 45

    engine = create_engine_from_settings(get_settings())
    try:
        with engine.connect() as connection:
            audit_details = connection.execute(
                text(
                    "SELECT details FROM audit_events "
                    "WHERE action = 'user.preferences.update'"
                )
            ).scalar_one()
    finally:
        engine.dispose()

    assert "project_view_mode:list->table" in audit_details
    assert "status_refresh_interval_seconds:30->45" in audit_details
