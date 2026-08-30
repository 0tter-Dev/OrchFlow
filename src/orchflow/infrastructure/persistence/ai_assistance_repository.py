"""Persistence repository for AI assistance manifests."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

from sqlalchemy.orm import Session, sessionmaker

from orchflow.application.ai_assistance import (
    AIAssistanceManifestOperation,
    AIAssistanceManifestRepository,
    AuthorizedContextManifest,
)
from orchflow.infrastructure.persistence.models import AIAuthorizedContextManifestModel


def _to_json(values: tuple[str, ...]) -> str:
    return json.dumps(list(values), separators=(",", ":"))


def _from_json(value: str) -> tuple[str, ...]:
    raw_values = json.loads(value)
    if not isinstance(raw_values, list):
        return ()
    return tuple(raw_value for raw_value in raw_values if isinstance(raw_value, str))


def _to_manifest(model: AIAuthorizedContextManifestModel) -> AuthorizedContextManifest:
    return AuthorizedContextManifest(
        id=model.id,
        project_id=model.project_id,
        requested_by_user_id=model.requested_by_user_id,
        selected_model=model.selected_model,
        intended_operation=cast(AIAssistanceManifestOperation, model.intended_operation),
        project_root_path=model.project_root_path,
        include_patterns=_from_json(model.include_patterns),
        exclude_patterns=_from_json(model.exclude_patterns),
        included_paths=_from_json(model.included_paths),
        excluded_paths=_from_json(model.excluded_paths),
        ignored_paths=_from_json(model.ignored_paths),
        secret_filter_rules=_from_json(model.secret_filter_rules),
        max_file_size_bytes=model.max_file_size_bytes,
        max_total_bytes=model.max_total_bytes,
        total_included_bytes=model.total_included_bytes,
        created_at=model.created_at,
    )


class SqlAlchemyAIAssistanceRepository(AIAssistanceManifestRepository):
    """SQLAlchemy-backed repository for AI assistance context manifests."""

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
    ) -> AuthorizedContextManifest:
        with self._session_scope() as session:
            model = AIAuthorizedContextManifestModel(
                project_id=project_id,
                requested_by_user_id=requested_by_user_id,
                selected_model=selected_model,
                intended_operation=intended_operation,
                project_root_path=project_root_path,
                include_patterns=_to_json(include_patterns),
                exclude_patterns=_to_json(exclude_patterns),
                included_paths=_to_json(included_paths),
                excluded_paths=_to_json(excluded_paths),
                ignored_paths=_to_json(ignored_paths),
                secret_filter_rules=_to_json(secret_filter_rules),
                max_file_size_bytes=max_file_size_bytes,
                max_total_bytes=max_total_bytes,
                total_included_bytes=total_included_bytes,
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_manifest(model)

    def get_authorized_context_manifest(
        self,
        manifest_id: int,
    ) -> AuthorizedContextManifest | None:
        with self._session_scope() as session:
            model = session.get(AIAuthorizedContextManifestModel, manifest_id)
            return _to_manifest(model) if model is not None else None
