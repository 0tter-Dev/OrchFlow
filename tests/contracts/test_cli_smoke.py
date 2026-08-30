"""Smoke tests for the initial CLI bootstrap."""

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from orchflow.external.cli.app import app

runner = CliRunner()


def _extract_user_id_from_cli_output(output: str, username: str) -> str:
    for block in output.strip().split("\n\n"):
        lines = block.splitlines()
        if f"username: {username}" not in lines:
            continue
        return next(line.removeprefix("id: ") for line in lines if line.startswith("id: "))
    raise AssertionError(f"User '{username}' was not found in CLI output.")


def test_info_command_displays_bootstrap_metadata() -> None:
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "OrchFlow 0.3.0" in result.stdout
    assert "stage: bootstrap" in result.stdout


def test_health_command_displays_operational_status() -> None:
    result = runner.invoke(app, ["health"])

    assert result.exit_code == 0
    assert "status: ok" in result.stdout


def test_config_command_displays_runtime_summary() -> None:
    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert "environment: development" in result.stdout
    assert "database_dialect: sqlite" in result.stdout


def test_database_command_displays_connectivity() -> None:
    result = runner.invoke(app, ["database"])

    assert result.exit_code == 0
    assert "status: ok" in result.stdout
    assert "is_connected: true" in result.stdout


def test_cli_auth_flow_registers_bootstrap_admin_and_lists_users(
    isolated_environment: None,
) -> None:
    register_result = runner.invoke(
        app,
        ["auth", "register", "--username", "admin-user", "--password", "password123"],
    )
    assert register_result.exit_code == 0
    assert "role: admin" in register_result.stdout

    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "admin-user", "--password", "password123"],
    )
    assert login_result.exit_code == 0
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    me_result = runner.invoke(app, ["auth", "me", "--token", token])
    assert me_result.exit_code == 0
    assert "username: admin-user" in me_result.stdout

    users_result = runner.invoke(app, ["auth", "users", "--token", token])
    assert users_result.exit_code == 0
    assert "role: admin" in users_result.stdout


def test_cli_audit_history_flow_is_available(isolated_environment: None) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "audit-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "audit-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    audit_result = runner.invoke(app, ["audit", "events", "--token", token, "--limit", "10"])

    assert audit_result.exit_code == 0
    assert "action: admin.audit_events.list" in audit_result.stdout
    assert "action: user.login" in audit_result.stdout


def test_cli_ai_assistance_status_flow_is_available(isolated_environment: None) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "ai-status-user", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "ai-status-user", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    status_result = runner.invoke(app, ["ai", "status", "--token", token])

    assert status_result.exit_code == 0
    assert "provider: litellm" in status_result.stdout
    assert "status: disabled" in status_result.stdout
    assert "ready_for_requests: false" in status_result.stdout


def test_cli_admin_user_management_flow_is_available(isolated_environment: None) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "admin-user", "--password", "password123"],
    )
    runner.invoke(
        app,
        ["auth", "register", "--username", "member-user", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "admin-user", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")
    users_result = runner.invoke(app, ["auth", "users", "--token", token])
    member_id = _extract_user_id_from_cli_output(users_result.stdout, "member-user")

    update_result = runner.invoke(
        app,
        [
            "auth",
            "update-user",
            "--token",
            token,
            "--user-id",
            member_id,
            "--role",
            "admin",
            "--no-is-active",
        ],
    )

    assert update_result.exit_code == 0
    assert "role: admin" in update_result.stdout
    assert "is_active: false" in update_result.stdout


def test_cli_project_registry_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "project-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "project-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"INICIAR\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
            "--map-start",
            "INICIAR",
        ],
    )
    assert register_result.exit_code == 0
    assert "reference_name: cli-project" in register_result.stdout

    list_result = runner.invoke(app, ["project", "list", "--token", token])
    assert list_result.exit_code == 0
    assert "reference_name: cli-project" in list_result.stdout


