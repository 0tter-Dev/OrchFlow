"""Application service for project registration and normalized project definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from orchflow.application.access_control import AuthorizationError
from orchflow.domain.access_control import User, UserRole
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


class ProjectOwnershipError(ProjectRegistryError):
    """Raised when project ownership management would violate rules."""


FIRST_ARGUMENT_TOKENS = ("%~1", "%1")
BATCH_LABEL_PREFIX_PATTERN = re.compile(r"^:+")
CANONICAL_ACTIONS = tuple(CanonicalLifecycleAction)


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


@dataclass(frozen=True, slots=True)
class UpdateProjectOwnerCommand:
    """Input required to add or remove a project owner."""

    token: str
    project_id: int
    user_id: int


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

    def add_project_owner(self, *, project_id: int, user_id: int) -> Project | None: ...

    def remove_project_owner(self, *, project_id: int, user_id: int) -> Project | None: ...

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

    def resolve_user(self, user_id: int) -> User | None: ...


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
        mappings = self._normalize_mappings(command.mappings)
        self._validate_lifecycle_script(project_root_path, lifecycle_script_path, mappings)

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

    def add_project_owner(self, command: UpdateProjectOwnerCommand) -> Project:
        """Add a project owner as an authenticated admin."""
        actor = self._current_user_resolver.get_current_user(command.token)
        self._ensure_admin(actor)
        target_user = self._current_user_resolver.resolve_user(command.user_id)
        if target_user is None:
            raise ProjectOwnershipError(f"User id '{command.user_id}' does not exist.")
        if not target_user.is_active:
            raise ProjectOwnershipError("Inactive users cannot be assigned as project owners.")

        project = self._repository.get_project_for_user(command.project_id, actor)
        if project is None:
            raise AuthorizationError("Project is not visible to the current user.")
        updated_project = self._repository.add_project_owner(
            project_id=project.id,
            user_id=target_user.id,
        )
        if updated_project is None:
            raise AuthorizationError("Project is not visible to the current user.")

        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.owner.add",
            target_type="project",
            target_id=str(project.id),
            details=f"user_id:{target_user.id}",
        )
        return updated_project

    def remove_project_owner(self, command: UpdateProjectOwnerCommand) -> Project:
        """Remove a project owner as an authenticated admin."""
        actor = self._current_user_resolver.get_current_user(command.token)
        self._ensure_admin(actor)
        project = self._repository.get_project_for_user(command.project_id, actor)
        if project is None:
            raise AuthorizationError("Project is not visible to the current user.")
        if command.user_id not in project.owner_user_ids:
            raise ProjectOwnershipError(
                f"User id '{command.user_id}' is not an owner of project '{project.id}'."
            )
        if len(project.owner_user_ids) <= 1:
            raise ProjectOwnershipError("A project must keep at least one owner.")

        updated_project = self._repository.remove_project_owner(
            project_id=project.id,
            user_id=command.user_id,
        )
        if updated_project is None:
            raise AuthorizationError("Project is not visible to the current user.")

        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.owner.remove",
            target_type="project",
            target_id=str(project.id),
            details=f"user_id:{command.user_id}",
        )
        return updated_project

    @staticmethod
    def _ensure_admin(user: User) -> None:
        if user.role is not UserRole.ADMIN:
            raise AuthorizationError("Admin privileges are required for this action.")

    @staticmethod
    def _normalize_directory_path(raw_path: str) -> str:
        path = Path(raw_path).expanduser()
        return str(path.resolve())

    @staticmethod
    def _normalize_file_path(raw_path: str) -> str:
        path = Path(raw_path).expanduser()
        return str(path.resolve())

    @staticmethod
    def _validate_lifecycle_script(
        project_root_path: str,
        lifecycle_script_path: str,
        mappings: tuple[ProjectMappingInput, ...],
    ) -> None:
        project_root = Path(project_root_path)
        lifecycle_script = Path(lifecycle_script_path)
        if not project_root.exists() or not project_root.is_dir():
            raise ProjectValidationError("Project root path must point to an existing directory.")
        if not lifecycle_script.exists() or not lifecycle_script.is_file():
            raise ProjectValidationError("Lifecycle script path must point to an existing file.")
        if lifecycle_script.suffix.lower() != ".bat":
            raise ProjectValidationError("Lifecycle script path must reference a '.bat' file.")

        script_content = lifecycle_script.read_text(encoding="utf-8", errors="ignore")
        ProjectRegistryService._validate_command_dispatch_contract(
            script_content,
            ProjectRegistryService._resolve_action_identifiers(mappings),
        )

    @staticmethod
    def _resolve_action_identifiers(
        mappings: tuple[ProjectMappingInput, ...],
    ) -> dict[CanonicalLifecycleAction, str]:
        mapping_by_action = {
            mapping.canonical_action: mapping.script_label
            for mapping in mappings
        }
        return {
            action: mapping_by_action.get(action, action.value.upper())
            for action in CANONICAL_ACTIONS
        }

    @staticmethod
    def _validate_command_dispatch_contract(
        script_content: str,
        action_identifiers: dict[CanonicalLifecycleAction, str],
    ) -> None:
        normalized_content = script_content.upper()
        if not any(token in normalized_content for token in FIRST_ARGUMENT_TOKENS):
            raise ProjectValidationError(
                "Lifecycle script must dispatch lifecycle actions from the first command "
                "argument (%~1 or %1). OrchFlow currently executes scripts as "
                "'control.bat ACTION'."
            )

        missing_actions = [
            f"{action.value} -> {identifier}"
            for action, identifier in action_identifiers.items()
            if not ProjectRegistryService._has_dispatch_handler(script_content, identifier)
        ]
        if missing_actions:
            raise ProjectValidationError(
                "Lifecycle script does not expose command-dispatch handlers for: "
                f"{', '.join(missing_actions)}. Add first-argument dispatch lines such as "
                "'if /I \"%~1\"==\"STATUS\" goto STATUS' or provide action mappings matching "
                "the script identifiers."
            )

    @staticmethod
    def _has_dispatch_handler(script_content: str, identifier: str) -> bool:
        normalized_identifier = ProjectRegistryService._normalize_script_identifier(identifier)
        for raw_line in script_content.splitlines():
            line = raw_line.strip().upper()
            if normalized_identifier not in line:
                continue
            if any(token in line for token in FIRST_ARGUMENT_TOKENS):
                return True
            if "==" in line:
                return True
            if (
                f"GOTO {normalized_identifier}" in line
                or f"GOTO :{normalized_identifier}" in line
            ):
                return True
            if f"CALL :{normalized_identifier}" in line:
                return True
        return False

    @staticmethod
    def _normalize_script_identifier(identifier: str) -> str:
        return BATCH_LABEL_PREFIX_PATTERN.sub("", identifier.strip()).upper()

    @staticmethod
    def _normalize_mappings(
        mappings: tuple[ProjectMappingInput, ...],
    ) -> tuple[ProjectMappingInput, ...]:
        seen_actions: set[CanonicalLifecycleAction] = set()
        normalized: list[ProjectMappingInput] = []
        for mapping in mappings:
            script_label = ProjectRegistryService._normalize_script_identifier(
                mapping.script_label
            )
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
