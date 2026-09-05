"""Integration tests for runtime inspection."""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError

import pytest

from orchflow.application.access_control import (
    AuthorizationError,
    LoginCommand,
    RegisterUserCommand,
)
from orchflow.application.project_registry import RegisterProjectCommand
from orchflow.application.runtime_inspection import (
    InspectRuntimeBatchCommand,
    InspectRuntimeCommand,
)
from orchflow.application.services import (
    create_access_control_service,
    create_project_registry_service,
    create_runtime_inspection_service,
)
from orchflow.domain.project_registry import Project
from orchflow.infrastructure.runtime_inspection import windows
from orchflow.infrastructure.runtime_inspection.windows import WindowsRuntimeInspector

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only runtime inspection")


def _find_free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_port(port: int, *, timeout_seconds: float = 5.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with socket.socket() as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    pytest.fail(f"Timed out waiting for port {port} to start listening.")


def _write_runtime_batch(path: Path, port: int) -> None:
    path.write_text(
        "@echo off\r\n"
        f'set "APP_PORT={port}"\r\n'
        f'set "APP_URL=http://localhost:{port}"\r\n'
        "if /I \"%~1\"==\"STATUS\" goto STATUS\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n"
        ":STATUS\r\n"
        "for /f \"tokens=5\" %%P in ('netstat -ano "
        "^| findstr /C:\":%APP_PORT%\" "
        "^| findstr /C:\"LISTENING\"') do "
        "echo status-ok %%P\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )


def _write_runtime_url_only_batch(path: Path, port: int) -> None:
    path.write_text(
        "@echo off\r\n"
        f'set "APP_URL=http://localhost:{port}"\r\n'
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )


def _write_runtime_no_hint_batch(path: Path) -> None:
    path.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )


def test_runtime_inspection_reports_running_process_and_port(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    runtime_service = create_runtime_inspection_service()

    access_control_service.register_user(
        RegisterUserCommand(username="runtime-admin", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="runtime-admin", password="password123")
    ).access_token

    port = _find_free_port()
    project_dir = tmp_path / "runtime-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_runtime_batch(lifecycle_script, port)

    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="runtime-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=project.project_root_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_port(port)

        snapshot = runtime_service.inspect_runtime(
            InspectRuntimeCommand(token=token, project_id=project.id)
        )
        assert snapshot.status == "running"
        assert snapshot.known_port == port
        assert snapshot.application_url == f"http://localhost:{port}"
        assert snapshot.application_reachable is True
        assert f"APP_PORT {port}" in snapshot.status_reason
        assert len(snapshot.process_snapshots) >= 1
    finally:
        server_process.terminate()
        server_process.wait(timeout=5)


def test_runtime_inspection_uses_reachable_app_url_without_app_port(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    runtime_service = create_runtime_inspection_service()

    access_control_service.register_user(
        RegisterUserCommand(username="runtime-url-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="runtime-url-user", password="password123")
    ).access_token

    port = _find_free_port()
    project_dir = tmp_path / "runtime-url-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_runtime_url_only_batch(lifecycle_script, port)
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="runtime-url-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=project.project_root_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_port(port)

        snapshot = runtime_service.inspect_runtime(
            InspectRuntimeCommand(token=token, project_id=project.id)
        )

        assert snapshot.status == "running"
        assert snapshot.known_port is None
        assert snapshot.application_url == f"http://localhost:{port}"
        assert snapshot.application_reachable is True
        assert "No APP_PORT hint" in snapshot.status_reason
        assert "responded" in snapshot.status_reason
    finally:
        server_process.terminate()
        server_process.wait(timeout=5)


def test_runtime_inspection_reports_unsupported_when_script_has_no_runtime_hints(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    runtime_service = create_runtime_inspection_service()

    access_control_service.register_user(
        RegisterUserCommand(username="runtime-no-hint-user", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="runtime-no-hint-user", password="password123")
    ).access_token

    project_dir = tmp_path / "runtime-no-hint-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_runtime_no_hint_batch(lifecycle_script)
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=token,
            reference_name="runtime-no-hint-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    snapshot = runtime_service.inspect_runtime(
        InspectRuntimeCommand(token=token, project_id=project.id)
    )

    assert snapshot.status == "unsupported"
    assert snapshot.known_port is None
    assert snapshot.application_url is None
    assert snapshot.application_reachable is None
    assert "No APP_PORT or APP_URL hint" in snapshot.status_reason


def test_runtime_inspection_batch_returns_visible_projects_once(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    runtime_service = create_runtime_inspection_service()

    access_control_service.register_user(
        RegisterUserCommand(username="runtime-batch-admin", password="password123")
    )
    token = access_control_service.login(
        LoginCommand(username="runtime-batch-admin", password="password123")
    ).access_token

    project_ids: list[int] = []
    ports = [_find_free_port(), _find_free_port()]
    for index, port in enumerate(ports):
        project_dir = tmp_path / f"runtime-batch-project-{index}"
        project_dir.mkdir()
        lifecycle_script = project_dir / "control.bat"
        _write_runtime_batch(lifecycle_script, port)
        project = project_registry_service.register_project(
            RegisterProjectCommand(
                token=token,
                reference_name=f"runtime-batch-project-{index}",
                project_root_path=str(project_dir),
                lifecycle_script_path=str(lifecycle_script),
            )
        )
        project_ids.append(project.id)

    snapshots = runtime_service.inspect_runtime_batch(
        InspectRuntimeBatchCommand(
            token=token,
            project_ids=(project_ids[0], project_ids[1], project_ids[0]),
        )
    )

    assert [snapshot.project_id for snapshot in snapshots] == project_ids
    assert [snapshot.known_port for snapshot in snapshots] == ports


def test_runtime_inspection_batch_reuses_project_visibility(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    access_control_service = create_access_control_service()
    project_registry_service = create_project_registry_service()
    runtime_service = create_runtime_inspection_service()

    access_control_service.register_user(
        RegisterUserCommand(username="runtime-batch-owner", password="password123")
    )
    owner_token = access_control_service.login(
        LoginCommand(username="runtime-batch-owner", password="password123")
    ).access_token
    access_control_service.register_user(
        RegisterUserCommand(username="runtime-batch-member", password="password123")
    )
    member_token = access_control_service.login(
        LoginCommand(username="runtime-batch-member", password="password123")
    ).access_token

    project_dir = tmp_path / "runtime-batch-private-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    _write_runtime_batch(lifecycle_script, _find_free_port())
    project = project_registry_service.register_project(
        RegisterProjectCommand(
            token=owner_token,
            reference_name="runtime-batch-private-project",
            project_root_path=str(project_dir),
            lifecycle_script_path=str(lifecycle_script),
        )
    )

    with pytest.raises(AuthorizationError, match="Project is not visible"):
        runtime_service.inspect_runtime_batch(
            InspectRuntimeBatchCommand(token=member_token, project_ids=(project.id,))
        )


def test_runtime_inspection_explains_app_url_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lifecycle_script = tmp_path / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        'set "APP_URL=http://localhost:65535"\r\n'
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    now = datetime.now(UTC)
    project = Project(
        id=1,
        reference_name="timeout-project",
        description=None,
        project_root_path=str(tmp_path),
        lifecycle_script_path=str(lifecycle_script),
        created_by_user_id=1,
        created_at=now,
        updated_at=now,
        owner_user_ids=(1,),
        action_mappings=(),
        lifecycle_function_decisions=(),
    )

    def raise_timeout(*args: object, **kwargs: object) -> object:
        raise URLError(TimeoutError("timed out"))

    monkeypatch.setattr(windows, "urlopen", raise_timeout)

    snapshot = WindowsRuntimeInspector(reachability_timeout_seconds=0.25).inspect(project)

    assert snapshot.status == "stopped"
    assert snapshot.application_reachable is False
    assert "timed out after 0.25s" in snapshot.status_reason
