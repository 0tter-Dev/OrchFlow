"""Integration tests for runtime inspection."""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from orchflow.application.access_control import LoginCommand, RegisterUserCommand
from orchflow.application.project_registry import RegisterProjectCommand
from orchflow.application.runtime_inspection import InspectRuntimeCommand
from orchflow.application.services import (
    create_access_control_service,
    create_project_registry_service,
    create_runtime_inspection_service,
)

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
        assert len(snapshot.process_snapshots) >= 1
    finally:
        server_process.terminate()
        server_process.wait(timeout=5)
