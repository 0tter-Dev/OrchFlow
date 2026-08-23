"""Access control domain contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class UserRole(StrEnum):
    """Supported OrchFlow user roles."""

    ADMIN = "admin"
    MEMBER = "member"


@dataclass(frozen=True, slots=True)
class User:
    """Persisted OrchFlow user."""

    id: int
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None


@dataclass(frozen=True, slots=True)
class AccessToken:
    """Authenticated access token payload."""

    access_token: str
    token_type: str
    expires_in_seconds: int


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Audit event emitted by access control operations."""

    id: int
    actor_user_id: int | None
    action: str
    target_type: str
    target_id: str | None
    details: str | None
    created_at: datetime
