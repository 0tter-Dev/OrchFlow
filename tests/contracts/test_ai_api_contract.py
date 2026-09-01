"""Focused HTTP contract tests for AI assistance API routes."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from orchflow.application.ai_assistance import AIAssistancePromptMessage
from orchflow.external.api.app import create_app
from orchflow.infrastructure.ai.litellm_gateway import LiteLLMGatewayClient
from orchflow.infrastructure.config.settings import get_settings

AI_ROUTE_REQUESTS: tuple[tuple[str, str, object | None], ...] = (
    ("get", "/ai/status", None),
    ("get", "/ai/gateway/health", None),
    ("get", "/ai/models", None),
    (
        "post",
        "/ai/context-manifests",
        {
            "project_id": 1,
            "selected_model": "ollama/llama3",
            "intended_operation": "improve_lifecycle_script",
        },
    ),
    ("get", "/ai/context-manifests/1", None),
    ("post", "/ai/analysis-proposals", {"manifest_id": 1}),
    ("get", "/ai/analysis-proposals/1", None),
    ("post", "/ai/analysis-proposals/1/review", {"decision": "approved"}),
    ("post", "/ai/analysis-proposals/1/apply", {}),
)

AI_STATUS_KEYS = {
    "provider",
    "status",
    "enabled",
    "mode",
    "base_url",
    "default_model",
    "timeout_seconds",
    "api_key_configured",
    "sdk_available",
    "ready_for_requests",
    "message",
}
AI_HEALTH_KEYS = {
    "provider",
    "status",
    "enabled",
    "mode",
    "base_url",
    "checked",
    "status_code",
    "response_time_ms",
    "message",
}
AI_MODEL_CATALOG_KEYS = {
    "provider",
    "enabled",
    "mode",
    "base_url",
    "default_model",
    "models",
    "supports_discovery",
    "message",
}
AI_MANIFEST_KEYS = {
    "id",
    "project_id",
    "requested_by_user_id",
    "selected_model",
    "intended_operation",
    "project_root_path",
    "include_patterns",
    "exclude_patterns",
    "included_paths",
    "excluded_paths",
    "ignored_paths",
    "secret_filter_rules",
    "max_file_size_bytes",
    "max_total_bytes",
    "total_included_bytes",
    "created_at",
}
AI_PROPOSAL_KEYS = {
    "id",
    "manifest_id",
    "project_id",
    "requested_by_user_id",
    "selected_model",
    "intended_operation",
    "lifecycle_strategy",
    "runtime_hints",
    "candidate_script_content",
    "action_mappings",
    "warnings",
    "created_at",
}
AI_REVIEW_KEYS = {
    "id",
    "proposal_id",
    "project_id",
    "reviewer_user_id",
    "decision",
    "validation_status",
    "validation_errors",
    "reviewer_notes",
    "created_at",
}
AI_APPLICATION_KEYS = {
    "id",
    "proposal_id",
    "project_id",
    "applied_by_user_id",
    "lifecycle_script_path",
    "persisted_mappings",
    "project",
    "created_at",
}


@pytest.fixture
def ai_enabled(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Enable AI assistance settings for contract tests that create proposals."""
    monkeypatch.setenv("ORCHFLOW_AI_ENABLED", "true")
    get_settings.cache_clear()

    try:
        yield
    finally:
        get_settings.cache_clear()


def _proposal_completion() -> str:
    return (
        '{"lifecycle_strategy":"Use first-argument dispatch for every canonical action.",'
        '"runtime_hints":["Keep APP_URL or APP_PORT declared when available."],'
        '"candidate_script_content":"@echo off\\r\\nif /I \\"%~1\\"==\\"STATUS\\" '
        'echo status-ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"START\\" '
        'echo start-ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"STOP\\" '
        'echo stop-ok & exit /b 0\\r\\nif /I \\"%~1\\"==\\"RESTART\\" '
        'echo restart-ok & exit /b 0\\r\\n",'
        '"action_mappings":[{"canonical_action":"status","script_label":"STATUS",'
        '"rationale":"Use the canonical status handler."}],'
        '"warnings":["Review before applying."]}'
    )


def _client_and_token(username: str) -> tuple[TestClient, str]:
    client = TestClient(create_app())
    client.post(
        "/auth/register",
        json={"username": username, "password": "password123"},
    )
    login_response = client.post(
        "/auth/login",
        json={"username": username, "password": "password123"},
    )
    return client, login_response.json()["access_token"]


def _register_project(client: TestClient, token: str, tmp_path: Path) -> int:
    project_dir = tmp_path / "ai-api-contract-project"
    project_dir.mkdir()
    (project_dir / "app.py").write_text("print('contract context')\n", encoding="utf-8")
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
            "reference_name": "ai-api-contract-project",
            "project_root_path": str(project_dir),
            "lifecycle_script_path": str(lifecycle_script),
        },
    )
    return int(register_response.json()["id"])


def test_ai_routes_require_bearer_authentication(isolated_environment: None) -> None:
    client = TestClient(create_app())

    for method, path, json_payload in AI_ROUTE_REQUESTS:
        response = client.request(method, path, json=json_payload)

        assert response.status_code == 401
        assert response.json() == {"detail": "Missing bearer token."}


def test_ai_routes_reject_non_bearer_authorization_scheme(
    isolated_environment: None,
) -> None:
    client = TestClient(create_app())

    response = client.get("/ai/status", headers={"Authorization": "Token bad"})

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authorization header must use the Bearer scheme."
    }


