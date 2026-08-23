"""Application service for OrchFlow access control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from orchflow.domain.access_control import AccessToken, User, UserRole


class AccessControlError(Exception):
    """Base exception for access control application failures."""


class AuthenticationError(AccessControlError):
    """Raised when user credentials or tokens are invalid."""


class AuthorizationError(AccessControlError):
    """Raised when a user lacks permission to perform an action."""


class UserConflictError(AccessControlError):
    """Raised when a user creation request conflicts with existing state."""


@dataclass(frozen=True, slots=True)
class RegisterUserCommand:
    """Input required to create a new OrchFlow user."""

    username: str
    password: str
    requested_role: UserRole | None = None
    actor_token: str | None = None


@dataclass(frozen=True, slots=True)
class LoginCommand:
    """Input required to authenticate a user."""

    username: str
    password: str


class UserRepository(Protocol):
    """Repository boundary used by the access control application service."""

    def count_users(self) -> int: ...

    def get_user_by_username(self, username: str) -> User | None: ...

    def get_user_by_id(self, user_id: int) -> User | None: ...

    def get_password_hash_by_username(self, username: str) -> str | None: ...

    def create_user(self, username: str, password_hash: str, role: UserRole) -> User: ...

    def update_last_login(self, user_id: int) -> User: ...

    def list_users(self) -> list[User]: ...

    def record_audit_event(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None: ...


class PasswordHasher(Protocol):
    """Password hashing boundary."""

    def hash_password(self, password: str) -> str: ...

    def verify_password(self, password: str, password_hash: str) -> bool: ...


class TokenManager(Protocol):
    """JWT token management boundary."""

    def issue_access_token(self, user: User) -> AccessToken: ...

    def parse_access_token(self, token: str) -> int: ...


class AccessControlService:
    """Application-layer service for authentication and authorization."""

    def __init__(
        self,
        repository: UserRepository,
        password_hasher: PasswordHasher,
        token_manager: TokenManager,
    ) -> None:
        self._repository = repository
        self._password_hasher = password_hasher
        self._token_manager = token_manager

    def register_user(self, command: RegisterUserCommand) -> User:
        """Create a new OrchFlow user under the current authorization rules."""
        username = command.username.strip().lower()
        self._validate_username(username)
        self._validate_password(command.password)

        if self._repository.get_user_by_username(username) is not None:
            raise UserConflictError(f"User '{username}' already exists.")

        current_user_count = self._repository.count_users()
        resolved_role = UserRole.ADMIN if current_user_count == 0 else (
            command.requested_role or UserRole.MEMBER
        )
        actor = self._resolve_actor(command.actor_token) if command.actor_token else None

        if current_user_count > 0 and resolved_role is UserRole.ADMIN:
            self._ensure_admin(actor)

        password_hash = self._password_hasher.hash_password(command.password)
        created_user = self._repository.create_user(username, password_hash, resolved_role)
        details = (
            "bootstrap-admin-created"
            if current_user_count == 0
            else f"user-created-with-role:{created_user.role.value}"
        )
        self._repository.record_audit_event(
            actor_user_id=actor.id if actor else created_user.id,
            action="user.register",
            target_type="user",
            target_id=str(created_user.id),
            details=details,
        )
        return created_user

    def login(self, command: LoginCommand) -> AccessToken:
        """Authenticate a user and return a signed access token."""
        username = command.username.strip().lower()
        user = self._repository.get_user_by_username(username)
        if user is None:
            raise AuthenticationError("Invalid username or password.")

        stored_hash = self._repository.get_password_hash_by_username(username)
        if stored_hash is None or not self._password_hasher.verify_password(
            command.password,
            stored_hash,
        ):
            raise AuthenticationError("Invalid username or password.")

        if not user.is_active:
            raise AuthorizationError("User is inactive.")

        user = self._repository.update_last_login(user.id)
        self._repository.record_audit_event(
            actor_user_id=user.id,
            action="user.login",
            target_type="user",
            target_id=str(user.id),
            details="access-token-issued",
        )
        return self._token_manager.issue_access_token(user)

    def get_current_user(self, token: str) -> User:
        """Resolve the current authenticated user from a bearer token."""
        user_id = self._token_manager.parse_access_token(token)
        user = self._repository.get_user_by_id(user_id)
        if user is None:
            raise AuthenticationError("Authenticated user no longer exists.")
        if not user.is_active:
            raise AuthorizationError("User is inactive.")
        return user

    def list_users(self, token: str) -> list[User]:
        """Return the user list for an authenticated admin."""
        actor = self.get_current_user(token)
        self._ensure_admin(actor)
        users = self._repository.list_users()
        self._repository.record_audit_event(
            actor_user_id=actor.id,
            action="admin.list_users",
            target_type="user",
            target_id=None,
            details=f"user-count:{len(users)}",
        )
        return users

    def _resolve_actor(self, token: str) -> User:
        return self.get_current_user(token)

    @staticmethod
    def _ensure_admin(user: User | None) -> None:
        if user is None or user.role is not UserRole.ADMIN:
            raise AuthorizationError("Admin privileges are required for this action.")

    @staticmethod
    def _validate_username(username: str) -> None:
        if len(username) < 3:
            raise UserConflictError("Username must contain at least 3 characters.")

    @staticmethod
    def _validate_password(password: str) -> None:
        if len(password) < 8:
            raise UserConflictError("Password must contain at least 8 characters.")
