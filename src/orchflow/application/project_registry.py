"""Application service for project registration and normalized project definitions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from orchflow.application.access_control import AuthorizationError
from orchflow.domain.access_control import User
from orchflow.domain.project_registry import (
    CanonicalLifecycleAction,
    MappingSource,
    Project,
)


class ProjectRegistryError(Exception):
    """Base exception for project registry application failures."""


class ProjectConflictError(ProjectRegistryError):
    """Raised when a project registration conflicts with existing state."""


class ProjectValidationError(ProjectRegistryError):
    """Raised when a project registration request is invalid."""


@dataclass(frozen=True, slots=True)
class ProjectMappingInput:
    """Input used to define a lifecycle action mapping during registration."""

    canonical_action: CanonicalLifecycleAction
    script_label: str
    source: MappingSource = MappingSource.USER_DEFINED


@dataclass(frozen=True, slots=True)
class RegisterProjectCommand:
    """Input required to register a project into OrchFlow."""

    token: str
    reference_name: str
    project_root_path: str
    lifecycle_script_path: str
    description: str | None = None
    mappings: tuple[ProjectMappingInput, ...] = ()


class ProjectRegistryRepository(Protocol):
    """Repository boundary for project registry use cases."""

    def get_project_by_reference_name(self, reference_name: str) -> Project | None: ...

    def create_project(
        self,
        *,
        reference_name: str,
        description: str | None,
        project_root_path: str,
        lifecycle_script_path: str,
        created_by_user_id: int,
        owner_user_ids: tuple[int, ...],
        mappings: tuple[ProjectMappingInput, ...],
    ) -> Project: ...

    def list_projects_for_user(self, user: User) -> list[Project]: ...

    def get_project_for_user(self, project_id: int, user: User) -> Project | None: ...

    def record_audit_event(
        self,
        *,
        actor_user_id: int,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None: ...


class CurrentUserResolver(Protocol):
    """Boundary used to resolve the current authenticated user."""

    def get_current_user(self, token: str) -> User: ...


class ProjectRegistryService:
    """Application-layer service for project registration and visibility."""

    def __init__(
        self,
        repository: ProjectRegistryRepository,
        current_user_resolver: CurrentUserResolver,
    ) -> None:
        self._repository = repository
        self._current_user_resolver = current_user_resolver

    def register_project(self, command: RegisterProjectCommand) -> Project:
        """Register a normalized project definition."""
        actor = self._current_user_resolver.get_current_user(command.token)
        reference_name = command.reference_name.strip()
        if len(reference_name) < 3:
            raise ProjectValidationError(
                "Project reference name must contain at least 3 characters."
            )

        if self._repository.get_project_by_reference_name(reference_name) is not None:
            raise ProjectConflictError(f"Project '{reference_name}' already exists.")

        project_root_path = self._normalize_directory_path(command.project_root_path)
        lifecycle_script_path = self._normalize_file_path(command.lifecycle_script_path)
        self._validate_lifecycle_script(project_root_path, lifecycle_script_path)
        mappings = self._normalize_mappings(command.mappings)

        project = self._repository.create_project(
            reference_name=reference_name,
            description=command.description.strip() if command.description else None,
            project_root_path=project_root_path,
            lifecycle_script_path=lifecycle_script_path,
            created_by_user_id=actor.id,
            owner_user_ids=(actor.id,),
            mappings=mappings,
        )
        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.register",
            target_type="project",
            target_id=str(project.id),
            details=f"reference_name:{project.reference_name}",
        )
        return project

    def list_projects(self, token: str) -> list[Project]:
        """List the projects visible to the current user."""
        actor = self._current_user_resolver.get_current_user(token)
        projects = self._repository.list_projects_for_user(actor)
        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.list",
            target_type="project",
            target_id=None,
            details=f"project-count:{len(projects)}",
        )
        return projects

    def get_project(self, token: str, project_id: int) -> Project:
        """Get a single project visible to the current user."""
        actor = self._current_user_resolver.get_current_user(token)
        project = self._repository.get_project_for_user(project_id, actor)
        if project is None:
            raise AuthorizationError("Project is not visible to the current user.")
        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.read",
            target_type="project",
            target_id=str(project.id),
            details=f"reference_name:{project.reference_name}",
        )
        return project

    @staticmethod
    def _normalize_directory_path(raw_path: str) -> str:
        path = Path(raw_path).expanduser()
        return str(path.resolve())

    @staticmethod
    def _normalize_file_path(raw_path: str) -> str:
        path = Path(raw_path).expanduser()
        return str(path.resolve())

    @staticmethod
    def _validate_lifecycle_script(project_root_path: str, lifecycle_script_path: str) -> None:
        project_root = Path(project_root_path)
        lifecycle_script = Path(lifecycle_script_path)
        if not project_root.exists() or not project_root.is_dir():
            raise ProjectValidationError("Project root path must point to an existing directory.")
        if not lifecycle_script.exists() or not lifecycle_script.is_file():
            raise ProjectValidationError("Lifecycle script path must point to an existing file.")
        if lifecycle_script.suffix.lower() != ".bat":
            raise ProjectValidationError("Lifecycle script path must reference a '.bat' file.")

    @staticmethod
    def _normalize_mappings(
        mappings: tuple[ProjectMappingInput, ...],
    ) -> tuple[ProjectMappingInput, ...]:
        seen_actions: set[CanonicalLifecycleAction] = set()
        normalized: list[ProjectMappingInput] = []
        for mapping in mappings:
            script_label = mapping.script_label.strip()
            if not script_label:
                raise ProjectValidationError(
                    "Lifecycle action mappings must include a script label."
                )
            if mapping.canonical_action in seen_actions:
                raise ProjectValidationError(
                    f"Duplicate mapping for canonical action '{mapping.canonical_action.value}'."
                )
            seen_actions.add(mapping.canonical_action)
            normalized.append(
                ProjectMappingInput(
                    canonical_action=mapping.canonical_action,
                    script_label=script_label,
                    source=mapping.source,
                )
            )
        return tuple(normalized)
