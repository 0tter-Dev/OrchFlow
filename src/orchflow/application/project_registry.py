"""Application service for project registration and normalized project definitions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from orchflow.application.access_control import AuthorizationError
from orchflow.domain.access_control import User, UserRole
from orchflow.domain.lifecycle_function_model import (
    IDEAL_LIFECYCLE_FUNCTIONS,
    LifecycleFunctionConfiguration,
    ProjectConfigurationHealth,
    build_lifecycle_function_configurations,
    derive_project_configuration_health,
)
from orchflow.domain.project_registry import (
    CanonicalLifecycleAction,
    LifecycleActionMapping,
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
class UpdateLifecycleFunctionConfigurationCommand:
    """Input required to replace lifecycle function configuration for a project."""

    token: str
    project_id: int
    mappings: tuple[ProjectMappingInput, ...] = ()
    unconfigured_actions: tuple[CanonicalLifecycleAction, ...] = ()


@dataclass(frozen=True, slots=True)
class ReloadProjectCommand:
    """Input required to reload lifecycle function detection for one project."""

    token: str
    project_id: int


@dataclass(frozen=True, slots=True)
class ReloadProjectsCommand:
    """Input required to reload lifecycle function detection for many projects."""

    token: str
    project_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ProjectReloadResult:
    """Result of refreshing a project's lifecycle function configuration."""

    project: Project
    previous_health: ProjectConfigurationHealth
    current_health: ProjectConfigurationHealth
    changed_actions: tuple[CanonicalLifecycleAction, ...]


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

    def replace_lifecycle_function_configuration(
        self,
        *,
        project_id: int,
        mappings: tuple[ProjectMappingInput, ...],
        unconfigured_actions: tuple[CanonicalLifecycleAction, ...],
        decided_by_user_id: int,
    ) -> Project | None: ...

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
        script_content = self._validate_lifecycle_script_paths(
            project_root_path,
            lifecycle_script_path,
        )
        mappings = self._resolve_configured_mappings(script_content, mappings)

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

    def update_lifecycle_function_configuration(
        self,
        command: UpdateLifecycleFunctionConfigurationCommand,
    ) -> Project:
        """Replace manual lifecycle function configuration for a visible project."""
        actor = self._current_user_resolver.get_current_user(command.token)
        project = self._repository.get_project_for_user(command.project_id, actor)
        if project is None:
            raise AuthorizationError("Project is not visible to the current user.")

        mappings = self._normalize_mappings(command.mappings)
        unconfigured_actions = self._normalize_unconfigured_actions(
            command.unconfigured_actions,
            mappings,
        )
        script_content = self._validate_lifecycle_script_paths(
            project.project_root_path,
            project.lifecycle_script_path,
        )
        configured_mappings = self._resolve_manual_mappings(script_content, mappings)
        if not configured_mappings:
            raise ProjectValidationError(
                "At least one lifecycle function must remain configured before a project "
                "can be operated by OrchFlow."
            )

        updated_project = self._repository.replace_lifecycle_function_configuration(
            project_id=project.id,
            mappings=configured_mappings,
            unconfigured_actions=unconfigured_actions,
            decided_by_user_id=actor.id,
        )
        if updated_project is None:
            raise AuthorizationError("Project is not visible to the current user.")

        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.lifecycle_configuration.update",
            target_type="project",
            target_id=str(project.id),
            details=(
                f"configured:{len(configured_mappings)};"
                f"unconfigured:{len(unconfigured_actions)}"
            ),
        )
        return updated_project

    def reload_project(self, command: ReloadProjectCommand) -> ProjectReloadResult:
        """Reload lifecycle script detection for one visible project."""
        actor = self._current_user_resolver.get_current_user(command.token)
        project = self._repository.get_project_for_user(command.project_id, actor)
        if project is None:
            raise AuthorizationError("Project is not visible to the current user.")
        return self._reload_visible_project(project, actor)

    def reload_projects(self, command: ReloadProjectsCommand) -> tuple[ProjectReloadResult, ...]:
        """Reload lifecycle script detection for many visible projects in sequence."""
        actor = self._current_user_resolver.get_current_user(command.token)
        if not command.project_ids:
            raise ProjectValidationError("At least one project id must be provided for reload.")

        seen_project_ids: set[int] = set()
        results: list[ProjectReloadResult] = []
        for project_id in command.project_ids:
            if project_id in seen_project_ids:
                raise ProjectValidationError(
                    f"Duplicate project id '{project_id}' provided for reload."
                )
            seen_project_ids.add(project_id)
            project = self._repository.get_project_for_user(project_id, actor)
            if project is None:
                raise AuthorizationError("Project is not visible to the current user.")
            results.append(self._reload_visible_project(project, actor))
        return tuple(results)

    @staticmethod
    def _ensure_admin(user: User) -> None:
        if user.role is not UserRole.ADMIN:
            raise AuthorizationError("Admin privileges are required for this action.")

    def _reload_visible_project(self, project: Project, actor: User) -> ProjectReloadResult:
        previous_unconfigured_actions = unconfigured_actions_for_project(project)
        previous_configurations = self._lifecycle_configurations(
            project.action_mappings,
            previous_unconfigured_actions,
        )
        previous_health = derive_project_configuration_health(previous_configurations)

        script_content = self._validate_lifecycle_script_paths(
            project.project_root_path,
            project.lifecycle_script_path,
        )
        reloaded_mappings = self._resolve_reloaded_mappings(
            script_content,
            project.action_mappings,
            previous_unconfigured_actions,
        )

        updated_project = self._repository.replace_lifecycle_function_configuration(
            project_id=project.id,
            mappings=reloaded_mappings,
            unconfigured_actions=previous_unconfigured_actions,
            decided_by_user_id=actor.id,
        )
        if updated_project is None:
            raise AuthorizationError("Project is not visible to the current user.")

        current_unconfigured_actions = unconfigured_actions_for_project(updated_project)
        current_configurations = self._lifecycle_configurations(
            updated_project.action_mappings,
            current_unconfigured_actions,
        )
        current_health = derive_project_configuration_health(current_configurations)
        changed_actions = self._changed_configuration_actions(
            previous_configurations,
            current_configurations,
        )

        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="project.lifecycle_configuration.reload",
            target_type="project",
            target_id=str(project.id),
            details=(
                f"previous_health:{previous_health.value};"
                f"current_health:{current_health.value};"
                f"changed_actions:{','.join(action.value for action in changed_actions) or 'none'};"
                f"configured:{len(updated_project.action_mappings)}"
            ),
        )
        return ProjectReloadResult(
            project=updated_project,
            previous_health=previous_health,
            current_health=current_health,
            changed_actions=changed_actions,
        )

    @staticmethod
    def _normalize_directory_path(raw_path: str) -> str:
        path = Path(raw_path).expanduser()
        return str(path.resolve())

    @staticmethod
    def _normalize_file_path(raw_path: str) -> str:
        path = Path(raw_path).expanduser()
        return str(path.resolve())

    @staticmethod
    def _validate_lifecycle_script_paths(
        project_root_path: str,
        lifecycle_script_path: str,
    ) -> str:
        project_root = Path(project_root_path)
        lifecycle_script = Path(lifecycle_script_path)
        if not project_root.exists() or not project_root.is_dir():
            raise ProjectValidationError("Project root path must point to an existing directory.")
        if not lifecycle_script.exists() or not lifecycle_script.is_file():
            raise ProjectValidationError("Lifecycle script path must point to an existing file.")
        if lifecycle_script.suffix.lower() != ".bat":
            raise ProjectValidationError("Lifecycle script path must reference a '.bat' file.")

        script_content = lifecycle_script.read_text(encoding="utf-8", errors="ignore")
        if not ProjectRegistryService._has_first_argument_dispatch(script_content):
            raise ProjectValidationError(
                "Lifecycle script must dispatch lifecycle actions from the first command "
                "argument (%~1 or %1). OrchFlow currently executes scripts as "
                "'control.bat ACTION'."
            )
        return script_content

    @staticmethod
    def _resolve_configured_mappings(
        script_content: str,
        mappings: tuple[ProjectMappingInput, ...],
    ) -> tuple[ProjectMappingInput, ...]:
        mapping_by_action = {
            mapping.canonical_action: mapping.script_label
            for mapping in mappings
        }
        missing_mapped_actions = [
            f"{action.value} -> {identifier}"
            for action, identifier in mapping_by_action.items()
            if not ProjectRegistryService._has_dispatch_handler(script_content, identifier)
        ]
        if missing_mapped_actions:
            raise ProjectValidationError(
                "Lifecycle script does not expose command-dispatch handlers for: "
                f"{', '.join(missing_mapped_actions)}. Add first-argument dispatch lines such as "
                "'if /I \"%~1\"==\"STATUS\" goto STATUS' or provide action mappings matching "
                "the script identifiers."
            )

        configured_mappings: list[ProjectMappingInput] = []
        for function in IDEAL_LIFECYCLE_FUNCTIONS:
            mapped_identifier = mapping_by_action.get(function.action)
            if mapped_identifier is not None:
                configured_mappings.append(
                    ProjectMappingInput(
                        canonical_action=function.action,
                        script_label=mapped_identifier,
                        source=ProjectRegistryService._mapping_source_for_action(
                            function.action,
                            mappings,
                        ),
                    )
                )
                continue
            if ProjectRegistryService._has_dispatch_handler(
                script_content,
                function.preferred_script_identifier,
            ):
                configured_mappings.append(
                    ProjectMappingInput(
                        canonical_action=function.action,
                        script_label=function.preferred_script_identifier,
                        source=MappingSource.IMPORTED,
                    )
                )

        if not configured_mappings:
            raise ProjectValidationError(
                "Lifecycle script must expose at least one configured lifecycle function "
                "matching the ideal model or an explicit action mapping."
            )
        return tuple(configured_mappings)

    @staticmethod
    def _resolve_manual_mappings(
        script_content: str,
        mappings: tuple[ProjectMappingInput, ...],
    ) -> tuple[ProjectMappingInput, ...]:
        missing_mapped_actions = [
            f"{mapping.canonical_action.value} -> {mapping.script_label}"
            for mapping in mappings
            if not ProjectRegistryService._has_dispatch_handler(
                script_content,
                mapping.script_label,
            )
        ]
        if missing_mapped_actions:
            raise ProjectValidationError(
                "Lifecycle script does not expose command-dispatch handlers for: "
                f"{', '.join(missing_mapped_actions)}. Add first-argument dispatch lines such as "
                "'if /I \"%~1\"==\"STATUS\" goto STATUS' or provide action mappings matching "
                "the script identifiers."
            )
        return tuple(
            ProjectMappingInput(
                canonical_action=mapping.canonical_action,
                script_label=mapping.script_label,
                source=mapping.source,
            )
            for mapping in mappings
        )

    @staticmethod
    def _resolve_reloaded_mappings(
        script_content: str,
        current_mappings: tuple[LifecycleActionMapping, ...],
        unconfigured_actions: tuple[CanonicalLifecycleAction, ...],
    ) -> tuple[ProjectMappingInput, ...]:
        current_mapping_by_action = {
            mapping.canonical_action: mapping
            for mapping in current_mappings
        }
        explicitly_unconfigured_actions = set(unconfigured_actions)
        reloaded_mappings: list[ProjectMappingInput] = []

        for function in IDEAL_LIFECYCLE_FUNCTIONS:
            if function.action in explicitly_unconfigured_actions:
                continue

            current_mapping = current_mapping_by_action.get(function.action)
            if (
                current_mapping is not None
                and current_mapping.source is not MappingSource.IMPORTED
                and ProjectRegistryService._has_dispatch_handler(
                    script_content,
                    current_mapping.script_label,
                )
            ):
                reloaded_mappings.append(
                    ProjectMappingInput(
                        canonical_action=function.action,
                        script_label=current_mapping.script_label,
                        source=current_mapping.source,
                    )
                )
                continue

            if ProjectRegistryService._has_dispatch_handler(
                script_content,
                function.preferred_script_identifier,
            ):
                reloaded_mappings.append(
                    ProjectMappingInput(
                        canonical_action=function.action,
                        script_label=function.preferred_script_identifier,
                        source=MappingSource.IMPORTED,
                    )
                )

        return tuple(reloaded_mappings)

    @staticmethod
    def _lifecycle_configurations(
        mappings: tuple[LifecycleActionMapping, ...],
        unconfigured_actions: tuple[CanonicalLifecycleAction, ...],
    ) -> tuple[LifecycleFunctionConfiguration, ...]:
        return build_lifecycle_function_configurations(
            {
                mapping.canonical_action: mapping.script_label
                for mapping in mappings
            },
            unconfigured_actions,
        )

    @staticmethod
    def _changed_configuration_actions(
        previous_configurations: tuple[LifecycleFunctionConfiguration, ...],
        current_configurations: tuple[LifecycleFunctionConfiguration, ...],
    ) -> tuple[CanonicalLifecycleAction, ...]:
        current_by_action = {
            configuration.action: configuration
            for configuration in current_configurations
        }
        changed_actions: list[CanonicalLifecycleAction] = []
        for previous_configuration in previous_configurations:
            current_configuration = current_by_action[previous_configuration.action]
            if (
                previous_configuration.state != current_configuration.state
                or previous_configuration.script_label != current_configuration.script_label
            ):
                changed_actions.append(previous_configuration.action)
        return tuple(changed_actions)

    @staticmethod
    def _has_first_argument_dispatch(script_content: str) -> bool:
        normalized_content = script_content.upper()
        return any(token in normalized_content for token in FIRST_ARGUMENT_TOKENS)

    @staticmethod
    def _has_dispatch_handler(script_content: str, identifier: str) -> bool:
        normalized_identifier = ProjectRegistryService._normalize_script_identifier(identifier)
        for raw_line in script_content.splitlines():
            line = raw_line.strip().upper()
            if ProjectRegistryService._line_dispatches_identifier(
                line,
                normalized_identifier,
            ):
                return True
        return False

    @staticmethod
    def _normalize_script_identifier(identifier: str) -> str:
        return BATCH_LABEL_PREFIX_PATTERN.sub("", identifier.strip()).upper()

    @staticmethod
    def _line_dispatches_identifier(line: str, normalized_identifier: str) -> bool:
        if not any(token in line for token in FIRST_ARGUMENT_TOKENS):
            return False
        identifier_pattern = re.escape(normalized_identifier)
        return any(
            re.search(
                rf'"?{re.escape(token)}"?\s*==\s*"?:?{identifier_pattern}"?(?:\s|&|$)',
                line,
            )
            is not None
            for token in FIRST_ARGUMENT_TOKENS
        )

    @staticmethod
    def _mapping_source_for_action(
        action: CanonicalLifecycleAction,
        mappings: tuple[ProjectMappingInput, ...],
    ) -> MappingSource:
        for mapping in mappings:
            if mapping.canonical_action == action:
                return mapping.source
        return MappingSource.IMPORTED

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

    @staticmethod
    def _normalize_unconfigured_actions(
        unconfigured_actions: tuple[CanonicalLifecycleAction, ...],
        mappings: tuple[ProjectMappingInput, ...],
    ) -> tuple[CanonicalLifecycleAction, ...]:
        mapped_actions = {mapping.canonical_action for mapping in mappings}
        seen_actions: set[CanonicalLifecycleAction] = set()
        normalized: list[CanonicalLifecycleAction] = []
        for action in unconfigured_actions:
            if action in seen_actions:
                raise ProjectValidationError(
                    f"Duplicate unconfigured decision for canonical action '{action.value}'."
                )
            if action in mapped_actions:
                raise ProjectValidationError(
                    f"Canonical action '{action.value}' cannot be both mapped and unconfigured."
                )
            seen_actions.add(action)
            normalized.append(action)
        return tuple(normalized)


def unconfigured_actions_for_project(project: Project) -> tuple[CanonicalLifecycleAction, ...]:
    """Return explicit unconfigured decisions for a project."""
    return tuple(
        decision.canonical_action
        for decision in project.lifecycle_function_decisions
        if decision.state == "unconfigured"
    )
