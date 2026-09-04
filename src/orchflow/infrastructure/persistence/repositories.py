"""Persistence repositories for OrchFlow."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from orchflow.application.access_control import UserRepository
from orchflow.application.audit_history import AuditEventFilters, AuditHistoryRepository
from orchflow.application.user_preferences import UserPreferencesRepository
from orchflow.domain.access_control import AuditEvent, User, UserRole
from orchflow.domain.user_preferences import ProjectViewMode, UserLocale, UserPreferences
from orchflow.infrastructure.persistence.models import (
    AuditEventModel,
    UserModel,
    UserPreferenceModel,
)


def _to_audit_event(model: AuditEventModel) -> AuditEvent:
    created_at = model.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return AuditEvent(
        id=model.id,
        actor_user_id=model.actor_user_id,
        action=model.action,
        target_type=model.target_type,
        target_id=model.target_id,
        details=model.details,
        created_at=created_at,
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


def _to_user_preferences(model: UserPreferenceModel) -> UserPreferences:
    return UserPreferences(
        user_id=model.user_id,
        locale=UserLocale(model.locale),
        project_view_mode=ProjectViewMode(model.project_view_mode),
        status_refresh_interval_seconds=model.status_refresh_interval_seconds,
    )


def _to_persistence_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


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

    def list_recent_audit_events(
        self,
        *,
        limit: int,
        filters: AuditEventFilters,
    ) -> list[AuditEvent]:
        with self._session_scope() as session:
            statement = select(AuditEventModel)
            if filters.actor_user_id is not None:
                statement = statement.where(
                    AuditEventModel.actor_user_id == filters.actor_user_id
                )
            if filters.action is not None:
                statement = statement.where(AuditEventModel.action == filters.action)
            if filters.project_id is not None:
                statement = statement.where(
                    AuditEventModel.target_type == "project",
                    AuditEventModel.target_id == str(filters.project_id),
                )
            if filters.created_from is not None:
                statement = statement.where(
                    AuditEventModel.created_at
                    >= _to_persistence_datetime(filters.created_from)
                )
            if filters.created_to is not None:
                statement = statement.where(
                    AuditEventModel.created_at <= _to_persistence_datetime(filters.created_to)
                )
            models = (
                session.execute(
                    statement.order_by(AuditEventModel.id.desc()).limit(limit)
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


class SqlAlchemyUserPreferencesRepository(UserPreferencesRepository):
    """SQLAlchemy-backed repository for user-owned interface preferences."""

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

    def get_preferences_by_user_id(self, user_id: int) -> UserPreferences | None:
        with self._session_scope() as session:
            model = (
                session.execute(
                    select(UserPreferenceModel).where(
                        UserPreferenceModel.user_id == user_id
                    )
                )
                .scalars()
                .one_or_none()
            )
            return _to_user_preferences(model) if model else None

    def upsert_preferences(self, preferences: UserPreferences) -> UserPreferences:
        with self._session_scope() as session:
            model = (
                session.execute(
                    select(UserPreferenceModel).where(
                        UserPreferenceModel.user_id == preferences.user_id
                    )
                )
                .scalars()
                .one_or_none()
            )
            if model is None:
                model = UserPreferenceModel(user_id=preferences.user_id)
            model.locale = preferences.locale.value
            model.project_view_mode = preferences.project_view_mode.value
            model.status_refresh_interval_seconds = (
                preferences.status_refresh_interval_seconds
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_user_preferences(model)

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
