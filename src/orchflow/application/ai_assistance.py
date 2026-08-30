"""Application boundary for review-driven AI assistance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Literal, Protocol

from orchflow.domain.access_control import User
from orchflow.domain.project_registry import Project

AIAssistanceGatewayStatus = Literal["disabled", "configured", "misconfigured"]
AIAssistanceHealthStatus = Literal["disabled", "healthy", "unhealthy", "unsupported"]
AIAssistanceManifestOperation = Literal["improve_lifecycle_script", "generate_lifecycle_script"]

DEFAULT_EXCLUDE_DIR_NAMES = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "coverage",
        "data",
        "dist",
        "node_modules",
        "runtime",
        "venv",
    }
)
DEFAULT_SECRET_PATH_PATTERNS = (
    ".env",
    ".env.*",
    "*.key",
    "*.pem",
    "*.pfx",
    "*.p12",
    "*secret*",
    "*token*",
)
DEFAULT_BINARY_EXTENSIONS = frozenset(
    {
        ".7z",
        ".bin",
        ".db",
        ".dll",
        ".exe",
        ".gif",
        ".ico",
        ".jpg",
        ".jpeg",
        ".pdf",
        ".png",
        ".pyc",
        ".sqlite",
        ".zip",
    }
)
DEFAULT_MAX_FILE_SIZE_BYTES = 64 * 1024
DEFAULT_MAX_TOTAL_BYTES = 256 * 1024
SUPPORTED_MANIFEST_OPERATIONS: tuple[AIAssistanceManifestOperation, ...] = (
    "improve_lifecycle_script",
    "generate_lifecycle_script",
)


class AIAssistanceError(Exception):
    """Base exception for AI assistance application failures."""


@dataclass(frozen=True, slots=True)
class GetAIAssistanceStatusCommand:
    """Input required to read the AI assistance gateway status."""

    token: str


@dataclass(frozen=True, slots=True)
class CheckAIAssistanceGatewayHealthCommand:
    """Input required to check the configured AI gateway health."""

    token: str


@dataclass(frozen=True, slots=True)
class ListAIAssistanceModelsCommand:
    """Input required to list configured AI gateway models."""

    token: str


@dataclass(frozen=True, slots=True)
class CreateAuthorizedContextManifestCommand:
    """Input required to create an authorized AI context manifest."""

    token: str
    project_id: int
    selected_model: str
    intended_operation: AIAssistanceManifestOperation
    include_patterns: tuple[str, ...] = ("*",)
    exclude_patterns: tuple[str, ...] = ()
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES


@dataclass(frozen=True, slots=True)
class GetAuthorizedContextManifestCommand:
    """Input required to read an authorized AI context manifest."""

    token: str
    manifest_id: int


@dataclass(frozen=True, slots=True)
class AIAssistanceStatus:
    """Safe AI assistance status returned to external surfaces."""

    provider: str
    status: AIAssistanceGatewayStatus
    enabled: bool
    mode: str
    base_url: str
    default_model: str
    timeout_seconds: int
    api_key_configured: bool
    sdk_available: bool
    ready_for_requests: bool
    message: str


@dataclass(frozen=True, slots=True)
class AIAssistanceGatewayHealth:
    """Safe AI gateway health returned to external surfaces."""

    provider: str
    status: AIAssistanceHealthStatus
    enabled: bool
    mode: str
    base_url: str
    checked: bool
    status_code: int | None
    response_time_ms: int | None
    message: str


@dataclass(frozen=True, slots=True)
class AIAssistanceModel:
    """Model or agent descriptor discovered through the AI gateway."""

    id: str
    owned_by: str | None = None


@dataclass(frozen=True, slots=True)
class AIAssistanceModelCatalog:
    """Safe model catalog returned to external surfaces."""

    provider: str
    enabled: bool
    mode: str
    base_url: str
    default_model: str
    models: tuple[AIAssistanceModel, ...]
    supports_discovery: bool
    message: str


@dataclass(frozen=True, slots=True)
class AuthorizedContextManifest:
    """Persisted, reviewable metadata for an authorized AI context selection."""

    id: int
    project_id: int
    requested_by_user_id: int
    selected_model: str
    intended_operation: AIAssistanceManifestOperation
    project_root_path: str
    include_patterns: tuple[str, ...]
    exclude_patterns: tuple[str, ...]
    included_paths: tuple[str, ...]
    excluded_paths: tuple[str, ...]
    ignored_paths: tuple[str, ...]
    secret_filter_rules: tuple[str, ...]
    max_file_size_bytes: int
    max_total_bytes: int
    total_included_bytes: int
    created_at: datetime


class AIAssistanceGateway(Protocol):
    """Infrastructure boundary for the configured AI/model gateway."""

    def get_status(self) -> AIAssistanceStatus: ...

    def check_health(self) -> AIAssistanceGatewayHealth: ...

    def list_models(self) -> AIAssistanceModelCatalog: ...


class AIAssistanceAuditRecorder(Protocol):
    """Persistence boundary for AI assistance audit events."""

    def record_audit_event(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None: ...


class AIAssistanceManifestRepository(Protocol):
    """Persistence boundary for authorized context manifests."""

    def create_authorized_context_manifest(
        self,
        *,
        project_id: int,
        requested_by_user_id: int,
        selected_model: str,
        intended_operation: AIAssistanceManifestOperation,
        project_root_path: str,
        include_patterns: tuple[str, ...],
        exclude_patterns: tuple[str, ...],
        included_paths: tuple[str, ...],
        excluded_paths: tuple[str, ...],
        ignored_paths: tuple[str, ...],
        secret_filter_rules: tuple[str, ...],
        max_file_size_bytes: int,
        max_total_bytes: int,
        total_included_bytes: int,
    ) -> AuthorizedContextManifest: ...

    def get_authorized_context_manifest(
        self,
        manifest_id: int,
    ) -> AuthorizedContextManifest | None: ...


class CurrentUserResolver(Protocol):
    """Boundary used to resolve the current authenticated user."""

    def get_current_user(self, token: str) -> User: ...


class ProjectResolver(Protocol):
    """Boundary used to resolve project visibility for AI context authorization."""

    def get_project(self, token: str, project_id: int) -> Project: ...


class AIAssistanceService:
    """Coordinates safe AI assistance operations owned by OrchFlow."""

    def __init__(
        self,
        gateway: AIAssistanceGateway,
        current_user_resolver: CurrentUserResolver,
        audit_recorder: AIAssistanceAuditRecorder,
        project_resolver: ProjectResolver,
        manifest_repository: AIAssistanceManifestRepository,
    ) -> None:
        self._gateway = gateway
        self._current_user_resolver = current_user_resolver
        self._audit_recorder = audit_recorder
        self._project_resolver = project_resolver
        self._manifest_repository = manifest_repository

    def get_status(self, command: GetAIAssistanceStatusCommand) -> AIAssistanceStatus:
        """Return the configured AI gateway status for an authenticated user."""
        actor = self._current_user_resolver.get_current_user(command.token)
        gateway_status = self._gateway.get_status()
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.status.read",
            target_type="ai_assistance_gateway",
            target_id=gateway_status.provider,
            details=(
                f"status:{gateway_status.status};"
                f"enabled:{str(gateway_status.enabled).lower()};"
                f"mode:{gateway_status.mode};"
                f"default_model:{gateway_status.default_model}"
            ),
        )
        return gateway_status

    def check_gateway_health(
        self,
        command: CheckAIAssistanceGatewayHealthCommand,
    ) -> AIAssistanceGatewayHealth:
        """Check the configured AI gateway without sending project context."""
        actor = self._current_user_resolver.get_current_user(command.token)
        health = self._gateway.check_health()
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.gateway.health",
            target_type="ai_assistance_gateway",
            target_id=health.provider,
            details=(
                f"status:{health.status};"
                f"enabled:{str(health.enabled).lower()};"
                f"mode:{health.mode};"
                f"checked:{str(health.checked).lower()};"
                f"status_code:{health.status_code}"
            ),
        )
        return health

    def list_models(
        self,
        command: ListAIAssistanceModelsCommand,
    ) -> AIAssistanceModelCatalog:
        """List configured AI gateway models without sending project context."""
        actor = self._current_user_resolver.get_current_user(command.token)
        catalog = self._gateway.list_models()
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.models.list",
            target_type="ai_assistance_gateway",
            target_id=catalog.provider,
            details=(
                f"enabled:{str(catalog.enabled).lower()};"
                f"mode:{catalog.mode};"
                f"supports_discovery:{str(catalog.supports_discovery).lower()};"
                f"model_count:{len(catalog.models)}"
            ),
        )
        return catalog

    def create_authorized_context_manifest(
        self,
        command: CreateAuthorizedContextManifestCommand,
    ) -> AuthorizedContextManifest:
        """Create an authorized project context manifest without reading file contents."""
        actor = self._current_user_resolver.get_current_user(command.token)
        project = self._project_resolver.get_project(command.token, command.project_id)
        include_patterns = self._validate_patterns(command.include_patterns, "include")
        exclude_patterns = self._validate_patterns(command.exclude_patterns, "exclude")
        intended_operation = self._validate_intended_operation(command.intended_operation)
        selected_model = self._validate_selected_model(command.selected_model)
        max_file_size_bytes = self._validate_positive_limit(
            command.max_file_size_bytes,
            "max_file_size_bytes",
        )
        max_total_bytes = self._validate_positive_limit(
            command.max_total_bytes,
            "max_total_bytes",
        )
        (
            included_paths,
            excluded_paths,
            ignored_paths,
            total_included_bytes,
        ) = self._build_manifest_paths(
            project_root_path=Path(project.project_root_path),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_file_size_bytes=max_file_size_bytes,
            max_total_bytes=max_total_bytes,
        )
        manifest = self._manifest_repository.create_authorized_context_manifest(
            project_id=project.id,
            requested_by_user_id=actor.id,
            selected_model=selected_model,
            intended_operation=intended_operation,
            project_root_path=project.project_root_path,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            included_paths=included_paths,
            excluded_paths=excluded_paths,
            ignored_paths=ignored_paths,
            secret_filter_rules=DEFAULT_SECRET_PATH_PATTERNS,
            max_file_size_bytes=max_file_size_bytes,
            max_total_bytes=max_total_bytes,
            total_included_bytes=total_included_bytes,
        )
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.context_manifest.create",
            target_type="ai_context_manifest",
            target_id=str(manifest.id),
            details=(
                f"project_id:{manifest.project_id};"
                f"model:{manifest.selected_model};"
                f"operation:{manifest.intended_operation};"
                f"included:{len(manifest.included_paths)};"
                f"excluded:{len(manifest.excluded_paths)};"
                f"ignored:{len(manifest.ignored_paths)};"
                f"total_bytes:{manifest.total_included_bytes}"
            ),
        )
        return manifest

    def get_authorized_context_manifest(
        self,
        command: GetAuthorizedContextManifestCommand,
    ) -> AuthorizedContextManifest:
        """Return a persisted authorized context manifest visible to the requester."""
        actor = self._current_user_resolver.get_current_user(command.token)
        manifest = self._manifest_repository.get_authorized_context_manifest(
            command.manifest_id
        )
        if manifest is None:
            raise AIAssistanceError("Authorized context manifest was not found.")
        self._project_resolver.get_project(command.token, manifest.project_id)
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.context_manifest.read",
            target_type="ai_context_manifest",
            target_id=str(manifest.id),
            details=f"project_id:{manifest.project_id};model:{manifest.selected_model}",
        )
        return manifest

    @staticmethod
    def _validate_patterns(patterns: tuple[str, ...], label: str) -> tuple[str, ...]:
        normalized = tuple(pattern.strip().replace("\\", "/") for pattern in patterns)
        normalized = tuple(pattern for pattern in normalized if pattern)
        if label == "include" and not normalized:
            raise AIAssistanceError("At least one include pattern is required.")
        for pattern in normalized:
            if ".." in Path(pattern).parts:
                raise AIAssistanceError(f"{label} patterns must not traverse directories.")
        return normalized

    @staticmethod
    def _validate_selected_model(selected_model: str) -> str:
        normalized = selected_model.strip()
        if not normalized:
            raise AIAssistanceError("Selected model is required.")
        return normalized

    @staticmethod
    def _validate_intended_operation(
        intended_operation: str,
    ) -> AIAssistanceManifestOperation:
        if intended_operation not in SUPPORTED_MANIFEST_OPERATIONS:
            raise AIAssistanceError("Unsupported AI context manifest operation.")
        return intended_operation

    @staticmethod
    def _validate_positive_limit(value: int, label: str) -> int:
        if value < 1:
            raise AIAssistanceError(f"{label} must be greater than zero.")
        return value

    def _build_manifest_paths(
        self,
        *,
        project_root_path: Path,
        include_patterns: tuple[str, ...],
        exclude_patterns: tuple[str, ...],
        max_file_size_bytes: int,
        max_total_bytes: int,
    ) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], int]:
        if not project_root_path.exists() or not project_root_path.is_dir():
            raise AIAssistanceError("Project root path must be an existing directory.")

        included_paths: list[str] = []
        excluded_paths: list[str] = []
        ignored_paths: list[str] = []
        total_included_bytes = 0

        for candidate in sorted(project_root_path.rglob("*")):
            relative_path = candidate.relative_to(project_root_path).as_posix()
            if candidate.is_dir():
                continue
            if self._is_generated_or_secret(relative_path, candidate):
                ignored_paths.append(relative_path)
                continue
            if not self._matches_any(relative_path, include_patterns):
                excluded_paths.append(relative_path)
                continue
            if self._matches_any(relative_path, exclude_patterns):
                excluded_paths.append(relative_path)
                continue

            file_size = candidate.stat().st_size
            if file_size > max_file_size_bytes:
                ignored_paths.append(relative_path)
                continue
            if total_included_bytes + file_size > max_total_bytes:
                ignored_paths.append(relative_path)
                continue
            included_paths.append(relative_path)
            total_included_bytes += file_size

        return (
            tuple(included_paths),
            tuple(excluded_paths),
            tuple(ignored_paths),
            total_included_bytes,
        )

    def _is_generated_or_secret(self, relative_path: str, candidate: Path) -> bool:
        path_parts = set(Path(relative_path).parts)
        if path_parts.intersection(DEFAULT_EXCLUDE_DIR_NAMES):
            return True
        if candidate.suffix.lower() in DEFAULT_BINARY_EXTENSIONS:
            return True
        return self._matches_any(relative_path, DEFAULT_SECRET_PATH_PATTERNS)

    @staticmethod
    def _matches_any(relative_path: str, patterns: tuple[str, ...]) -> bool:
        return any(
            fnmatch(relative_path, pattern) or fnmatch(Path(relative_path).name, pattern)
            for pattern in patterns
        )