def test_cli_project_lifecycle_configuration_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "manual-cli-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "manual-cli-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-manual-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"INICIAR\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-manual-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
        ],
    )
    project_id = next(
        line.removeprefix("id: ")
        for line in register_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    configure_result = runner.invoke(
        app,
        [
            "project",
            "configure-lifecycle",
            "--token",
            token,
            "--project-id",
            project_id,
            "--map-start",
            "INICIAR",
            "--stop-unconfigured",
            "--restart-unconfigured",
        ],
    )

    assert configure_result.exit_code == 0
    assert "lifecycle_configuration_health: partial" in configure_result.stdout
    assert "start: INICIAR (user_defined)" in configure_result.stdout
    assert "stop: unconfigured" in configure_result.stdout
    assert "restart: unconfigured" in configure_result.stdout


def test_cli_project_reload_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "reload-cli-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "reload-cli-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-reload-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-reload-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
        ],
    )
    project_id = next(
        line.removeprefix("id: ")
        for line in register_result.stdout.splitlines()
        if line.startswith("id: ")
    )
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    reload_result = runner.invoke(
        app,
        ["project", "reload", "--token", token, "--project-id", project_id],
    )
    reload_many_result = runner.invoke(
        app,
        [
            "project",
            "reload-many",
            "--token",
            token,
            "--project-id",
            project_id,
        ],
    )

    assert reload_result.exit_code == 0
    assert "previous_lifecycle_configuration_health: partial" in reload_result.stdout
    assert "current_lifecycle_configuration_health: complete" in reload_result.stdout
    assert "changed_actions: start, stop, restart" in reload_result.stdout
    assert reload_many_result.exit_code == 0
    assert "changed_actions: none" in reload_many_result.stdout


def test_cli_project_owner_management_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "owner-admin", "--password", "password123"],
    )
    runner.invoke(
        app,
        ["auth", "register", "--username", "owner-member", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "owner-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")
    users_result = runner.invoke(app, ["auth", "users", "--token", token])
    member_id = _extract_user_id_from_cli_output(users_result.stdout, "owner-member")

    project_dir = tmp_path / "cli-owned-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-owned-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
        ],
    )
    project_id = next(
        line.removeprefix("id: ")
        for line in register_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    add_result = runner.invoke(
        app,
        [
            "project",
            "add-owner",
            "--token",
            token,
            "--project-id",
            project_id,
            "--user-id",
            member_id,
        ],
    )
    assert add_result.exit_code == 0
    assert f"owner_user_ids: 1, {member_id}" in add_result.stdout

    remove_result = runner.invoke(
        app,
        [
            "project",
            "remove-owner",
            "--token",
            token,
            "--project-id",
            project_id,
            "--user-id",
            member_id,
        ],
    )
    assert remove_result.exit_code == 0
    assert f"owner_user_ids: 1, {member_id}" not in remove_result.stdout


def test_cli_lifecycle_rejects_unconfigured_actions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "gated-cli-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "gated-cli-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-gated-lifecycle-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-gated-lifecycle-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
        ],
    )
    project_id = next(
        line.removeprefix("id: ")
        for line in register_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    lifecycle_result = runner.invoke(
        app,
        ["lifecycle", "start", "--token", token, "--project-id", project_id],
    )

    assert lifecycle_result.exit_code == 1
    assert "undefined for this project" in lifecycle_result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only batch execution")
def test_cli_lifecycle_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "lifecycle-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "lifecycle-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-lifecycle-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo started-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stopped-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restarted-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-lifecycle-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
        ],
    )
    assert register_result.exit_code == 0
    project_id_line = next(
        line for line in register_result.stdout.splitlines() if line.startswith("id: ")
    )
    project_id = project_id_line.removeprefix("id: ")

    lifecycle_result = runner.invoke(
        app,
        ["lifecycle", "status", "--token", token, "--project-id", project_id],
    )
    assert lifecycle_result.exit_code == 0
    assert "canonical_action: status" in lifecycle_result.stdout
    assert "status-ok" in lifecycle_result.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only runtime inspection")
def test_cli_runtime_inspection_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "runtime-admin", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "runtime-admin", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-runtime-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "set \"APP_PORT=49191\"\r\n"
        "set \"APP_URL=http://localhost:49191\"\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )

    register_result = runner.invoke(
        app,
        [
            "project",
            "register",
            "--token",
            token,
            "--reference-name",
            "cli-runtime-project",
            "--project-root-path",
            str(project_dir),
            "--lifecycle-script-path",
            str(lifecycle_script),
        ],
    )
    project_id_line = next(
        line for line in register_result.stdout.splitlines() if line.startswith("id: ")
    )
    project_id = project_id_line.removeprefix("id: ")

    runtime_result = runner.invoke(
        app,
        ["runtime", "inspect", "--token", token, "--project-id", project_id],
    )
    assert runtime_result.exit_code == 0
    assert "known_port: 49191" in runtime_result.stdout
    assert "application_reachable:" in runtime_result.stdout
    assert "status_reason:" in runtime_result.stdout
    assert "inspected_at:" in runtime_result.stdout
