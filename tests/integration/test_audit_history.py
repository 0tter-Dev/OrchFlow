"""Integration tests for audit history visibility."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from orchflow.application.access_control import (
    AuthorizationError,
    LoginCommand,
    RegisterUserCommand,
)
from orchflow.application.audit_history import (
    AuditEventFilters,
    AuditHistoryValidationError,
    ListAuditEventsCommand,
)
from orchflow.application.project_registry import RegisterProjectCommand
from orchflow.application.services import (
    create_access_control_service,
    create_audit_history_service,
    create_project_registry_service,
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


def test_admin_can_filter_audit_events(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    access_control_service.register_user(
        RegisterUserCommand(username="filter-admin", password="password123")
    )
    admin_token = access_control_service.login(
        LoginCommand(username="filter-admin", password="password123")
    )
    start_time = datetime.now(UTC) - timedelta(seconds=1)

    project_dir = tmp_path / "filter-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    project_registry_service = create_project_registry_service()
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=admin_token.access_token,
            reference_name="filter-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )
    end_time = datetime.now(UTC) + timedelta(seconds=1)

    audit_history_service = create_audit_history_service()

    project_events = audit_history_service.list_recent_events(
        ListAuditEventsCommand(
            token=admin_token.access_token,
            limit=10,
            filters=AuditEventFilters(project_id=project.id),
        )
    )
    assert {event.target_id for event in project_events} == {str(project.id)}

    action_events = audit_history_service.list_recent_events(
        ListAuditEventsCommand(
            token=admin_token.access_token,
            limit=10,
            filters=AuditEventFilters(action="project.register"),
        )
    )
    assert {event.action for event in action_events} == {"project.register"}

    actor_events = audit_history_service.list_recent_events(
        ListAuditEventsCommand(
            token=admin_token.access_token,
            limit=10,
            filters=AuditEventFilters(actor_user_id=project.created_by_user_id),
        )
    )
    assert actor_events
    assert {event.actor_user_id for event in actor_events} == {project.created_by_user_id}

    window_events = audit_history_service.list_recent_events(
        ListAuditEventsCommand(
            token=admin_token.access_token,
            limit=10,
            filters=AuditEventFilters(created_from=start_time, created_to=end_time),
        )
    )
    assert window_events
    assert all(start_time <= event.created_at <= end_time for event in window_events)


def test_audit_history_rejects_inverted_time_window(isolated_environment: None) -> None:
    access_control_service = create_access_control_service()
    access_control_service.register_user(
        RegisterUserCommand(username="range-admin", password="password123")
    )
    admin_token = access_control_service.login(
        LoginCommand(username="range-admin", password="password123")
    )

    audit_history_service = create_audit_history_service()
    now = datetime.now(UTC)

    with pytest.raises(AuditHistoryValidationError, match="start time"):
        audit_history_service.list_recent_events(
            ListAuditEventsCommand(
                token=admin_token.access_token,
                filters=AuditEventFilters(
                    created_from=now + timedelta(minutes=1),
                    created_to=now,
                ),
            )
        )
