"""Application boundary for review-driven AI assistance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from fnmatch import fnmatch
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Literal, Protocol, cast

from orchflow.domain.access_control import User
from orchflow.domain.lifecycle_function_model import build_lifecycle_function_configurations
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
class CreateAnalysisProposalCommand:
    """Input required to create a reviewable AI analysis proposal."""

    token: str
    manifest_id: int
    user_instructions: str | None = None


@dataclass(frozen=True, slots=True)
class GetAnalysisProposalCommand:
    """Input required to read a reviewable AI analysis proposal."""

    token: str
    proposal_id: int


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


@dataclass(frozen=True, slots=True)
class AuthorizedContextFile:
    """File content approved by an authorized context manifest."""

    relative_path: str
    content: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class AIAssistancePromptMessage:
    """Message sent to the configured AI gateway."""

    role: Literal["system", "user"]
    content: str


@dataclass(frozen=True, slots=True)
class ProposedLifecycleActionMapping:
    """AI-proposed canonical action mapping candidate."""

    canonical_action: Literal["status", "start", "stop", "restart"]
    script_label: str
    rationale: str | None = None


@dataclass(frozen=True, slots=True)
class AnalysisProposalContent:
    """Structured, reviewable AI proposal content."""

    lifecycle_strategy: str
    runtime_hints: tuple[str, ...]
    candidate_script_content: str
    action_mappings: tuple[ProposedLifecycleActionMapping, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AIAnalysisProposal:
    """Persisted AI analysis proposal awaiting human review."""

    id: int
    manifest_id: int
    project_id: int
    requested_by_user_id: int
    selected_model: str
    intended_operation: AIAssistanceManifestOperation
    lifecycle_strategy: str
    runtime_hints: tuple[str, ...]
    candidate_script_content: str
    action_mappings: tuple[ProposedLifecycleActionMapping, ...]
    warnings: tuple[str, ...]
    created_at: datetime


class AIAssistanceGateway(Protocol):
    """Infrastructure boundary for the configured AI/model gateway."""

    def get_status(self) -> AIAssistanceStatus: ...

    def check_health(self) -> AIAssistanceGatewayHealth: ...

    def list_models(self) -> AIAssistanceModelCatalog: ...

    def generate_completion(
        self,
        *,
        model: str,
        messages: tuple[AIAssistancePromptMessage, ...],
    ) -> str: ...


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
    """Persistence boundary for AI context manifests and proposals."""

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

    def create_analysis_proposal(
        self,
        *,
        manifest_id: int,
        project_id: int,
        requested_by_user_id: int,
        selected_model: str,
        intended_operation: AIAssistanceManifestOperation,
        lifecycle_strategy: str,
        runtime_hints: tuple[str, ...],
        candidate_script_content: str,
        action_mappings: tuple[ProposedLifecycleActionMapping, ...],
        warnings: tuple[str, ...],
    ) -> AIAnalysisProposal: ...

    def get_analysis_proposal(
        self,
        proposal_id: int,
    ) -> AIAnalysisProposal | None: ...


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

    def create_analysis_proposal(
        self,
        command: CreateAnalysisProposalCommand,
    ) -> AIAnalysisProposal:
        """Create a reviewable AI analysis proposal without writing files."""
        actor = self._current_user_resolver.get_current_user(command.token)
        manifest = self._manifest_repository.get_authorized_context_manifest(
            command.manifest_id
        )
        if manifest is None:
            raise AIAssistanceError("Authorized context manifest was not found.")
        if manifest.requested_by_user_id != actor.id:
            raise AIAssistanceError(
                "Authorized context manifest belongs to another user."
            )
        project = self._project_resolver.get_project(command.token, manifest.project_id)
        gateway_status = self._gateway.get_status()
        if not gateway_status.ready_for_requests:
            raise AIAssistanceError(
                "AI assistance gateway is not ready for analysis proposals."
            )

        approved_files = self._read_approved_context_files(manifest)
        messages = self._build_analysis_proposal_messages(
            project=project,
            manifest=manifest,
            approved_files=approved_files,
            user_instructions=command.user_instructions,
        )
        completion = self._gateway.generate_completion(
            model=manifest.selected_model,
            messages=messages,
        )
        content = self._parse_analysis_proposal_content(completion)
        proposal = self._manifest_repository.create_analysis_proposal(
            manifest_id=manifest.id,
            project_id=manifest.project_id,
            requested_by_user_id=actor.id,
            selected_model=manifest.selected_model,
            intended_operation=manifest.intended_operation,
            lifecycle_strategy=content.lifecycle_strategy,
            runtime_hints=content.runtime_hints,
            candidate_script_content=content.candidate_script_content,
            action_mappings=content.action_mappings,
            warnings=content.warnings,
        )
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.analysis_proposal.create",
            target_type="ai_analysis_proposal",
            target_id=str(proposal.id),
            details=(
                f"manifest_id:{proposal.manifest_id};"
                f"project_id:{proposal.project_id};"
                f"model:{proposal.selected_model};"
                f"operation:{proposal.intended_operation};"
                f"approved_files:{len(approved_files)};"
                f"proposed_mappings:{len(proposal.action_mappings)}"
            ),
        )
        return proposal

    def get_analysis_proposal(
        self,
        command: GetAnalysisProposalCommand,
    ) -> AIAnalysisProposal:
        """Return a persisted AI analysis proposal visible to the requester."""
        actor = self._current_user_resolver.get_current_user(command.token)
        proposal = self._manifest_repository.get_analysis_proposal(command.proposal_id)
        if proposal is None:
            raise AIAssistanceError("AI analysis proposal was not found.")
        self._project_resolver.get_project(command.token, proposal.project_id)
        self._audit_recorder.record_audit_event(
            actor_user_id=actor.id,
            action="ai_assistance.analysis_proposal.read",
            target_type="ai_analysis_proposal",
            target_id=str(proposal.id),
            details=f"manifest_id:{proposal.manifest_id};project_id:{proposal.project_id}",
        )
        return proposal

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

    def _read_approved_context_files(
        self,
        manifest: AuthorizedContextManifest,
    ) -> tuple[AuthorizedContextFile, ...]:
        root_path = Path(manifest.project_root_path).resolve()
        files: list[AuthorizedContextFile] = []
        total_size = 0
        for relative_path in manifest.included_paths:
            candidate = (root_path / relative_path).resolve()
            try:
                candidate.relative_to(root_path)
            except ValueError as error:
                raise AIAssistanceError(
                    "Authorized context manifest contains an invalid path."
                ) from error
            if not candidate.exists() or not candidate.is_file():
                raise AIAssistanceError(
                    f"Authorized context file is no longer available: {relative_path}"
                )
            file_size = candidate.stat().st_size
            if file_size > manifest.max_file_size_bytes:
                raise AIAssistanceError(
                    f"Authorized context file exceeds size limit: {relative_path}"
                )
            if total_size + file_size > manifest.max_total_bytes:
                raise AIAssistanceError(
                    "Authorized context files exceed the manifest total size limit."
                )
            files.append(
                AuthorizedContextFile(
                    relative_path=relative_path,
                    content=candidate.read_text(encoding="utf-8", errors="replace"),
                    size_bytes=file_size,
                )
            )
            total_size += file_size
        return tuple(files)

    def _build_analysis_proposal_messages(
        self,
        *,
        project: Project,
        manifest: AuthorizedContextManifest,
        approved_files: tuple[AuthorizedContextFile, ...],
        user_instructions: str | None,
    ) -> tuple[AIAssistancePromptMessage, ...]:
        lifecycle_configurations = build_lifecycle_function_configurations(
            {
                mapping.canonical_action: mapping.script_label
                for mapping in project.action_mappings
            },
            (
                decision.canonical_action
                for decision in project.lifecycle_function_decisions
                if decision.state == "unconfigured"
            ),
        )
        ideal_functions = [
            {
                "canonical_action": configuration.action.value,
                "description": configuration.description,
                "preferred_script_identifier": configuration.preferred_script_identifier,
                "current_state": configuration.state.value,
                "current_script_label": configuration.script_label,
            }
            for configuration in lifecycle_configurations
        ]
        file_payload = [
            {
                "relative_path": approved_file.relative_path,
                "size_bytes": approved_file.size_bytes,
                "content": approved_file.content,
            }
            for approved_file in approved_files
        ]
        user_payload = {
            "project": {
                "id": project.id,
                "reference_name": project.reference_name,
                "description": project.description,
                "project_root_path": project.project_root_path,
                "lifecycle_script_path": project.lifecycle_script_path,
            },
            "manifest": {
                "id": manifest.id,
                "intended_operation": manifest.intended_operation,
                "included_paths": manifest.included_paths,
                "excluded_paths": manifest.excluded_paths,
                "ignored_paths": manifest.ignored_paths,
                "secret_filter_rules": manifest.secret_filter_rules,
            },
            "ideal_lifecycle_functions": ideal_functions,
            "approved_files": file_payload,
            "user_instructions": (user_instructions or "").strip(),
        }
        return (
            AIAssistancePromptMessage(
                role="system",
                content=(
                    "You are assisting OrchFlow with a review-driven Windows .bat "
                    "lifecycle proposal. Return valid JSON only. Do not claim the "
                    "proposal has been applied. Do not request or reveal secrets. "
                    "Use first-argument dispatch labels for lifecycle actions."
                ),
            ),
            AIAssistancePromptMessage(
                role="user",
                content=(
                    "Create an analysis proposal with these JSON fields: "
                    "lifecycle_strategy string, runtime_hints string array, "
                    "candidate_script_content string, action_mappings array of "
                    "{canonical_action, script_label, rationale}, and warnings "
                    "string array.\n\n"
                    f"{json.dumps(user_payload, ensure_ascii=False)}"
                ),
            ),
        )

    def _parse_analysis_proposal_content(
        self,
        completion: str,
    ) -> AnalysisProposalContent:
        payload = self._parse_json_payload(completion)
        lifecycle_strategy = self._required_string(payload, "lifecycle_strategy")
        candidate_script_content = self._required_string(
            payload,
            "candidate_script_content",
        )
        runtime_hints = self._string_tuple(payload.get("runtime_hints", ()))
        warnings = self._string_tuple(payload.get("warnings", ()))
        action_mappings = self._parse_action_mappings(payload.get("action_mappings", ()))
        if not candidate_script_content.strip():
            raise AIAssistanceError("AI proposal must include candidate script content.")
        return AnalysisProposalContent(
            lifecycle_strategy=lifecycle_strategy,
            runtime_hints=runtime_hints,
            candidate_script_content=candidate_script_content,
            action_mappings=action_mappings,
            warnings=warnings,
        )

    @staticmethod
    def _parse_json_payload(completion: str) -> dict[str, Any]:
        text = completion.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 3:
                text = "\n".join(lines[1:-1]).strip()
                if text.startswith("json"):
                    text = text.removeprefix("json").strip()
        try:
            payload = json.loads(text)
        except JSONDecodeError as error:
            raise AIAssistanceError("AI proposal response must be valid JSON.") from error
        if not isinstance(payload, dict):
            raise AIAssistanceError("AI proposal response must be a JSON object.")
        return payload

    @staticmethod
    def _required_string(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise AIAssistanceError(f"AI proposal field '{key}' is required.")
        return value.strip()

    @staticmethod
    def _string_tuple(value: Any) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)):
            return ()
        return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())

    def _parse_action_mappings(
        self,
        raw_mappings: Any,
    ) -> tuple[ProposedLifecycleActionMapping, ...]:
        if not isinstance(raw_mappings, (list, tuple)):
            return ()
        mappings: list[ProposedLifecycleActionMapping] = []
        for raw_mapping in raw_mappings:
            if not isinstance(raw_mapping, dict):
                continue
            canonical_action = raw_mapping.get("canonical_action")
            script_label = raw_mapping.get("script_label")
            rationale = raw_mapping.get("rationale")
            if canonical_action not in {"status", "start", "stop", "restart"}:
                continue
            if not isinstance(script_label, str) or not script_label.strip():
                continue
            mappings.append(
                ProposedLifecycleActionMapping(
                    canonical_action=cast(
                        Literal["status", "start", "stop", "restart"],
                        canonical_action,
                    ),
                    script_label=script_label.strip(),
                    rationale=rationale.strip() if isinstance(rationale, str) else None,
                )
            )
        return tuple(mappings)
