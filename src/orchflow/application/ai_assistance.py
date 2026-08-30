"""Application boundary for review-driven AI assistance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from orchflow.domain.access_control import User

AIAssistanceGatewayStatus = Literal["disabled", "configured", "misconfigured"]
AIAssistanceHealthStatus = Literal["disabled", "healthy", "unhealthy", "unsupported"]


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


class CurrentUserResolver(Protocol):
    """Boundary used to resolve the current authenticated user."""

    def get_current_user(self, token: str) -> User: ...


class AIAssistanceService:
    """Coordinates safe AI assistance operations owned by OrchFlow."""

    def __init__(
        self,
        gateway: AIAssistanceGateway,
        current_user_resolver: CurrentUserResolver,
        audit_recorder: AIAssistanceAuditRecorder,
    ) -> None:
        self._gateway = gateway
        self._current_user_resolver = current_user_resolver
        self._audit_recorder = audit_recorder

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
