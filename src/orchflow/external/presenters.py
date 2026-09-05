"""Shared presentation helpers for OrchFlow external adapters."""

from orchflow.application.ai_assistance import (
    AIAnalysisProposal,
    AIAnalysisProposalApplication,
    AIAnalysisProposalReview,
    AIAssistanceGatewayHealth,
    AIAssistanceModelCatalog,
    AIAssistanceStatus,
    AuthorizedContextManifest,
)
from orchflow.application.project_registry import (
    ProjectReloadResult,
    ProjectUnlinkResult,
    unconfigured_actions_for_project,
)
from orchflow.domain.access_control import AuditEvent, User
from orchflow.domain.lifecycle import LifecycleExecutionResult
from orchflow.domain.lifecycle_function_model import (
    build_lifecycle_function_configurations,
    derive_project_configuration_health,
)
from orchflow.domain.project_registry import Project
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot
from orchflow.domain.user_preferences import UserPreferences


def render_user(user: User) -> str:
    """Render a user into a simple CLI-friendly representation."""
    return (
        f"id: {user.id}\n"
        f"username: {user.username}\n"
        f"role: {user.role.value}\n"
        f"is_active: {str(user.is_active).lower()}"
    )


def render_user_preferences(preferences: UserPreferences) -> str:
    """Render user preferences into a simple CLI-friendly representation."""
    return (
        f"user_id: {preferences.user_id}\n"
        f"locale: {preferences.locale.value}\n"
        f"project_view_mode: {preferences.project_view_mode.value}\n"
        "status_refresh_interval_seconds: "
        f"{preferences.status_refresh_interval_seconds}"
    )


def render_ai_assistance_status(status: AIAssistanceStatus) -> str:
    """Render AI assistance status for CLI output."""
    return (
        f"provider: {status.provider}\n"
        f"status: {status.status}\n"
        f"enabled: {str(status.enabled).lower()}\n"
        f"mode: {status.mode}\n"
        f"base_url: {status.base_url}\n"
        f"default_model: {status.default_model}\n"
        f"timeout_seconds: {status.timeout_seconds}\n"
        f"api_key_configured: {str(status.api_key_configured).lower()}\n"
        f"sdk_available: {str(status.sdk_available).lower()}\n"
        f"ready_for_requests: {str(status.ready_for_requests).lower()}\n"
        f"message: {status.message}"
    )


def render_ai_assistance_gateway_health(health: AIAssistanceGatewayHealth) -> str:
    """Render AI assistance gateway health for CLI output."""
    return (
        f"provider: {health.provider}\n"
        f"status: {health.status}\n"
        f"enabled: {str(health.enabled).lower()}\n"
        f"mode: {health.mode}\n"
        f"base_url: {health.base_url}\n"
        f"checked: {str(health.checked).lower()}\n"
        f"status_code: {health.status_code}\n"
        f"response_time_ms: {health.response_time_ms}\n"
        f"message: {health.message}"
    )


def render_ai_assistance_model_catalog(catalog: AIAssistanceModelCatalog) -> str:
    """Render AI assistance model discovery for CLI output."""
    model_lines = (
        "\n".join(
            f"{model.id}{f' ({model.owned_by})' if model.owned_by else ''}"
            for model in catalog.models
        )
        if catalog.models
        else "none"
    )
    return (
        f"provider: {catalog.provider}\n"
        f"enabled: {str(catalog.enabled).lower()}\n"
        f"mode: {catalog.mode}\n"
        f"base_url: {catalog.base_url}\n"
        f"default_model: {catalog.default_model}\n"
        f"supports_discovery: {str(catalog.supports_discovery).lower()}\n"
        f"message: {catalog.message}\n"
        f"models:\n{model_lines}"
    )


def render_authorized_context_manifest(manifest: AuthorizedContextManifest) -> str:
    """Render an authorized AI context manifest for CLI output."""
    return (
        f"id: {manifest.id}\n"
        f"project_id: {manifest.project_id}\n"
        f"requested_by_user_id: {manifest.requested_by_user_id}\n"
        f"selected_model: {manifest.selected_model}\n"
        f"intended_operation: {manifest.intended_operation}\n"
        f"project_root_path: {manifest.project_root_path}\n"
        f"include_patterns: {', '.join(manifest.include_patterns)}\n"
        f"exclude_patterns: {', '.join(manifest.exclude_patterns)}\n"
        f"included_paths: {', '.join(manifest.included_paths) or 'none'}\n"
        f"excluded_paths: {', '.join(manifest.excluded_paths) or 'none'}\n"
        f"ignored_paths: {', '.join(manifest.ignored_paths) or 'none'}\n"
        f"secret_filter_rules: {', '.join(manifest.secret_filter_rules)}\n"
        f"max_file_size_bytes: {manifest.max_file_size_bytes}\n"
        f"max_total_bytes: {manifest.max_total_bytes}\n"
        f"total_included_bytes: {manifest.total_included_bytes}\n"
        f"created_at: {manifest.created_at.isoformat()}"
    )


