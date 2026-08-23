"""Security primitives for access control."""

from __future__ import annotations

from base64 import b64encode
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import bcrypt
from jose import JWTError, jwt  # type: ignore[import-untyped]

from orchflow.application.access_control import AuthenticationError, PasswordHasher, TokenManager
from orchflow.domain.access_control import AccessToken, User
from orchflow.infrastructure.config.settings import AppSettings, get_settings


def _normalize_password(password: str) -> bytes:
    """Normalize password bytes before bcrypt to avoid the 72-byte input limit."""
    digest = sha256(password.encode("utf-8")).digest()
    return b64encode(digest)


class BcryptPasswordHasher(PasswordHasher):
    """Password hasher backed directly by bcrypt with SHA-256 prehashing."""

    def hash_password(self, password: str) -> str:
        normalized_password = _normalize_password(password)
        hashed_password = bcrypt.hashpw(normalized_password, bcrypt.gensalt())
        return hashed_password.decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        normalized_password = _normalize_password(password)
        return bcrypt.checkpw(normalized_password, password_hash.encode("utf-8"))


class JwtTokenManager(TokenManager):
    """JWT token manager for OrchFlow access tokens."""

    def __init__(self, settings: AppSettings | None = None) -> None:
        self._settings = settings or get_settings()

    def issue_access_token(self, user: User) -> AccessToken:
        expires_in_seconds = self._settings.jwt_access_token_expire_minutes * 60
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "type": "access",
            "exp": expires_at,
        }
        token = jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )
        return AccessToken(
            access_token=token,
            token_type="bearer",
            expires_in_seconds=expires_in_seconds,
        )

    def parse_access_token(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except JWTError as error:
            raise AuthenticationError("Invalid or expired access token.") from error

        subject = payload.get("sub")
        token_type = payload.get("type")
        if subject is None or token_type != "access":
            raise AuthenticationError("Invalid or expired access token.")
        return int(subject)
