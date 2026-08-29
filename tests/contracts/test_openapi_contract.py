"""OpenAPI contract coverage for public OrchFlow API routes."""

from orchflow.external.api.app import create_app


def test_openapi_contract_exposes_current_operator_routes() -> None:
    schema = create_app().openapi()
    paths = schema["paths"]

    expected_operations = [
        ("/auth/login", "post"),
        ("/auth/me", "get"),
        ("/auth/users", "get"),
        ("/auth/users/{user_id}", "patch"),
        ("/audit/events", "get"),
        ("/projects", "get"),
        ("/projects", "post"),
        ("/projects/{project_id}", "get"),
        ("/projects/{project_id}/lifecycle-configuration", "patch"),
        ("/projects/{project_id}/lifecycle/{action}", "post"),
        ("/projects/{project_id}/owners/{user_id}", "post"),
        ("/projects/{project_id}/owners/{user_id}", "delete"),
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
