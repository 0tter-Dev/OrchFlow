"""Integration tests for access control."""

from __future__ import annotations

import pytest
from sqlalchemy import text

from orchflow.application.access_control import (
    AuthorizationError,
    LoginCommand,
    RegisterUserCommand,
    UpdateUserCommand,
)
from orchflow.application.services import create_access_control_service
from orchflow.domain.access_control import UserRole
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


def test_admin_can_update_user_role_and_activation(isolated_environment: None) -> None:
    service = create_access_control_service()
    service.register_user(RegisterUserCommand(username="admin-user", password="password123"))
    member = service.register_user(
        RegisterUserCommand(username="member-user", password="password123")
    )
    token = service.login(LoginCommand(username="admin-user", password="password123"))

    updated_user = service.update_user(
        UpdateUserCommand(
            token=token.access_token,
            user_id=member.id,
            role=UserRole.ADMIN,
            is_active=False,
        )
    )

    assert updated_user.role is UserRole.ADMIN
    assert updated_user.is_active is False


def test_last_active_admin_cannot_be_demoted(isolated_environment: None) -> None:
    service = create_access_control_service()
    admin = service.register_user(
        RegisterUserCommand(username="admin-user", password="password123")
    )
    token = service.login(LoginCommand(username="admin-user", password="password123"))

    with pytest.raises(AuthorizationError, match="At least one active admin"):
        service.update_user(
            UpdateUserCommand(
                token=token.access_token,
                user_id=admin.id,
                role=UserRole.MEMBER,
            )
        )