def render_ai_analysis_proposal(proposal: AIAnalysisProposal) -> str:
    """Render a reviewable AI analysis proposal for CLI output."""
    runtime_hints = ", ".join(proposal.runtime_hints) or "none"
    warnings = ", ".join(proposal.warnings) or "none"
    mappings = (
        "\n".join(
            (
                f"{mapping.canonical_action}: {mapping.script_label}"
                f"{f' ({mapping.rationale})' if mapping.rationale else ''}"
            )
            for mapping in proposal.action_mappings
        )
        if proposal.action_mappings
        else "none"
    )
    return (
        f"id: {proposal.id}\n"
        f"manifest_id: {proposal.manifest_id}\n"
        f"project_id: {proposal.project_id}\n"
        f"requested_by_user_id: {proposal.requested_by_user_id}\n"
        f"selected_model: {proposal.selected_model}\n"
        f"intended_operation: {proposal.intended_operation}\n"
        f"lifecycle_strategy: {proposal.lifecycle_strategy}\n"
        f"runtime_hints: {runtime_hints}\n"
        f"warnings: {warnings}\n"
        f"action_mappings:\n{mappings}\n"
        f"candidate_script_content:\n{proposal.candidate_script_content}\n"
        f"created_at: {proposal.created_at.isoformat()}"
    )


def render_ai_analysis_proposal_review(review: AIAnalysisProposalReview) -> str:
    """Render a human review decision for CLI output."""
    validation_errors = ", ".join(review.validation_errors) or "none"
    return (
        f"id: {review.id}\n"
        f"proposal_id: {review.proposal_id}\n"
        f"project_id: {review.project_id}\n"
        f"reviewer_user_id: {review.reviewer_user_id}\n"
        f"decision: {review.decision}\n"
        f"validation_status: {review.validation_status}\n"
        f"validation_errors: {validation_errors}\n"
        f"reviewer_notes: {review.reviewer_notes or ''}\n"
        f"created_at: {review.created_at.isoformat()}"
    )


def render_ai_analysis_proposal_application(
    application: AIAnalysisProposalApplication,
) -> str:
    """Render an approved AI analysis proposal application for CLI output."""
    mappings = (
        "\n".join(
            f"{mapping.canonical_action}: {mapping.script_label}"
            for mapping in application.persisted_mappings
        )
        if application.persisted_mappings
        else "none"
    )
    project_details = (
        f"\nproject:\n{render_project(application.project)}"
        if application.project is not None
        else ""
    )
    return (
        f"id: {application.id}\n"
        f"proposal_id: {application.proposal_id}\n"
        f"project_id: {application.project_id}\n"
        f"applied_by_user_id: {application.applied_by_user_id}\n"
        f"lifecycle_script_path: {application.lifecycle_script_path}\n"
        f"persisted_mappings:\n{mappings}\n"
        f"created_at: {application.created_at.isoformat()}"
        f"{project_details}"
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


def render_project_reload_result(result: ProjectReloadResult) -> str:
    """Render a lifecycle configuration reload result for CLI output."""
    changed_actions = (
        ", ".join(action.value for action in result.changed_actions)
        if result.changed_actions
        else "none"
    )
    return (
        f"previous_lifecycle_configuration_health: {result.previous_health.value}\n"
        f"current_lifecycle_configuration_health: {result.current_health.value}\n"
        f"changed_actions: {changed_actions}\n"
        f"{render_project(result.project)}"
    )


def render_project_unlink_result(result: ProjectUnlinkResult) -> str:
    """Render a project unlink result for CLI output."""
    return (
        f"project_id: {result.project_id}\n"
        f"reference_name: {result.reference_name}\n"
        f"project_root_path: {result.project_root_path}\n"
        f"lifecycle_script_path: {result.lifecycle_script_path}\n"
        "local_files_preserved: true\n"
        f"registry_entry_removed: {str(result.registry_entry_removed).lower()}\n"
        f"unlinked_owner_user_id: {result.unlinked_owner_user_id or ''}"
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
