"""Application service for lifecycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orchflow.application.project_registry import (
    CurrentUserResolver,
    ProjectRegistryService,
    unconfigured_actions_for_project,
)
from orchflow.domain.lifecycle import LifecycleExecutionResult
from orchflow.domain.project_registry import CanonicalLifecycleAction, Project
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot


class LifecycleOrchestrationError(Exception):
    """Base exception for lifecycle orchestration failures."""


class LifecycleExecutionError(LifecycleOrchestrationError):
    """Raised when a lifecycle command fails during execution."""

    def __init__(self, result: LifecycleExecutionResult) -> None:
        super().__init__(
            f"Lifecycle action '{result.canonical_action.value}' failed with exit code "
            f"{result.exit_code}."
        )
        self.result = result


class LifecycleActionConfigurationError(LifecycleOrchestrationError):
    """Raised when a lifecycle action is not configured for execution."""


@dataclass(frozen=True, slots=True)
class ExecuteLifecycleCommand:
    """Input required to execute a lifecycle action."""

    token: str
    project_id: int
    action: CanonicalLifecycleAction


class ProjectLifecycleAdapter(Protocol):
    """Adapter boundary for executing lifecycle actions against a project."""

    def execute(
        self,
        project: Project,
        action: CanonicalLifecycleAction,
    ) -> LifecycleExecutionResult: ...


class LifecycleAuditRecorder(Protocol):
    """Boundary used to record audit events for lifecycle actions."""

    def record_audit_event(
        self,
        *,
        actor_user_id: int,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None: ...


class RuntimeInspector(Protocol):
    """Boundary used to inspect runtime state after lifecycle execution."""

    def inspect(self, project: Project) -> RuntimeInspectionSnapshot: ...


class LifecycleOrchestrationService:
    """Application-layer service for lifecycle execution."""

    def __init__(
        self,
        project_registry_service: ProjectRegistryService,
        current_user_resolver: CurrentUserResolver,
        adapter: ProjectLifecycleAdapter,
        audit_recorder: LifecycleAuditRecorder,
        runtime_inspector: RuntimeInspector | None = None,
    ) -> None:
        self._project_registry_service = project_registry_service
        self._current_user_resolver = current_user_resolver
        self._adapter = adapter
        self._audit_recorder = audit_recorder
        self._runtime_inspector = runtime_inspector

    def execute_action(self, command: ExecuteLifecycleCommand) -> LifecycleExecutionResult:
        """Execute a lifecycle action against a visible project."""
        actor = self._current_user_resolver.get_current_user(command.token)
        project = self._project_registry_service.get_project(command.token, command.project_id)
        if self._resolve_configured_command_identifier(
            project,
            command.action,
        ) is None:
            reason = self._unconfigured_action_reason(project, command.action)
            self._audit_recorder.record_audit_event(
                actor_user_id=actor.id,
                action=f"lifecycle.{command.action.value}.blocked",
                target_type="project",
                target_id=str(project.id),
                details=f"reason:{reason}",
            )
            raise LifecycleActionConfigurationError(
                f"Lifecycle action '{command.action.value}' cannot be executed because "
                f"{reason}."
            )

        base_result = self._adapter.execute(project, command.action)
        runtime_snapshot = (
            self._runtime_inspector.inspect(project)
            if self._runtime_inspector is not None
            else None
        )
        result = LifecycleExecutionResult(
            project_id=base_result.project_id,
            canonical_action=base_result.canonical_action,
            command_identifier=base_result.command_identifier,
            exit_code=base_result.exit_code,
            stdout=base_result.stdout,
            stderr=base_result.stderr,
            succeeded=base_result.succeeded,
            started_at=base_result.started_at,
            finished_at=base_result.finished_at,
            runtime_snapshot=runtime_snapshot,
        )
        details = (
            f"identifier:{result.command_identifier};"
            f"exit_code:{result.exit_code};"
            f"succeeded:{str(result.succeeded).lower()}"
        )
        if runtime_snapshot is not None:
            details = f"{details};runtime_status:{runtime_snapshot.status}"
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action=f"lifecycle.{command.action.value}",
            target_type="project",
            target_id=str(project.id),
            details=details,
        )
        if not result.succeeded:
            raise LifecycleExecutionError(result)
        return result

    @staticmethod
    def _resolve_configured_command_identifier(
        project: Project,
        action: CanonicalLifecycleAction,
    ) -> str | None:
        for mapping in project.action_mappings:
            if mapping.canonical_action is action:
                return mapping.script_label
        return None

    @staticmethod
    def _unconfigured_action_reason(project: Project, action: CanonicalLifecycleAction) -> str:
        if not project.action_mappings:
            return "the project has no configured lifecycle functions"
        if action in unconfigured_actions_for_project(project):
            return "the action is explicitly marked as unconfigured"
        return "the action is undefined for this project"
