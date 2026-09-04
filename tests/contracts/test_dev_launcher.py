"""Contract tests for the Windows local development launcher."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "orchflow-dev.bat"


def _launcher_text() -> str:
    return LAUNCHER.read_text(encoding="utf-8")


def test_windows_dev_launcher_is_available_at_repository_root() -> None:
    assert LAUNCHER.exists()


def test_windows_dev_launcher_preserves_existing_env_files() -> None:
    text = _launcher_text()

    assert 'if exist "%TARGET_FILE%"' in text
    assert 'echo [skip] %TARGET_FILE% already exists.' in text
    assert 'copy "%SOURCE_FILE%" "%TARGET_FILE%"' in text
    assert '"%ROOT_DIR%\\.env.example" "%ROOT_DIR%\\.env"' in text
    assert '"%WEB_DIR%\\.env.example" "%WEB_DIR%\\.env"' in text


def test_windows_dev_launcher_covers_core_setup_and_runtime_commands() -> None:
    text = _launcher_text()

    expected_commands = [
        "uv sync --dev",
        "corepack enable",
        "pnpm install",
        "uv run alembic upgrade head",
        "uv run orchflow info",
        "uv run orchflow health",
        "uv run orchflow database",
        "uv run uvicorn orchflow.external.api.app:create_app --factory",
        "pnpm dev",
        'start "" "%WEB_URL%"',
    ]

    for command in expected_commands:
        assert command in text


def test_windows_dev_launcher_routes_menu_options_through_explicit_labels() -> None:
    text = _launcher_text()

    assert 'if "%ACTION%"=="1" goto MENU_CHECK_PREREQUISITES' in text
    assert 'if "%ACTION%"=="9" goto MENU_RUN_SETUP' in text
    assert "if \"%ACTION%\"==\"1\" call :CHECK_PREREQUISITES & pause & goto MENU" not in text
