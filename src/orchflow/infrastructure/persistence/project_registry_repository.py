"""Persistence repository for project registry use cases."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from orchflow.application.project_registry import ProjectMappingInput, ProjectRegistryRepository
from orchflow.domain.access_control import User, UserRole
from orchflow.domain.project_registry import (
    CanonicalLifecycleAction,
    LifecycleActionMapping,
    LifecycleFunctionDecision,
    MappingSource,
    Project,
)
from orchflow.infrastructure.persistence.models import (
    AuditEventModel,
    LifecycleActionMappingModel,
    LifecycleFunctionDecisionModel,
    ProjectModel,
    ProjectOwnerModel,
)


def _to_mapping(model: LifecycleActionMappingModel) -> LifecycleActionMapping:
    return LifecycleActionMapping(
        id=model.id,
        project_id=model.project_id,
        canonical_action=CanonicalLifecycleAction(model.canonical_action),
        script_label=model.script_label,
        source=MappingSource(model.source),
        configured_by_user_id=model.configured_by_user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_function_decision(model: LifecycleFunctionDecisionModel) -> LifecycleFunctionDecision:
    return LifecycleFunctionDecision(
        id=model.id,
        project_id=model.project_id,
        canonical_action=CanonicalLifecycleAction(model.canonical_action),
        state=model.state,
        decided_by_user_id=model.decided_by_user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_project(
    model: ProjectModel,
    owner_user_ids: tuple[int, ...],
    mappings: tuple[LifecycleActionMapping, ...],
    function_decisions: tuple[LifecycleFunctionDecision, ...],
) -> Project:
    return Project(
        id=model.id,
        reference_name=model.reference_name,
        description=model.description,
        project_root_path=model.project_root_path,
        lifecycle_script_path=model.lifecycle_script_path,
        created_by_user_id=model.created_by_user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        owner_user_ids=owner_user_ids,
        action_mappings=mappings,
        lifecycle_function_decisions=function_decisions,
    )


class SqlAlchemyProjectRegistryRepository(ProjectRegistryRepository):
    """SQLAlchemy-backed repository for project registry use cases."""

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

    def get_project_by_reference_name(self, reference_name: str) -> Project | None:
        with self._session_scope() as session:
            model = (
                session.query(ProjectModel)
                .filter(ProjectModel.reference_name == reference_name)
                .one_or_none()
            )
            return self._inflate_project(session, model) if model else None

    def create_project(
        self,
        *,
        reference_name: str,
        description: str | None,
        project_root_path: str,
        lifecycle_script_path: str,
        created_by_user_id: int,
        owner_user_ids: tuple[int, ...],
        mappings: tuple[ProjectMappingInput, ...],
    ) -> Project:
        with self._session_scope() as session:
            model = ProjectModel(
                reference_name=reference_name,
                description=description,
                project_root_path=project_root_path,
                lifecycle_script_path=lifecycle_script_path,
                created_by_user_id=created_by_user_id,
            )
            session.add(model)
            session.flush()

            for owner_user_id in owner_user_ids:
                session.add(ProjectOwnerModel(project_id=model.id, user_id=owner_user_id))

            for mapping in mappings:
                session.add(
                    LifecycleActionMappingModel(
                        project_id=model.id,
                        canonical_action=mapping.canonical_action.value,
                        script_label=mapping.script_label,
                        source=mapping.source.value,
                        configured_by_user_id=created_by_user_id,
                    )
                )

            session.flush()
            session.refresh(model)
            return self._inflate_project(session, model)

    def list_projects_for_user(self, user: User) -> list[Project]:
        with self._session_scope() as session:
            query = select(ProjectModel).order_by(ProjectModel.id.asc())
            if user.role is not UserRole.ADMIN:
                query = (
                    select(ProjectModel)
                    .join(ProjectOwnerModel, ProjectOwnerModel.project_id == ProjectModel.id)
                    .where(ProjectOwnerModel.user_id == user.id)
                    .order_by(ProjectModel.id.asc())
                )
            models = session.execute(query).scalars().all()
            return [self._inflate_project(session, model) for model in models]

    def replace_lifecycle_function_configuration(
        self,
        *,
        project_id: int,
        mappings: tuple[ProjectMappingInput, ...],
        unconfigured_actions: tuple[CanonicalLifecycleAction, ...],
        decided_by_user_id: int,
    ) -> Project | None:
        with self._session_scope() as session:
            model = session.get(ProjectModel, project_id)
            if model is None:
                return None
            existing_mappings = (
                session.execute(
                    select(LifecycleActionMappingModel).where(
                        LifecycleActionMappingModel.project_id == project_id
                    )
                )
                .scalars()
                .all()
            )
            for existing_mapping in existing_mappings:
                session.delete(existing_mapping)

            existing_decisions = (
                session.execute(
                    select(LifecycleFunctionDecisionModel).where(
                        LifecycleFunctionDecisionModel.project_id == project_id
                    )
                )
                .scalars()
                .all()
            )
            for existing_decision in existing_decisions:
                session.delete(existing_decision)

            session.flush()

            for mapping in mappings:
                session.add(
                    LifecycleActionMappingModel(
                        project_id=project_id,
                        canonical_action=mapping.canonical_action.value,
                        script_label=mapping.script_label,
                        source=mapping.source.value,
                        configured_by_user_id=decided_by_user_id,
                    )
                )

            for action in unconfigured_actions:
                session.add(
                    LifecycleFunctionDecisionModel(
                        project_id=project_id,
                        canonical_action=action.value,
                        state="unconfigured",
                        decided_by_user_id=decided_by_user_id,
                    )
                )

            session.flush()
            return self._inflate_project(session, model)

    def update_project(
        self,
        *,
        project_id: int,
        reference_name: str,
        description: str | None,
        project_root_path: str,
        lifecycle_script_path: str,
        mappings: tuple[ProjectMappingInput, ...],
        unconfigured_actions: tuple[CanonicalLifecycleAction, ...],
        updated_by_user_id: int,
    ) -> Project | None:
        with self._session_scope() as session:
            model = session.get(ProjectModel, project_id)
            if model is None:
                return None

            model.reference_name = reference_name
            model.description = description
            model.project_root_path = project_root_path
            model.lifecycle_script_path = lifecycle_script_path

            existing_mappings = (
                session.execute(
                    select(LifecycleActionMappingModel).where(
                        LifecycleActionMappingModel.project_id == project_id
                    )
                )
                .scalars()
                .all()
            )
            for existing_mapping in existing_mappings:
                session.delete(existing_mapping)

            existing_decisions = (
                session.execute(
                    select(LifecycleFunctionDecisionModel).where(
                        LifecycleFunctionDecisionModel.project_id == project_id
                    )
                )
                .scalars()
                .all()
            )
            for existing_decision in existing_decisions:
                session.delete(existing_decision)

            session.flush()

            for mapping in mappings:
                session.add(
                    LifecycleActionMappingModel(
                        project_id=project_id,
                        canonical_action=mapping.canonical_action.value,
                        script_label=mapping.script_label,
                        source=mapping.source.value,
                        configured_by_user_id=updated_by_user_id,
                    )
                )

            for action in unconfigured_actions:
                session.add(
                    LifecycleFunctionDecisionModel(
                        project_id=project_id,
                        canonical_action=action.value,
                        state="unconfigured",
                        decided_by_user_id=updated_by_user_id,
                    )
                )

            session.flush()
            return self._inflate_project(session, model)

    def get_project_for_user(self, project_id: int, user: User) -> Project | None:
        with self._session_scope() as session:
            model = session.get(ProjectModel, project_id)
            if model is None:
                return None
            project = self._inflate_project(session, model)
            if user.role is UserRole.ADMIN or user.id in project.owner_user_ids:
                return project
            return None

    def add_project_owner(self, *, project_id: int, user_id: int) -> Project | None:
        with self._session_scope() as session:
            model = session.get(ProjectModel, project_id)
            if model is None:
                return None
            existing_owner = (
                session.execute(
                    select(ProjectOwnerModel)
                    .where(ProjectOwnerModel.project_id == project_id)
                    .where(ProjectOwnerModel.user_id == user_id)
                )
                .scalars()
                .one_or_none()
            )
            if existing_owner is None:
                session.add(ProjectOwnerModel(project_id=project_id, user_id=user_id))
                session.flush()
            return self._inflate_project(session, model)

    def remove_project_owner(self, *, project_id: int, user_id: int) -> Project | None:
        with self._session_scope() as session:
            model = session.get(ProjectModel, project_id)
            if model is None:
                return None
            owner = (
                session.execute(
                    select(ProjectOwnerModel)
                    .where(ProjectOwnerModel.project_id == project_id)
                    .where(ProjectOwnerModel.user_id == user_id)
                )
                .scalars()
                .one_or_none()
            )
            if owner is not None:
                session.delete(owner)
                session.flush()
            return self._inflate_project(session, model)

    def record_audit_event(
        self,
        *,
        actor_user_id: int,
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

    def _inflate_project(self, session: Session, model: ProjectModel) -> Project:
        owner_ids = tuple(
            session.execute(
                select(ProjectOwnerModel.user_id).where(ProjectOwnerModel.project_id == model.id)
            )
            .scalars()
            .all()
        )
        mapping_models = (
            session.execute(
                select(LifecycleActionMappingModel)
                .where(LifecycleActionMappingModel.project_id == model.id)
                .order_by(LifecycleActionMappingModel.id.asc())
            )
            .scalars()
            .all()
        )
        mappings = tuple(_to_mapping(mapping_model) for mapping_model in mapping_models)
        function_decision_models = (
            session.execute(
                select(LifecycleFunctionDecisionModel)
                .where(LifecycleFunctionDecisionModel.project_id == model.id)
                .order_by(LifecycleFunctionDecisionModel.id.asc())
            )
            .scalars()
            .all()
        )
        function_decisions = tuple(
            _to_function_decision(function_decision_model)
            for function_decision_model in function_decision_models
        )
        return _to_project(model, owner_ids, mappings, function_decisions)
