"""Integration tests for audit history visibility."""

import pytest

from orchflow.application.access_control import (
    AuthorizationError,
    LoginCommand,
    RegisterUserCommand,
)
from orchflow.application.audit_history import ListAuditEventsCommand
from orchflow.application.services import (
    create_access_control_service,
    create_audit_history_service,
)


def test_admin_can_list_recent_audit_events(isolated_environment: None) -> None:
    access_control_service = create_access_control_service()
    access_control_service.register_user(
        RegisterUserCommand(username="audit-admin", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="audit-admin", password="password123")
    )

    audit_history_service = create_audit_history_service()
    events = audit_history_service.list_recent_events(
        ListAuditEventsCommand(token=token.access_token, limit=10)
    )

    assert events[0].action == "admin.audit_events.list"
    assert any(event.action == "user.login" for event in events)
    assert any(event.action == "user.register" for event in events)


def test_member_cannot_list_audit_events(isolated_environment: None) -> None:
    access_control_service = create_access_control_service()
    access_control_service.register_user(
        RegisterUserCommand(username="audit-admin", password="password123")
    )
    access_control_service.register_user(
        RegisterUserCommand(username="audit-member", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="audit-member", password="password123")
    )

    audit_history_service = create_audit_history_service()

    with pytest.raises(AuthorizationError, match="Admin privileges are required"):
        audit_history_service.list_recent_events(
            ListAuditEventsCommand(token=token.access_token, limit=10)
        )
