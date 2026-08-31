"""Application service for operational audit history visibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from orchflow.application.access_control import AuthorizationError
from orchflow.domain.access_control import AuditEvent, User, UserRole


class AuditHistoryError(Exception):
    """Base exception for audit history application failures."""


class AuditHistoryValidationError(AuditHistoryError):
    """Raised when audit history input is invalid."""


@dataclass(frozen=True, slots=True)
class AuditEventFilters:
    """Optional filters for admin audit history visibility."""

    actor_user_id: int | None = None
    action: str | None = None
    project_id: int | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None


@dataclass(frozen=True, slots=True)
class ListAuditEventsCommand:
    """Input required to list recent audit events."""

    token: str
    limit: int = 25
    filters: AuditEventFilters = field(default_factory=AuditEventFilters)


class AuditHistoryRepository(Protocol):
    """Repository boundary for audit history visibility."""

    def list_recent_audit_events(
        self,
        *,
        limit: int,
        filters: AuditEventFilters,
    ) -> list[AuditEvent]: ...

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
        filters = self._validate_filters(command.filters)
        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="admin.audit_events.list",
            target_type="audit_event",
            target_id=None,
            details=self._build_list_details(limit, filters),
        )
        return self._repository.list_recent_audit_events(limit=limit, filters=filters)

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

    @staticmethod
    def _validate_filters(filters: AuditEventFilters) -> AuditEventFilters:
        if filters.actor_user_id is not None and filters.actor_user_id < 1:
            raise AuditHistoryValidationError("Audit history actor filter must be at least 1.")
        if filters.project_id is not None and filters.project_id < 1:
            raise AuditHistoryValidationError("Audit history project filter must be at least 1.")
        action = filters.action.strip() if filters.action is not None else None
        if action == "":
            raise AuditHistoryValidationError("Audit history action filter cannot be empty.")
        if (
            filters.created_from is not None
            and filters.created_to is not None
            and filters.created_from > filters.created_to
        ):
            raise AuditHistoryValidationError(
                "Audit history start time must be before the end time."
            )
        return AuditEventFilters(
            actor_user_id=filters.actor_user_id,
            action=action,
            project_id=filters.project_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )

    @staticmethod
    def _build_list_details(limit: int, filters: AuditEventFilters) -> str:
        details = [f"limit:{limit}"]
        if filters.actor_user_id is not None:
            details.append(f"actor_user_id:{filters.actor_user_id}")
        if filters.action is not None:
            details.append(f"action:{filters.action}")
        if filters.project_id is not None:
            details.append(f"project_id:{filters.project_id}")
        if filters.created_from is not None:
            details.append(f"created_from:{filters.created_from.isoformat()}")
        if filters.created_to is not None:
            details.append(f"created_to:{filters.created_to.isoformat()}")
        return ";".join(details)
