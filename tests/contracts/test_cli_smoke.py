"""Smoke tests for the initial CLI bootstrap."""

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from orchflow.external.cli.app import app

runner = CliRunner()


def test_info_command_displays_bootstrap_metadata() -> None:
    result = runner.invoke(app, ["info"])

    assert result.exit_code == 0
    assert "OrchFlow 0.1.2" in result.stdout
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
    lifecycle_script.write_text("@echo off\r\necho CLI\r\n", encoding="utf-8")

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
