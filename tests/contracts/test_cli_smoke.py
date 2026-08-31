"""Smoke tests for the initial CLI bootstrap."""

import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from orchflow.application.ai_assistance import AIAssistancePromptMessage
from orchflow.external.cli.app import app
from orchflow.infrastructure.ai.litellm_gateway import LiteLLMGatewayClient
from orchflow.infrastructure.config.settings import get_settings

runner = CliRunner()


def _proposal_completion() -> str:
    return (
        '{"lifecycle_strategy":"Use canonical dispatch labels.",'
        '"runtime_hints":["APP_URL can help runtime inspection."],'
        '"candidate_script_content":"@echo off\\r\\nif /I \\"%~1\\"==\\"STATUS\\" '
        'echo status-ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"START\\" '
        'echo start-ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"STOP\\" '
        'echo stop-ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"RESTART\\" '
        'echo restart-ok & exit /b 0\\r\\n",'
        '"action_mappings":[{"canonical_action":"status","script_label":"STATUS",'
        '"rationale":"Detected status command."}],'
        '"warnings":["Review before writing files."]}'
    )


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
    assert "OrchFlow 0.3.9" in result.stdout
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

    filtered_result = runner.invoke(
        app,
        ["audit", "events", "--token", token, "--limit", "10", "--action", "user.login"],
    )

    assert filtered_result.exit_code == 0
    assert "action: user.login" in filtered_result.stdout
    assert "action: admin.audit_events.list" not in filtered_result.stdout


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