def test_ai_safe_gateway_routes_return_stable_disabled_contracts(
    isolated_environment: None,
) -> None:
    client, token = _client_and_token("ai-contract-status-user")
    headers = {"Authorization": f"Bearer {token}"}

    status_response = client.get("/ai/status", headers=headers)
    health_response = client.get("/ai/gateway/health", headers=headers)
    models_response = client.get("/ai/models", headers=headers)

    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert set(status_payload) == AI_STATUS_KEYS
    assert status_payload["provider"] == "litellm"
    assert status_payload["status"] == "disabled"
    assert status_payload["ready_for_requests"] is False

    assert health_response.status_code == 200
    health_payload = health_response.json()
    assert set(health_payload) == AI_HEALTH_KEYS
    assert health_payload["status"] == "disabled"
    assert health_payload["checked"] is False

    assert models_response.status_code == 200
    models_payload = models_response.json()
    assert set(models_payload) == AI_MODEL_CATALOG_KEYS
    assert models_payload["supports_discovery"] is False
    assert models_payload["models"] == []


@pytest.mark.parametrize(
    ("path", "payload", "required_field"),
    [
        ("/ai/context-manifests", {}, "project_id"),
        ("/ai/analysis-proposals", {}, "manifest_id"),
        ("/ai/analysis-proposals/1/review", {}, "decision"),
    ],
)
def test_ai_mutation_routes_expose_fastapi_validation_contract(
    isolated_environment: None,
    path: str,
    payload: dict[str, object],
    required_field: str,
) -> None:
    client, token = _client_and_token(f"ai-contract-validation-{required_field}")

    response = client.post(
        path,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

    assert response.status_code == 422
    assert any(
        error["loc"][-1] == required_field
        for error in response.json()["detail"]
    )


def test_ai_manifest_proposal_review_and_apply_routes_keep_response_contracts(
    isolated_environment: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ai_enabled: None,
) -> None:
    def fake_generate_completion(
        self: LiteLLMGatewayClient,
        *,
        model: str,
        messages: tuple[AIAssistancePromptMessage, ...],
    ) -> str:
        assert model == "ollama/llama3"
        assert "contract context" in messages[1].content
        return _proposal_completion()

    monkeypatch.setattr(
        LiteLLMGatewayClient,
        "generate_completion",
        fake_generate_completion,
    )
    client, token = _client_and_token("ai-contract-flow-user")
    headers = {"Authorization": f"Bearer {token}"}
    project_id = _register_project(client, token, tmp_path)

    manifest_response = client.post(
        "/ai/context-manifests",
        headers=headers,
        json={
            "project_id": project_id,
            "selected_model": "ollama/llama3",
            "intended_operation": "improve_lifecycle_script",
            "include_patterns": ["app.py"],
        },
    )
    assert manifest_response.status_code == 201
    manifest = manifest_response.json()
    assert set(manifest) == AI_MANIFEST_KEYS
    assert manifest["included_paths"] == ["app.py"]

    proposal_response = client.post(
        "/ai/analysis-proposals",
        headers=headers,
        json={"manifest_id": manifest["id"], "user_instructions": "Keep it auditable."},
    )
    assert proposal_response.status_code == 201
    proposal = proposal_response.json()
    assert set(proposal) == AI_PROPOSAL_KEYS
    assert proposal["manifest_id"] == manifest["id"]
    assert proposal["action_mappings"][0] == {
        "canonical_action": "status",
        "script_label": "STATUS",
        "rationale": "Use the canonical status handler.",
    }

    review_response = client.post(
        f"/ai/analysis-proposals/{proposal['id']}/review",
        headers=headers,
        json={"decision": "approved", "reviewer_notes": "Looks valid."},
    )
    assert review_response.status_code == 201
    review = review_response.json()
    assert set(review) == AI_REVIEW_KEYS
    assert review["validation_status"] == "valid"
    assert review["validation_errors"] == []

    apply_response = client.post(
        f"/ai/analysis-proposals/{proposal['id']}/apply",
        headers=headers,
        json={"confirm_file_write": True, "confirm_mapping_persistence": True},
    )
    assert apply_response.status_code == 201
    application = apply_response.json()
    assert set(application) == AI_APPLICATION_KEYS
    assert application["proposal_id"] == proposal["id"]
    assert application["project"]["lifecycle_configuration_health"] == "complete"
    assert len(application["persisted_mappings"]) == 4


def test_ai_apply_route_requires_explicit_confirmations(
    isolated_environment: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ai_enabled: None,
) -> None:
    monkeypatch.setattr(
        LiteLLMGatewayClient,
        "generate_completion",
        lambda self, *, model, messages: _proposal_completion(),
    )
    client, token = _client_and_token("ai-contract-confirmation-user")
    headers = {"Authorization": f"Bearer {token}"}
    project_id = _register_project(client, token, tmp_path)
    manifest_response = client.post(
        "/ai/context-manifests",
        headers=headers,
        json={
            "project_id": project_id,
            "selected_model": "ollama/llama3",
            "intended_operation": "improve_lifecycle_script",
            "include_patterns": ["app.py"],
        },
    )
    proposal_response = client.post(
        "/ai/analysis-proposals",
        headers=headers,
        json={"manifest_id": manifest_response.json()["id"]},
    )
    proposal_id = proposal_response.json()["id"]
    client.post(
        f"/ai/analysis-proposals/{proposal_id}/review",
        headers=headers,
        json={"decision": "approved"},
    )

    apply_response = client.post(
        f"/ai/analysis-proposals/{proposal_id}/apply",
        headers=headers,
        json={},
    )

    assert apply_response.status_code == 400
    assert apply_response.json() == {
        "detail": "Applying an AI proposal requires explicit file-write confirmation."
    }
