"""Contract tests for the Windows local development launchers."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEV_LAUNCHER = ROOT / "orchflow-dev.bat"
SETUP_LAUNCHER = ROOT / "orchflow-setup.bat"
CONTROL_LAUNCHER = ROOT / "orchflow-control.bat"
CONTROL_SCRIPT = ROOT / "scripts" / "orchflow-local-process-control.ps1"


def _launcher_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_windows_launchers_are_available_at_repository_root() -> None:
    assert DEV_LAUNCHER.exists()
    assert SETUP_LAUNCHER.exists()
    assert CONTROL_LAUNCHER.exists()
    assert CONTROL_SCRIPT.exists()


def test_windows_setup_launcher_preserves_existing_env_files() -> None:
    text = _launcher_text(SETUP_LAUNCHER)

    assert 'if exist "%TARGET_FILE%"' in text
    assert 'echo [skip] %TARGET_FILE% already exists.' in text
    assert 'copy "%SOURCE_FILE%" "%TARGET_FILE%"' in text
    assert '"%ROOT_DIR%\\.env.example" "%ROOT_DIR%\\.env"' in text
    assert '"%WEB_DIR%\\.env.example" "%WEB_DIR%\\.env"' in text


def test_windows_setup_launcher_covers_core_setup_and_runtime_commands() -> None:
    text = _launcher_text(SETUP_LAUNCHER)

    expected_commands = [
        "uv sync --dev",
        "corepack enable",
        "pnpm install",
        "uv run alembic upgrade head",
        "uv run orchflow info",
        "uv run orchflow health",
        "uv run orchflow database",
        'call "%CONTROL_LAUNCHER%" start',
    ]

    for command in expected_commands:
        assert command in text


def test_windows_setup_launcher_keeps_simple_setup_menu_and_cli_validation_scope() -> None:
    text = _launcher_text(SETUP_LAUNCHER)

    assert "OrchFlow Setup Launcher" in text
    assert "[1] Check environment, prerequisites, and dependencies" in text
    assert "[2] Start API and Web" in text
    assert "[3] Exit" in text
    assert "Validating OrchFlow CLI and bootstrap status" in text
    assert 'if "%ACTION%"=="4"' not in text
    assert "if \"%ACTION%\"==\"1\" call :CHECK_PREREQUISITES & pause & goto MENU" not in text


def test_windows_dev_launcher_delegates_to_setup_and_control_launchers() -> None:
    text = _launcher_text(DEV_LAUNCHER)

    assert 'set "SETUP_LAUNCHER=%ROOT_DIR%\\orchflow-setup.bat"' in text
    assert 'set "CONTROL_LAUNCHER=%ROOT_DIR%\\orchflow-control.bat"' in text
    assert 'call "%SETUP_LAUNCHER%" check' in text
    assert 'call "%CONTROL_LAUNCHER%" start' in text
    assert 'call "%CONTROL_LAUNCHER%"' in text


def test_windows_control_launcher_exposes_pid_based_process_menu() -> None:
    text = _launcher_text(CONTROL_LAUNCHER)

    assert "OrchFlow Control Launcher" in text
    assert "[1] Check status" in text
    assert "[2] Start" in text
    assert "[3] Stop" in text
    assert "[4] Restart" in text
    assert "[5] Exit" in text
    assert 'set "CONTROL_SCRIPT=%ROOT_DIR%\\scripts\\orchflow-local-process-control.ps1"' in text
    assert 'powershell -NoProfile -ExecutionPolicy Bypass -File "%CONTROL_SCRIPT%" %~1' in text
    assert 'call "%SETUP_LAUNCHER%" start-all' not in text


def test_windows_process_control_script_tracks_owned_local_processes() -> None:
    text = _launcher_text(CONTROL_SCRIPT)

    expected_fragments = [
        "orchflow-api.pid",
        "orchflow-web.pid",
        "orchflow-api.json",
        "orchflow-web.json",
        "ORCHFLOW_RUNTIME_DIR",
        "ORCHFLOW_API_HOST",
        "ORCHFLOW_API_PORT",
        "ORCHFLOW_WEB_HOST",
        "ORCHFLOW_WEB_PORT",
        "ORCHFLOW_WEB_URL",
        "uv run uvicorn orchflow.external.api.app:create_app --factory",
        "pnpm dev --host",
        "--strictPort",
        "Get-NetTCPConnection",
        "Write-ProcessMetadata",
        "Rolling back API start because Web did not start.",
        "taskkill /PID $trackedPid /T /F",
    ]

    for fragment in expected_fragments:
        assert fragment in text
