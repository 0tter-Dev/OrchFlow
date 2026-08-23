"""Integration tests for project registry."""

from __future__ import annotations

from pathlib import Path

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.project_registry import ProjectMappingInput, RegisterProjectCommand
from orchflow.application.services import (
    create_access_control_service,
    create_project_registry_service,
)
from orchflow.domain.project_registry import CanonicalLifecycleAction


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
    lifecycle_script.write_text("@echo off\r\necho OrchFlow\r\n", encoding="utf-8")

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
