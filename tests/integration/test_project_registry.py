"""Integration tests for project registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.project_registry import (
    ProjectMappingInput,
    ProjectValidationError,
    RegisterProjectCommand,
)
from orchflow.application.services import (
    create_access_control_service,
    create_project_registry_service,
)
from orchflow.domain.project_registry import CanonicalLifecycleAction


def _write_dispatch_batch(path: Path, *, start_identifier: str = "START") -> None:
    path.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        f"if /I \"%~1\"==\"{start_identifier}\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )


def test_registered_project_is_visible_to_owner(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="owner-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="owner-user", password="password123")
    ).access_token

    project_dir = tmp_path / "orch-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script, start_identifier="INICIAR")

    created_project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="orch-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
            mappings=(
                ProjectMappingInput(
                    canonical_action=CanonicalLifecycleAction.START,
                    script_label="INICIAR",
                ),
            ),
        )
    )

    listed_projects = project_registry_service.list_projects(token)

    assert len(listed_projects) == 1
    assert listed_projects[0].id == created_project.id
    assert listed_projects[0].action_mappings[0].script_label == "INICIAR"


def test_registration_rejects_scripts_without_first_argument_dispatch(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="invalid-script-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="invalid-script-user", password="password123")
    ).access_token

    project_dir = tmp_path / "invalid-script-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        ":STATUS\r\n"
        "echo status-ok\r\n",
        encoding="utf-8",
    )

    with pytest.raises(ProjectValidationError, match="first command argument"):
        project_registry_service.register_project(
            RegisterProjectCommand(
                token=token,
                reference_name="invalid-script-project",
                project_root_path=str(project_dir),
                lifecycle_script_path=str(lifecycle_script),
            )
        )


def test_registration_rejects_missing_mapped_dispatch_handler(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="missing-map-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="missing-map-user", password="password123")
    ).access_token

    project_dir = tmp_path / "missing-map-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script)

    with pytest.raises(ProjectValidationError, match="start -> INICIAR"):
        project_registry_service.register_project(
            RegisterProjectCommand(
                token=token,
                reference_name="missing-map-project",
                project_root_path=str(project_dir),
                lifecycle_script_path=str(lifecycle_script),
                mappings=(
                    ProjectMappingInput(
                        canonical_action=CanonicalLifecycleAction.START,
                        script_label=":INICIAR",
                    ),
                ),
            )
        )
