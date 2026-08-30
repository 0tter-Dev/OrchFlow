"""OpenAPI contract coverage for public OrchFlow API routes."""

from orchflow.external.api.app import create_app


def test_openapi_contract_exposes_current_operator_routes() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]

    expected_operations = [
        ("/ai/analysis-proposals", "post"),
        ("/ai/analysis-proposals/{proposal_id}", "get"),
        ("/ai/context-manifests", "post"),
        ("/ai/context-manifests/{manifest_id}", "get"),
        ("/ai/gateway/health", "get"),
        ("/ai/models", "get"),
        ("/ai/status", "get"),
        ("/auth/login", "post"),
        ("/auth/me", "get"),
        ("/auth/users", "get"),
        ("/auth/users/{user_id}", "patch"),
        ("/audit/events", "get"),
        ("/projects", "get"),
        ("/projects", "post"),
        ("/projects/reload", "post"),
        ("/projects/{project_id}", "get"),
        ("/projects/{project_id}/lifecycle-configuration", "patch"),
        ("/projects/{project_id}/lifecycle/{action}", "post"),
        ("/projects/{project_id}/owners/{user_id}", "post"),
        ("/projects/{project_id}/owners/{user_id}", "delete"),
        ("/projects/{project_id}/reload", "post"),
        ("/projects/{project_id}/runtime", "get"),
    ]

    for path, method in expected_operations:
        assert method in paths[path]


def test_runtime_openapi_contract_includes_refined_diagnostics() -> None:
    schema = create_app().openapi()
    runtime_schema = schema["components"]["schemas"]["RuntimeInspectionResponse"]
    runtime_properties = runtime_schema["properties"]

    assert "status_reason" in runtime_properties
    assert "application_reachable" in runtime_properties
    assert "inspected_at" in runtime_properties


def test_project_openapi_contract_includes_ownership_metadata() -> None:
    schema = create_app().openapi()
    project_schema = schema["components"]["schemas"]["ProjectResponse"]
    project_properties = project_schema["properties"]

    assert "owner_user_ids" in project_properties
    assert "created_by_user_id" in project_properties


def test_project_openapi_contract_includes_lifecycle_configuration_metadata() -> None:
    schema = create_app().openapi()
    project_schema = schema["components"]["schemas"]["ProjectResponse"]
    project_properties = project_schema["properties"]

    assert "lifecycle_configuration_health" in project_properties
    assert "lifecycle_function_configurations" in project_properties


def test_project_reload_openapi_contract_includes_change_metadata() -> None:
    schema = create_app().openapi()
    reload_schema = schema["components"]["schemas"]["ProjectReloadResponse"]
    reload_properties = reload_schema["properties"]

    assert "project" in reload_properties
    assert "previous_lifecycle_configuration_health" in reload_properties
    assert "current_lifecycle_configuration_health" in reload_properties
    assert "changed_actions" in reload_properties


def test_ai_assistance_openapi_contract_includes_safe_gateway_status() -> None:
    schema = create_app().openapi()
    ai_status_schema = schema["components"]["schemas"]["AIAssistanceStatusResponse"]
    ai_status_properties = ai_status_schema["properties"]

    assert "provider" in ai_status_properties
    assert "status" in ai_status_properties
    assert "ready_for_requests" in ai_status_properties
    assert "api_key_configured" in ai_status_properties


def test_ai_assistance_openapi_contract_includes_health_and_model_discovery() -> None:
    schema = create_app().openapi()
    health_properties = schema["components"]["schemas"][
        "AIAssistanceGatewayHealthResponse"
    ]["properties"]
    catalog_properties = schema["components"]["schemas"][
        "AIAssistanceModelCatalogResponse"
    ]["properties"]

    assert "checked" in health_properties
    assert "status_code" in health_properties
    assert "response_time_ms" in health_properties
    assert "models" in catalog_properties
    assert "supports_discovery" in catalog_properties


def test_ai_assistance_openapi_contract_includes_authorized_context_manifest() -> None:
    schema = create_app().openapi()
    manifest_properties = schema["components"]["schemas"][
        "AuthorizedContextManifestResponse"
    ]["properties"]

    assert "project_id" in manifest_properties
    assert "selected_model" in manifest_properties
    assert "included_paths" in manifest_properties
    assert "ignored_paths" in manifest_properties
    assert "secret_filter_rules" in manifest_properties


def test_ai_assistance_openapi_contract_includes_analysis_proposal() -> None:
    schema = create_app().openapi()
    proposal_properties = schema["components"]["schemas"][
        "AIAnalysisProposalResponse"
    ]["properties"]

    assert "manifest_id" in proposal_properties
    assert "lifecycle_strategy" in proposal_properties
    assert "runtime_hints" in proposal_properties
    assert "candidate_script_content" in proposal_properties
    assert "action_mappings" in proposal_properties
    assert "warnings" in proposal_properties
