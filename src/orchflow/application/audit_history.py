"""Application service for operational audit history visibility."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orchflow.application.access_control import AuthorizationError
from orchflow.domain.access_control import AuditEvent, User, UserRole


class AuditHistoryError(Exception):
    """Base exception for audit history application failures."""


class AuditHistoryValidationError(AuditHistoryError):
    """Raised when audit history input is invalid."""


@dataclass(frozen=True, slots=True)
class ListAuditEventsCommand:
    """Input required to list recent audit events."""

    token: str
    limit: int = 25


class AuditHistoryRepository(Protocol):
    """Repository boundary for audit history visibility."""

    def list_recent_audit_events(self, limit: int) -> list[AuditEvent]: ...

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


class AuditHistoryService:
    """Application-layer service for recent audit history visibility."""

    def __init__(
        self,
        repository: AuditHistoryRepository,
        current_user_resolver: CurrentUserResolver,
    ) -> None:
        self._repository = repository
        self._current_user_resolver = current_user_resolver

    def list_recent_events(self, command: ListAuditEventsCommand) -> list[AuditEvent]:
        """Return recent audit events for authenticated administrators."""
        actor = self._current_user_resolver.get_current_user(command.token)
        self._ensure_admin(actor)
        limit = self._validate_limit(command.limit)
        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="admin.audit_events.list",
            target_type="audit_event",
            target_id=None,
            details=f"limit:{limit}",
        )
        return self._repository.list_recent_audit_events(limit)

    @staticmethod
    def _ensure_admin(user: User) -> None:
        if user.role is not UserRole.ADMIN:
            raise AuthorizationError("Admin privileges are required for this action.")

    @staticmethod
    def _validate_limit(limit: int) -> int:
        if limit < 1:
            raise AuditHistoryValidationError("Audit history limit must be at least 1.")
        if limit > 100:
            raise AuditHistoryValidationError("Audit history limit must be at most 100.")
        return limit
