"""Integration tests for lifecycle execution gating by configuration state."""

from __future__ import annotations

from pathlib import Path

import pytest

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.lifecycle import (
    ExecuteLifecycleCommand,
    LifecycleActionConfigurationError,
)
from orchflow.application.project_registry import (
    ProjectMappingInput,
    RegisterProjectCommand,
    ReloadProjectCommand,
    UpdateLifecycleFunctionConfigurationCommand,
)
from orchflow.application.services import (
    create_access_control_service,
    create_lifecycle_orchestration_service,
    create_project_registry_service,
)
from orchflow.domain.project_registry import CanonicalLifecycleAction


def _write_batch(path: Path, *identifiers: str) -> None:
    lines = ["@echo off\r\n"]
    for identifier in identifiers:
        lines.append(
            f"if /I \"%~1\"==\"{identifier}\" "
            f"echo {identifier.lower()}-ok & exit /b 0\r\n"
        )
    lines.append("exit /b 1\r\n")
    path.write_text("".join(lines), encoding="utf-8")


def test_lifecycle_execution_rejects_undefined_action(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    lifecycle_service = create_lifecycle_orchestration_service()

    access_control_service.register_user(
        RegisterUserCommand(username="undefined-action-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="undefined-action-user", password="password123")
    ).access_token
    project_dir = tmp_path / "undefined-action-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_batch(lifecycle_script, "STATUS")
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="undefined-action-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    with pytest.raises(LifecycleActionConfigurationError, match="undefined"):
        lifecycle_service.execute_action(
            ExecuteLifecycleCommand(
                token=token,
                project_id=project.id,
                action=CanonicalLifecycleAction.START,
            )
        )


def test_lifecycle_execution_rejects_explicitly_unconfigured_action(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    lifecycle_service = create_lifecycle_orchestration_service()

    access_control_service.register_user(
        RegisterUserCommand(username="unconfigured-action-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="unconfigured-action-user", password="password123")
    ).access_token
    project_dir = tmp_path / "unconfigured-action-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_batch(lifecycle_script, "STATUS", "START")
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="unconfigured-action-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )
    project_registry_service.update_lifecycle_function_configuration(
        UpdateLifecycleFunctionConfigurationCommand(
            token=token,
            project_id=project.id,
            mappings=(
                ProjectMappingInput(
                    canonical_action=CanonicalLifecycleAction.STATUS,
                    script_label="STATUS",
                ),
            ),
            unconfigured_actions=(CanonicalLifecycleAction.START,),
        )
    )

    with pytest.raises(LifecycleActionConfigurationError, match="explicitly marked"):
        lifecycle_service.execute_action(
            ExecuteLifecycleCommand(
                token=token,
                project_id=project.id,
                action=CanonicalLifecycleAction.START,
            )
        )


def test_lifecycle_execution_rejects_blocked_project_after_reload(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    lifecycle_service = create_lifecycle_orchestration_service()

    access_control_service.register_user(
        RegisterUserCommand(username="blocked-execution-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="blocked-execution-user", password="password123")
    ).access_token
    project_dir = tmp_path / "blocked-execution-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_batch(lifecycle_script, "STATUS")
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="blocked-execution-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )
    _write_batch(lifecycle_script, "VERIFY")
    project_registry_service.reload_project(
        ReloadProjectCommand(token=token, project_id=project.id)
    )

    with pytest.raises(LifecycleActionConfigurationError, match="no configured"):
        lifecycle_service.execute_action(
            ExecuteLifecycleCommand(
                token=token,
                project_id=project.id,
                action=CanonicalLifecycleAction.STATUS,
            )
        )
