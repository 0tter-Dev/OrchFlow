"""Integration tests for lifecycle orchestration."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.lifecycle import ExecuteLifecycleCommand
from orchflow.application.project_registry import RegisterProjectCommand
from orchflow.application.services import (
    create_access_control_service,
    create_lifecycle_orchestration_service,
    create_project_registry_service,
)
from orchflow.domain.project_registry import CanonicalLifecycleAction

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only batch execution")


def _write_dispatch_batch(path: Path) -> None:
    path.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" goto STATUS\r\n"
        "if /I \"%~1\"==\"START\" goto START\r\n"
        "if /I \"%~1\"==\"STOP\" goto STOP\r\n"
        "if /I \"%~1\"==\"RESTART\" goto RESTART\r\n"
        "echo unknown-action\r\n"
        "exit /b 1\r\n"
        ":STATUS\r\n"
        "echo status-ok\r\n"
        "exit /b 0\r\n"
        ":START\r\n"
        "echo started-ok\r\n"
        "exit /b 0\r\n"
        ":STOP\r\n"
        "echo stopped-ok\r\n"
        "exit /b 0\r\n"
        ":RESTART\r\n"
        "echo restarted-ok\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )


def test_lifecycle_execution_supports_all_canonical_actions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    lifecycle_service = create_lifecycle_orchestration_service()

    access_control_service.register_user(
        RegisterUserCommand(username="lifecycle-admin", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="lifecycle-admin", password="password123")
    ).access_token

    project_dir = tmp_path / "lifecycle-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script)

    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="lifecycle-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    expected_outputs = {
        CanonicalLifecycleAction.STATUS: "status-ok",
        CanonicalLifecycleAction.START: "started-ok",
        CanonicalLifecycleAction.STOP: "stopped-ok",
        CanonicalLifecycleAction.RESTART: "restarted-ok",
    }
    for action, expected_output in expected_outputs.items():
        result = lifecycle_service.execute_action(
            ExecuteLifecycleCommand(
                token=token,
                project_id=project.id,
                action=action,
            )
        )
        assert result.succeeded is True
        assert result.command_identifier == action.value.upper()
        assert expected_output in result.stdout
