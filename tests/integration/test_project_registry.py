"""Integration tests for project registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.project_registry import (
    ProjectMappingInput,
    ProjectOwnershipError,
    ProjectValidationError,
    RegisterProjectCommand,
    ReloadProjectCommand,
    ReloadProjectsCommand,
    UpdateLifecycleFunctionConfigurationCommand,
    UpdateProjectOwnerCommand,
)
from orchflow.application.services import (
    create_access_control_service,
    create_project_registry_service,
)
from orchflow.domain.project_registry import CanonicalLifecycleAction, MappingSource


def _write_dispatch_batch(
    path: Path,
    *,
    include_restart: bool = True,
    include_status: bool = True,
    include_stop: bool = True,
    start_identifier: str | None = "START",
) -> None:
    lines = ["@echo off\r\n"]
    if include_status:
        lines.append("if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n")
    if start_identifier is not None:
        lines.append(f"if /I \"%~1\"==\"{start_identifier}\" echo start-ok & exit /b 0\r\n")
    if include_stop:
        lines.append("if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n")
    if include_restart:
        lines.append("if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n")
    lines.append("exit /b 1\r\n")
    path.write_text(
        "".join(lines),
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
    mapping_by_action = {
        mapping.canonical_action: mapping
        for mapping in listed_projects[0].action_mappings
    }

    assert len(listed_projects) == 1
    assert listed_projects[0].id == created_project.id
    assert mapping_by_action[CanonicalLifecycleAction.START].script_label == "INICIAR"


def test_registration_imports_detected_ideal_lifecycle_functions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="auto-map-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="auto-map-user", password="password123")
    ).access_token

    project_dir = tmp_path / "auto-map-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script)

    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="auto-map-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    assert {
        mapping.canonical_action: (mapping.script_label, mapping.source)
        for mapping in project.action_mappings
    } == {
        CanonicalLifecycleAction.STATUS: ("STATUS", MappingSource.IMPORTED),
        CanonicalLifecycleAction.START: ("START", MappingSource.IMPORTED),
        CanonicalLifecycleAction.STOP: ("STOP", MappingSource.IMPORTED),
        CanonicalLifecycleAction.RESTART: ("RESTART", MappingSource.IMPORTED),
    }


def test_registration_accepts_partial_lifecycle_configuration(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="partial-config-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="partial-config-user", password="password123")
    ).access_token

    project_dir = tmp_path / "partial-config-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(
        lifecycle_script,
        include_restart=False,
        include_stop=False,
        include_status=False,
        start_identifier="START",
    )

    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="partial-config-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    assert len(project.action_mappings) == 1
    assert project.action_mappings[0].canonical_action is CanonicalLifecycleAction.START
    assert project.action_mappings[0].script_label == "START"


def test_registration_rejects_lifecycle_scripts_without_configurable_actions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="blocked-config-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="blocked-config-user", password="password123")
    ).access_token

    project_dir = tmp_path / "blocked-config-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"VERIFY\" echo custom-status & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    with pytest.raises(ProjectValidationError, match="at least one configured"):
        project_registry_service.register_project(
            RegisterProjectCommand(
                token=token,
                reference_name="blocked-config-project",
                project_root_path=str(project_dir),
                lifecycle_script_path=str(lifecycle_script),
            )
        )


def test_user_can_replace_lifecycle_configuration_with_unconfigured_decision(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="manual-config-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="manual-config-user", password="password123")
    ).access_token

    project_dir = tmp_path / "manual-config-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script, start_identifier="INICIAR")
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="manual-config-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    updated_project = project_registry_service.update_lifecycle_function_configuration(
        UpdateLifecycleFunctionConfigurationCommand(
            token=token,
            project_id=project.id,
            mappings=(
                ProjectMappingInput(
                    canonical_action=CanonicalLifecycleAction.START,
                    script_label="INICIAR",
                ),
            ),
            unconfigured_actions=(CanonicalLifecycleAction.STOP,),
        )
    )

    assert {
        mapping.canonical_action: mapping.script_label
        for mapping in updated_project.action_mappings
    } == {CanonicalLifecycleAction.START: "INICIAR"}
    assert tuple(
        decision.canonical_action
        for decision in updated_project.lifecycle_function_decisions
    ) == (CanonicalLifecycleAction.STOP,)
    assert updated_project.lifecycle_function_decisions[0].state == "unconfigured"


def test_lifecycle_configuration_update_rejects_all_unconfigured_actions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="all-unconfigured-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="all-unconfigured-user", password="password123")
    ).access_token

    project_dir = tmp_path / "all-unconfigured-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script)
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="all-unconfigured-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    with pytest.raises(ProjectValidationError, match="At least one lifecycle function"):
        project_registry_service.update_lifecycle_function_configuration(
            UpdateLifecycleFunctionConfigurationCommand(
                token=token,
                project_id=project.id,
                unconfigured_actions=(
                    CanonicalLifecycleAction.STATUS,
                    CanonicalLifecycleAction.START,
                    CanonicalLifecycleAction.STOP,
                    CanonicalLifecycleAction.RESTART,
                ),
            )
        )


def test_project_reload_refreshes_detection_and_preserves_valid_user_decisions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="reload-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="reload-user", password="password123")
    ).access_token

    project_dir = tmp_path / "reload-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script, include_restart=False, start_identifier="INICIAR")
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="reload-project",
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
    project_registry_service.update_lifecycle_function_configuration(
        UpdateLifecycleFunctionConfigurationCommand(
            token=token,
            project_id=project.id,
            mappings=(
                ProjectMappingInput(
                    canonical_action=CanonicalLifecycleAction.START,
                    script_label="INICIAR",
                ),
            ),
            unconfigured_actions=(CanonicalLifecycleAction.STOP,),
        )
    )
    _write_dispatch_batch(lifecycle_script, include_stop=True, start_identifier="START")

    result = project_registry_service.reload_project(
        ReloadProjectCommand(token=token, project_id=project.id)
    )

    mappings = {
        mapping.canonical_action: (mapping.script_label, mapping.source)
        for mapping in result.project.action_mappings
    }
    assert result.previous_health.value == "partial"
    assert result.current_health.value == "partial"
    assert result.changed_actions == (
        CanonicalLifecycleAction.STATUS,
        CanonicalLifecycleAction.START,
        CanonicalLifecycleAction.RESTART,
    )
    assert mappings == {
        CanonicalLifecycleAction.STATUS: ("STATUS", MappingSource.IMPORTED),
        CanonicalLifecycleAction.START: ("START", MappingSource.IMPORTED),
        CanonicalLifecycleAction.RESTART: ("RESTART", MappingSource.IMPORTED),
    }
    assert tuple(
        decision.canonical_action
        for decision in result.project.lifecycle_function_decisions
    ) == (CanonicalLifecycleAction.STOP,)


def test_project_reload_can_mark_project_as_blocked_after_script_changes(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="blocked-reload-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="blocked-reload-user", password="password123")
    ).access_token

    project_dir = tmp_path / "blocked-reload-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script, include_restart=False, include_stop=False)
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="blocked-reload-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"VERIFY\" echo custom-status & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    result = project_registry_service.reload_project(
        ReloadProjectCommand(token=token, project_id=project.id)
    )

    assert result.previous_health.value == "partial"
    assert result.current_health.value == "blocked"
    assert result.project.action_mappings == ()
    assert result.changed_actions == (
        CanonicalLifecycleAction.STATUS,
        CanonicalLifecycleAction.START,
    )


def test_project_reload_many_runs_visible_projects_in_sequence(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()

    access_control_service.register_user(
        RegisterUserCommand(username="reload-many-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="reload-many-user", password="password123")
    ).access_token

    project_ids: list[int] = []
    for index in range(2):
        project_dir = tmp_path / f"reload-many-project-{index}"
        project_dir.mkdir()
        lifecycle_script = project_dir / "control.bat"
        _write_dispatch_batch(lifecycle_script, include_restart=False)
        project = project_registry_service.register_project(
            RegisterProjectCommand(
                token=token,
                reference_name=f"reload-many-project-{index}",
                project_root_path=str(project_dir),
                lifecycle_script_path=str(lifecycle_script),
            )
        )
        project_ids.append(project.id)
        _write_dispatch_batch(lifecycle_script)

    results = project_registry_service.reload_projects(
        ReloadProjectsCommand(token=token, project_ids=tuple(project_ids))
    )

    assert [result.project.id for result in results] == project_ids
    assert all(result.current_health.value == "complete" for result in results)
    assert all(result.changed_actions == (CanonicalLifecycleAction.RESTART,) for result in results)


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


def test_admin_can_add_and_remove_project_owner(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    admin = access_control_service.register_user(
        RegisterUserCommand(username="admin-user", password="password123")
    )
    member = access_control_service.register_user(
        RegisterUserCommand(username="member-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="admin-user", password="password123")
    ).access_token

    project_dir = tmp_path / "owned-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script)
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="owned-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    with_member = project_registry_service.add_project_owner(
        UpdateProjectOwnerCommand(token=token, project_id=project.id, user_id=member.id)
    )
    assert with_member.owner_user_ids == (admin.id, member.id)

    without_member = project_registry_service.remove_project_owner(
        UpdateProjectOwnerCommand(token=token, project_id=project.id, user_id=member.id)
    )
    assert without_member.owner_user_ids == (admin.id,)


def test_project_must_keep_at_least_one_owner(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    admin = access_control_service.register_user(
        RegisterUserCommand(username="admin-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="admin-user", password="password123")
    ).access_token

    project_dir = tmp_path / "single-owner-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_dispatch_batch(lifecycle_script)
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="single-owner-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    with pytest.raises(ProjectOwnershipError, match="at least one owner"):
        project_registry_service.remove_project_owner(
            UpdateProjectOwnerCommand(token=token, project_id=project.id, user_id=admin.id)
        )
