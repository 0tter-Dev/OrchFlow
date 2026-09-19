from fastapi.testclient import TestClient
from typer.testing import CliRunner

from orchflow.external.api.app import create_app
from orchflow.external.cli.app import app


def test_configuration_health_is_safe_and_consistent() -> None:
    api = TestClient(create_app()).get("/system/config/health")
    cli = CliRunner().invoke(app, ["config-health"])

    assert api.status_code == 200
    assert api.json()["status"] in {"ready", "warning"}
    assert api.json()["groups"][-1]["status"] == "disabled"
    assert "change-this-in-local-env" not in str(api.json())
    assert cli.exit_code == 0
    assert f"status: {api.json()['status']}" in cli.stdout
