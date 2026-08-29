"""Shared presentation helpers for OrchFlow external adapters."""

from orchflow.application.project_registry import unconfigured_actions_for_project
from orchflow.domain.access_control import AuditEvent, User
from orchflow.domain.lifecycle import LifecycleExecutionResult
from orchflow.domain.lifecycle_function_model import (
    build_lifecycle_function_configurations,
    derive_project_configuration_health,
)
from orchflow.domain.project_registry import Project
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot


def render_user(user: User) -> str:
    """Render a user into a simple CLI-friendly representation."""
    return (
        f"id: {user.id}\n"
        f"username: {user.username}\n"
        f"role: {user.role.value}\n"
        f"is_active: {str(user.is_active).lower()}"
    )


def render_audit_event(event: AuditEvent) -> str:
    """Render an audit event for CLI output."""
    return (
        f"id: {event.id}\n"
        f"actor_user_id: {event.actor_user_id}\n"
        f"action: {event.action}\n"
        f"target_type: {event.target_type}\n"
        f"target_id: {event.target_id}\n"
        f"details: {event.details or ''}\n"
        f"created_at: {event.created_at.isoformat()}"
    )


def render_project(project: Project) -> str:
    """Render a project into a simple CLI-friendly representation."""
    lifecycle_function_configurations = build_lifecycle_function_configurations(
        {
            mapping.canonical_action: mapping.script_label
            for mapping in project.action_mappings
        },
        unconfigured_actions_for_project(project),
    )
    lifecycle_configuration_health = derive_project_configuration_health(
        lifecycle_function_configurations
    )
    mapping_lines = (
        "\n".join(
            f"{mapping.canonical_action.value}: {mapping.script_label} ({mapping.source.value})"
            for mapping in project.action_mappings
        )
        if project.action_mappings
        else "none"
    )
    function_configuration_lines = "\n".join(
        (
            f"{configuration.action.value}: {configuration.state.value}"
            f"{f' -> {configuration.script_label}' if configuration.script_label else ''}"
        )
        for configuration in lifecycle_function_configurations
    )
    owners = ", ".join(str(owner_user_id) for owner_user_id in project.owner_user_ids)
    return (
        f"id: {project.id}\n"
        f"reference_name: {project.reference_name}\n"
        f"description: {project.description or ''}\n"
        f"project_root_path: {project.project_root_path}\n"
        f"lifecycle_script_path: {project.lifecycle_script_path}\n"
        f"created_by_user_id: {project.created_by_user_id}\n"
        f"owner_user_ids: {owners}\n"
        f"lifecycle_configuration_health: {lifecycle_configuration_health.value}\n"
        f"action_mappings:\n{mapping_lines}\n"
        f"lifecycle_function_configurations:\n{function_configuration_lines}"
    )


def render_lifecycle_result(result: LifecycleExecutionResult) -> str:
    """Render a lifecycle execution result for CLI output."""
    runtime_summary = (
        f"\nruntime_status: {result.runtime_snapshot.status}"
        if result.runtime_snapshot is not None
        else ""
    )
    return (
        f"project_id: {result.project_id}\n"
        f"canonical_action: {result.canonical_action.value}\n"
        f"command_identifier: {result.command_identifier}\n"
        f"exit_code: {result.exit_code}\n"
        f"succeeded: {str(result.succeeded).lower()}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
        f"{runtime_summary}"
    )


def render_runtime_snapshot(snapshot: RuntimeInspectionSnapshot) -> str:
    """Render runtime inspection data for CLI output."""
    process_lines = (
        "\n".join(
            (
                f"pid={process.pid},"
                f"name={process.name},"
                f"cpu_seconds={process.cpu_seconds},"
                f"memory_bytes={process.memory_bytes},"
                f"started_at={process.started_at}"
            )
            for process in snapshot.process_snapshots
        )
        if snapshot.process_snapshots
        else "none"
    )
    return (
        f"project_id: {snapshot.project_id}\n"
        f"status: {snapshot.status}\n"
        f"status_reason: {snapshot.status_reason}\n"
        f"known_port: {snapshot.known_port}\n"
        f"application_url: {snapshot.application_url}\n"
        f"application_reachable: {snapshot.application_reachable}\n"
        f"uptime_seconds: {snapshot.uptime_seconds}\n"
        f"inspected_at: {snapshot.inspected_at.isoformat()}\n"
        f"processes:\n{process_lines}"
    )
