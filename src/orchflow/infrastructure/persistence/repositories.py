"""Persistence repositories for OrchFlow."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from orchflow.application.access_control import UserRepository
from orchflow.application.audit_history import AuditHistoryRepository
from orchflow.domain.access_control import AuditEvent, User, UserRole
from orchflow.infrastructure.persistence.models import AuditEventModel, UserModel


def _to_audit_event(model: AuditEventModel) -> AuditEvent:
    return AuditEvent(
        id=model.id,
        actor_user_id=model.actor_user_id,
        action=model.action,
        target_type=model.target_type,
        target_id=model.target_id,
        details=model.details,
        created_at=model.created_at,
    )


def _to_user(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        role=UserRole(model.role),
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
        last_login_at=model.last_login_at,
            )


class SqlAlchemyAuditHistoryRepository(AuditHistoryRepository):
    """SQLAlchemy-backed repository for recent audit history visibility."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _session_scope(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def list_recent_audit_events(self, limit: int) -> list[AuditEvent]:
        with self._session_scope() as session:
            models = (
                session.execute(
                    select(AuditEventModel)
                    .order_by(AuditEventModel.id.desc())
                    .limit(limit)
                )
                .scalars()
                .all()
            )
            return [_to_audit_event(model) for model in models]

    def record_audit_event(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None:
        with self._session_scope() as session:
            session.add(
                AuditEventModel(
                    actor_user_id=actor_user_id,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    details=details,
                )
            )


class SqlAlchemyUserRepository(UserRepository):
    """SQLAlchemy-backed repository for access control use cases."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    @contextmanager
    def _session_scope(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def count_users(self) -> int:
        with self._session_scope() as session:
            return session.query(UserModel).count()

    def get_user_by_username(self, username: str) -> User | None:
        with self._session_scope() as session:
            model = session.query(UserModel).filter(UserModel.username == username).one_or_none()
            return _to_user(model) if model else None

    def get_user_by_id(self, user_id: int) -> User | None:
        with self._session_scope() as session:
            model = session.get(UserModel, user_id)
            return _to_user(model) if model else None

    def get_password_hash_by_username(self, username: str) -> str | None:
        with self._session_scope() as session:
            model = session.query(UserModel).filter(UserModel.username == username).one_or_none()
            return model.password_hash if model else None

    def create_user(self, username: str, password_hash: str, role: UserRole) -> User:
        with self._session_scope() as session:
            model = UserModel(
                username=username,
                password_hash=password_hash,
                role=role.value,
                is_active=True,
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_user(model)

    def update_last_login(self, user_id: int) -> User:
        with self._session_scope() as session:
            model = session.get(UserModel, user_id)
            if model is None:
                raise ValueError(f"User id '{user_id}' does not exist.")
            model.last_login_at = datetime.now(UTC)
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_user(model)

    def list_users(self) -> list[User]:
        with self._session_scope() as session:
            models = session.query(UserModel).order_by(UserModel.id.asc()).all()
            return [_to_user(model) for model in models]

    def update_user(
        self,
        *,
        user_id: int,
        role: UserRole | None,
        is_active: bool | None,
    ) -> User | None:
        with self._session_scope() as session:
            model = session.get(UserModel, user_id)
            if model is None:
                return None
            if role is not None:
                model.role = role.value
            if is_active is not None:
                model.is_active = is_active
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_user(model)

    def record_audit_event(
        self,
        *,
        actor_user_id: int | None,
        action: str,
        target_type: str,
        target_id: str | None,
        details: str | None,
    ) -> None:
        with self._session_scope() as session:
            session.add(
                AuditEventModel(
                    actor_user_id=actor_user_id,
                    action=action,
                    target_type=target_type,
                    target_id=target_id,
                    details=details,
                )
            )
