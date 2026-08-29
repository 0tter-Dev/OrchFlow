"""Smoke tests for the initial API bootstrap."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from orchflow.external.api.app import create_app


def test_root_returns_bootstrap_metadata() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "OrchFlow",
        "version": "0.2.15",
        "status": "ok",
        "stage": "bootstrap",
    }


def test_health_returns_operational_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_configuration_endpoint_exposes_safe_runtime_summary() -> None:
    client = TestClient(create_app())

    response = client.get("/system/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["environment"] == "development"
    assert payload["database_dialect"] == "sqlite"
    assert payload["api_base_url"] == "http://localhost:8000"


def test_database_endpoint_reports_connectivity() -> None:
    client = TestClient(create_app())

    response = client.get("/system/database")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["is_connected"] is True


def test_auth_flow_registers_bootstrap_admin_and_lists_users(
    isolated_environment: None,
) -> None:
    client = TestClient(create_app())

    register_response = client.post(
        "/auth/register",
        json={"username": "admin-user", "password": "password123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["role"] == "admin"

    login_response = client.post(
        "/auth/login",
        json={"username": "admin-user", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin-user"

    users_response = client.get("/auth/users", headers={"Authorization": f"Bearer {token}"})
    assert users_response.status_code == 200
    assert len(users_response.json()) == 1


def test_audit_history_flow_is_exposed_in_api(isolated_environment: None) -> None:
    client = TestClient(create_app())

    client.post(
        "/auth/register",
        json={"username": "audit-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "audit-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    events_response = client.get(
        "/audit/events?limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert events_response.status_code == 200
    events = events_response.json()
    assert events[0]["action"] == "admin.audit_events.list"
    assert any(event["action"] == "user.login" for event in events)


def test_audit_history_api_requires_admin(isolated_environment: None) -> None:
    client = TestClient(create_app())

    client.post(
        "/auth/register",
        json={"username": "audit-admin", "password": "password123"},
    )
    client.post(
        "/auth/register",
        json={"username": "audit-member", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "audit-member", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    events_response = client.get(
        "/audit/events",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert events_response.status_code == 403


def test_registering_admin_after_bootstrap_requires_admin_token(
    isolated_environment: None,
) -> None:
    client = TestClient(create_app())

    first_user_response = client.post(
        "/auth/register",
        json={"username": "first-admin", "password": "password123"},
    )
    assert first_user_response.status_code == 201

    member_response = client.post(
        "/auth/register",
        json={"username": "plain-member", "password": "password123"},
    )
    assert member_response.status_code == 201
    assert member_response.json()["role"] == "member"

    forbidden_response = client.post(
        "/auth/register",
        json={"username": "forbidden-admin", "password": "password123", "role": "admin"},
    )
    assert forbidden_response.status_code == 403


def test_admin_user_management_flow_is_exposed_in_api(isolated_environment: None) -> None:
    client = TestClient(create_app())

    client.post(
        "/auth/register",
        json={"username": "admin-user", "password": "password123"},
    )
    client.post(
        "/auth/register",
        json={"username": "member-user", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "admin-user", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    users_response = client.get("/auth/users", headers={"Authorization": f"Bearer {token}"})
    member_id = next(
        user["id"] for user in users_response.json() if user["username"] == "member-user"
    )

    update_response = client.patch(
        f"/auth/users/{member_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "admin", "is_active": False},
    )

    assert update_response.status_code == 200
    assert update_response.json()["role"] == "admin"
    assert update_response.json()["is_active"] is False


def test_project_registry_flow_is_exposed_in_api(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "project-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "project-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"INICIAR\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"PARAR\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
            "mappings": [
                {"canonical_action": "start", "script_label": "INICIAR"},
                {"canonical_action": "stop", "script_label": "PARAR"},
            ],
        },
    )
    assert register_response.status_code == 201
    project_id = register_response.json()["id"]

    list_response = client.get("/projects", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["reference_name"] == "api-project"
    assert get_response.json()["lifecycle_configuration_health"] == "complete"


def test_project_registry_api_exposes_partial_lifecycle_configuration(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "partial-project-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "partial-project-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-partial-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-partial-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )

    assert register_response.status_code == 201
    payload = register_response.json()
    assert payload["lifecycle_configuration_health"] == "partial"
    assert payload["action_mappings"] == [
        {
            "canonical_action": "status",
            "script_label": "STATUS",
            "source": "imported",
            "configured_by_user_id": 1,
        }
    ]
    assert {
        configuration["canonical_action"]: configuration["state"]
        for configuration in payload["lifecycle_function_configurations"]
    } == {
        "status": "configured",
        "start": "undefined",
        "stop": "undefined",
        "restart": "undefined",
    }


def test_project_lifecycle_configuration_update_is_exposed_in_api(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "manual-project-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "manual-project-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-manual-project"
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
    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-manual-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    project_id = register_response.json()["id"]

    update_response = client.patch(
        f"/projects/{project_id}/lifecycle-configuration",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "mappings": [{"canonical_action": "start", "script_label": "INICIAR"}],
            "unconfigured_actions": ["stop", "restart"],
        },
    )

    assert update_response.status_code == 200
    payload = update_response.json()
    assert payload["lifecycle_configuration_health"] == "partial"
    assert payload["action_mappings"] == [
        {
            "canonical_action": "start",
            "script_label": "INICIAR",
            "source": "user_defined",
            "configured_by_user_id": 1,
        }
    ]
    assert {
        configuration["canonical_action"]: configuration["state"]
        for configuration in payload["lifecycle_function_configurations"]
    } == {
        "status": "undefined",
        "start": "configured",
        "stop": "unconfigured",
        "restart": "unconfigured",
    }


def test_project_reload_flow_is_exposed_in_api(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "reload-project-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "reload-project-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-reload-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-reload-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    project_id = register_response.json()["id"]
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )

    reload_response = client.post(
        f"/projects/{project_id}/reload",
        headers={"Authorization": f"Bearer {token}"},
    )
    reload_many_response = client.post(
        "/projects/reload",
        headers={"Authorization": f"Bearer {token}"},
        json={"project_ids": [project_id]},
    )

    assert reload_response.status_code == 200
    payload = reload_response.json()
    assert payload["previous_lifecycle_configuration_health"] == "partial"
    assert payload["current_lifecycle_configuration_health"] == "complete"
    assert payload["changed_actions"] == ["start", "stop", "restart"]
    assert payload["project"]["lifecycle_configuration_health"] == "complete"
    assert reload_many_response.status_code == 200
    assert reload_many_response.json()[0]["project"]["id"] == project_id


def test_lifecycle_api_rejects_unconfigured_actions(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "gated-lifecycle-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "gated-lifecycle-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-gated-lifecycle-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "exit /b 1\r\n",
        encoding="utf-8",
    )
    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-gated-lifecycle-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    project_id = register_response.json()["id"]

    lifecycle_response = client.post(
        f"/projects/{project_id}/lifecycle/start",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert lifecycle_response.status_code == 400
    assert "undefined for this project" in lifecycle_response.json()["detail"]


def test_project_owner_management_flow_is_exposed_in_api(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "owner-admin", "password": "password123"},
    )
    client.post(
        "/auth/register",
        json={"username": "owner-member", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "owner-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    users_response = client.get("/auth/users", headers={"Authorization": f"Bearer {token}"})
    member_id = next(
        user["id"] for user in users_response.json() if user["username"] == "owner-member"
    )

    project_dir = tmp_path / "api-owned-project"
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
    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-owned-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    project_id = register_response.json()["id"]

    add_response = client.post(
        f"/projects/{project_id}/owners/{member_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add_response.status_code == 200
    assert member_id in add_response.json()["owner_user_ids"]

    remove_response = client.delete(
        f"/projects/{project_id}/owners/{member_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert remove_response.status_code == 200
    assert member_id not in remove_response.json()["owner_user_ids"]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only batch execution")
def test_lifecycle_flow_is_exposed_in_api(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "lifecycle-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "lifecycle-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-lifecycle-project"
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

    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-lifecycle-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    project_id = register_response.json()["id"]

    lifecycle_response = client.post(
        f"/projects/{project_id}/lifecycle/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert lifecycle_response.status_code == 200
    assert lifecycle_response.json()["succeeded"] is True
    assert "status-ok" in lifecycle_response.json()["stdout"]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-only runtime inspection")
def test_runtime_inspection_is_exposed_in_api(
    isolated_environment: None,
    tmp_path: Path,
) -> None:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": "runtime-admin", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "runtime-admin", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    project_dir = tmp_path / "api-runtime-project"
    project_dir.mkdir()
    lifecycle_script = project_dir / "control.bat"
    lifecycle_script.write_text(
        "@echo off\r\n"
        "set \"APP_PORT=49190\"\r\n"
        "set \"APP_URL=http://localhost:49190\"\r\n"
        "if /I \"%~1\"==\"STATUS\" echo status-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"START\" echo start-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"STOP\" echo stop-ok & exit /b 0\r\n"
        "if /I \"%~1\"==\"RESTART\" echo restart-ok & exit /b 0\r\n"
        "exit /b 0\r\n",
        encoding="utf-8",
    )

    register_response = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "reference_name": "api-runtime-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    project_id = register_response.json()["id"]

    runtime_response = client.get(
        f"/projects/{project_id}/runtime",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert runtime_response.status_code == 200
    payload = runtime_response.json()
    assert payload["known_port"] == 49190
    assert isinstance(payload["application_reachable"], bool)
    assert payload["inspected_at"]
    assert "APP_PORT 49190" in payload["status_reason"]
    assert payload["status"] in {"running", "stopped"}
