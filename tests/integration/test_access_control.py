"""Integration tests for access control."""

from __future__ import annotations

from sqlalchemy import text

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.services import create_access_control_service
from orchflow.infrastructure.config.settings import get_settings
from orchflow.infrastructure.persistence.session import create_engine_from_settings


def test_first_registered_user_becomes_admin(isolated_environment: None) -> None:
    service = create_access_control_service()

    user = service.register_user(RegisterUserCommand(username="bootstrap", password="password123"))

    assert user.role.value == "admin"


def test_login_records_audit_event(isolated_environment: None) -> None:
    service = create_access_control_service()
    service.register_user(RegisterUserCommand(username="bootstrap", password="password123"))

    token = service.login(LoginCommand(username="bootstrap", password="password123"))
    assert token.token_type == "bearer"

    engine = create_engine_from_settings(get_settings())
    try:
        with engine.connect() as connection:
            audit_count = connection.execute(
                text("SELECT COUNT(*) FROM audit_events WHERE action = 'user.login'")
            ).scalar_one()
    finally:
        engine.dispose()

    assert audit_count == 1