def test_cli_ai_assistance_gateway_health_flow_is_available(
    isolated_environment: None,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "ai-health-user", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "ai-health-user", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    health_result = runner.invoke(app, ["ai", "health", "--token", token])

    assert health_result.exit_code == 0
    assert "provider: litellm" in health_result.stdout
    assert "status: disabled" in health_result.stdout
    assert "checked: false" in health_result.stdout


def test_cli_ai_assistance_model_discovery_flow_is_available(
    isolated_environment: None,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "ai-model-user", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "ai-model-user", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    models_result = runner.invoke(app, ["ai", "models", "--token", token])

    assert models_result.exit_code == 0
    assert "provider: litellm" in models_result.stdout
    assert "supports_discovery: false" in models_result.stdout
    assert "models:\nnone" in models_result.stdout


def test_cli_ai_context_manifest_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    runner.invoke(
        app,
        ["auth", "register", "--username", "ai-manifest-user", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "ai-manifest-user", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-ai-manifest-project"
    project_dir.mkdir()
    (project_dir / "app.py").write_text("print('ok')\n", encoding="utf-8")
    (project_dir / ".env").write_text("SECRET=value\n", encoding="utf-8")
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
            "cli-ai-manifest-project",
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

    manifest_result = runner.invoke(
        app,
        [
            "ai",
            "manifest-create",
            "--token",
            token,
            "--project-id",
            project_id,
            "--selected-model",
            "ollama/llama3",
            "--intended-operation",
            "improve_lifecycle_script",
            "--include-pattern",
            "*.py",
        ],
    )

    assert manifest_result.exit_code == 0
    assert "selected_model: ollama/llama3" in manifest_result.stdout
    assert "included_paths: app.py" in manifest_result.stdout
    assert ".env" in manifest_result.stdout
    manifest_id = next(
        line.removeprefix("id: ")
        for line in manifest_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    show_result = runner.invoke(
        app,
        ["ai", "manifest-show", "--token", token, "--manifest-id", manifest_id],
    )

    assert show_result.exit_code == 0
    assert "project_id:" in show_result.stdout
    assert "included_paths: app.py" in show_result.stdout


def test_cli_ai_analysis_proposal_flow_is_available(
    isolated_environment: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ORCHFLOW_AI_ENABLED", "true")
    get_settings.cache_clear()

    captured_messages: list[AIAssistancePromptMessage] = []

    def fake_generate_completion(
        self: LiteLLMGatewayClient,
        *,
        model: str,
        messages: tuple[AIAssistancePromptMessage, ...],
    ) -> str:
        assert model == "ollama/llama3"
        captured_messages.extend(messages)
        return _proposal_completion()

    monkeypatch.setattr(
        LiteLLMGatewayClient,
        "generate_completion",
        fake_generate_completion,
    )
    runner.invoke(
        app,
        ["auth", "register", "--username", "ai-proposal-user", "--password", "password123"],
    )
    login_result = runner.invoke(
        app,
        ["auth", "login", "--username", "ai-proposal-user", "--password", "password123"],
    )
    token_line = next(
        line for line in login_result.stdout.splitlines() if line.startswith("access_token: ")
    )
    token = token_line.removeprefix("access_token: ")

    project_dir = tmp_path / "cli-ai-proposal-project"
    project_dir.mkdir()
    (project_dir / "app.py").write_text("print('approved proposal context')\n", encoding="utf-8")
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
            "cli-ai-proposal-project",
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
    manifest_result = runner.invoke(
        app,
        [
            "ai",
            "manifest-create",
            "--token",
            token,
            "--project-id",
            project_id,
            "--selected-model",
            "ollama/llama3",
            "--intended-operation",
            "improve_lifecycle_script",
            "--include-pattern",
            "app.py",
        ],
    )
    manifest_id = next(
        line.removeprefix("id: ")
        for line in manifest_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    proposal_result = runner.invoke(
        app,
        [
            "ai",
            "proposal-create",
            "--token",
            token,
            "--manifest-id",
            manifest_id,
            "--user-instructions",
            "Keep it reviewable.",
        ],
    )

    assert proposal_result.exit_code == 0
    assert "lifecycle_strategy: Use canonical dispatch labels." in proposal_result.stdout
    assert "status: STATUS" in proposal_result.stdout
    assert "candidate_script_content:" in proposal_result.stdout
    assert "approved proposal context" in captured_messages[1].content
    assert [
        line.strip()
        for line in lifecycle_script.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ] == [
        "@echo off",
        'if /I "%~1"=="STATUS" echo status-ok & exit /b 0',
        "exit /b 1",
    ]
    proposal_id = next(
        line.removeprefix("id: ")
        for line in proposal_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    show_result = runner.invoke(
        app,
        ["ai", "proposal-show", "--token", token, "--proposal-id", proposal_id],
    )

    assert show_result.exit_code == 0
    assert "manifest_id:" in show_result.stdout
    assert "runtime_hints: APP_URL can help runtime inspection." in show_result.stdout

    review_result = runner.invoke(
        app,
        [
            "ai",
            "proposal-review",
            "--token",
            token,
            "--proposal-id",
            proposal_id,
            "--decision",
            "approved",
            "--reviewer-notes",
            "Approved for next step.",
        ],
    )

    assert review_result.exit_code == 0
    assert "decision: approved" in review_result.stdout
    assert "validation_status: valid" in review_result.stdout
    assert "validation_errors: none" in review_result.stdout

    apply_result = runner.invoke(
        app,
        [
            "ai",
            "proposal-apply",
            "--token",
            token,
            "--proposal-id",
            proposal_id,
            "--confirm-file-write",
            "--confirm-mapping-persistence",
        ],
    )

    assert apply_result.exit_code == 0
    assert "persisted_mappings:" in apply_result.stdout
    assert "start: START" in apply_result.stdout
    assert "lifecycle_configuration_health: complete" in apply_result.stdout
    assert "status: STATUS (ai_approved)" in apply_result.stdout
    assert "START" in lifecycle_script.read_text(encoding="utf-8")


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
    project_id = next(
        line.removeprefix("id: ")
        for line in register_result.stdout.splitlines()
        if line.startswith("id: ")
    )

    replacement_script = project_dir / "orchflow.bat"
    replacement_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    update_result = runner.invoke(
        app,
        [
            "project",
            "update",
            "--token",
            token,
            "--project-id",
            project_id,
            "--reference-name",
            "cli-project-renamed",
            "--lifecycle-script-path",
            str(replacement_script),
            "--clear-description",
            "--map-start",
            "START",
            "--stop-unconfigured",
            "--restart-unconfigured",
        ],
    )
    assert update_result.exit_code == 0
    assert "reference_name: cli-project-renamed" in update_result.stdout
    assert "start: START (user_defined)" in update_result.stdout

    list_result = runner.invoke(app, ["project", "list", "--token", token])
    assert list_result.exit_code == 0
    assert "reference_name: cli-project-renamed" in list_result.stdout


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
