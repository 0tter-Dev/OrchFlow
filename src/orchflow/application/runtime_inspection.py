"""Application service for runtime inspection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orchflow.application.project_registry import CurrentUserResolver, ProjectRegistryService
from orchflow.domain.project_registry import Project
from orchflow.domain.runtime_inspection import RuntimeInspectionSnapshot


class RuntimeInspectionError(Exception):
    """Base exception for runtime inspection failures."""


@dataclass(frozen=True, slots=True)
class InspectRuntimeCommand:
    """Input required to inspect a project's runtime state."""

    token: str
    project_id: int


@dataclass(frozen=True, slots=True)
class InspectRuntimeBatchCommand:
    """Input required to inspect many visible projects in sequence."""

    token: str
    project_ids: tuple[int, ...]


class RuntimeInspector(Protocol):
    """Boundary used to inspect a project's runtime state."""

    def inspect(self, project: Project) -> RuntimeInspectionSnapshot: ...


class RuntimeInspectionService:
    """Application-layer service for runtime inspection."""

    def __init__(
        self,
        project_registry_service: ProjectRegistryService,
        current_user_resolver: CurrentUserResolver,
        inspector: RuntimeInspector,
    ) -> None:
        self._project_registry_service = project_registry_service
        self._current_user_resolver = current_user_resolver
        self._inspector = inspector

    def inspect_runtime(self, command: InspectRuntimeCommand) -> RuntimeInspectionSnapshot:
        """Inspect runtime data for a project visible to the current user."""
        _ = self._current_user_resolver.get_current_user(command.token)
        project = self._project_registry_service.get_project(command.token, command.project_id)
        return self._inspector.inspect(project)

    def inspect_runtime_batch(
        self,
        command: InspectRuntimeBatchCommand,
    ) -> list[RuntimeInspectionSnapshot]:
        """Inspect runtime data for many projects visible to the current user."""
        _ = self._current_user_resolver.get_current_user(command.token)
        snapshots: list[RuntimeInspectionSnapshot] = []
        seen_project_ids: set[int] = set()
        for project_id in command.project_ids:
            if project_id in seen_project_ids:
                continue
            seen_project_ids.add(project_id)
            project = self._project_registry_service.get_project(command.token, project_id)
            snapshots.append(self._inspector.inspect(project))
        return snapshots
