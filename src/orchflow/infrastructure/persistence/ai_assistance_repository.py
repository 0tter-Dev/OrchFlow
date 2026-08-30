"""Persistence repository for AI assistance manifests."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Literal, cast

from sqlalchemy.orm import Session, sessionmaker

from orchflow.application.ai_assistance import (
    AIAnalysisProposal,
    AIAnalysisProposalApplication,
    AIAnalysisProposalReview,
    AIAnalysisProposalReviewDecision,
    AIAnalysisProposalValidationStatus,
    AIAssistanceManifestOperation,
    AIAssistanceManifestRepository,
    AuthorizedContextManifest,
    ProposedLifecycleActionMapping,
)
from orchflow.domain.project_registry import Project
from orchflow.infrastructure.persistence.models import (
    AIAnalysisProposalApplicationModel,
    AIAnalysisProposalModel,
    AIAnalysisProposalReviewModel,
    AIAuthorizedContextManifestModel,
)


def _to_json(values: tuple[str, ...]) -> str:
    return json.dumps(list(values), separators=(",", ":"))


def _from_json(value: str) -> tuple[str, ...]:
    raw_values = json.loads(value)
    if not isinstance(raw_values, list):
        return ()
    return tuple(raw_value for raw_value in raw_values if isinstance(raw_value, str))


def _mappings_to_json(values: tuple[ProposedLifecycleActionMapping, ...]) -> str:
    return json.dumps(
        [
            {
                "canonical_action": value.canonical_action,
                "script_label": value.script_label,
                "rationale": value.rationale,
            }
            for value in values
        ],
        separators=(",", ":"),
    )


def _mappings_from_json(value: str) -> tuple[ProposedLifecycleActionMapping, ...]:
    raw_values = json.loads(value)
    if not isinstance(raw_values, list):
        return ()
    mappings: list[ProposedLifecycleActionMapping] = []
    for raw_value in raw_values:
        if not isinstance(raw_value, dict):
            continue
        canonical_action = raw_value.get("canonical_action")
        script_label = raw_value.get("script_label")
        rationale = raw_value.get("rationale")
        if canonical_action not in {"status", "start", "stop", "restart"}:
            continue
        if not isinstance(script_label, str):
            continue
        mappings.append(
            ProposedLifecycleActionMapping(
                canonical_action=cast(
                    Literal["status", "start", "stop", "restart"],
                    canonical_action,
                ),
                script_label=script_label,
                rationale=rationale if isinstance(rationale, str) else None,
            )
        )
    return tuple(mappings)


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


def _to_proposal(model: AIAnalysisProposalModel) -> AIAnalysisProposal:
    return AIAnalysisProposal(
        id=model.id,
        manifest_id=model.manifest_id,
        project_id=model.project_id,
        requested_by_user_id=model.requested_by_user_id,
        selected_model=model.selected_model,
        intended_operation=cast(AIAssistanceManifestOperation, model.intended_operation),
        lifecycle_strategy=model.lifecycle_strategy,
        runtime_hints=_from_json(model.runtime_hints),
        candidate_script_content=model.candidate_script_content,
        action_mappings=_mappings_from_json(model.action_mappings),
        warnings=_from_json(model.warnings),
        created_at=model.created_at,
    )


def _to_review(model: AIAnalysisProposalReviewModel) -> AIAnalysisProposalReview:
    return AIAnalysisProposalReview(
        id=model.id,
        proposal_id=model.proposal_id,
        project_id=model.project_id,
        reviewer_user_id=model.reviewer_user_id,
        decision=cast(AIAnalysisProposalReviewDecision, model.decision),
        validation_status=cast(AIAnalysisProposalValidationStatus, model.validation_status),
        validation_errors=_from_json(model.validation_errors),
        reviewer_notes=model.reviewer_notes,
        created_at=model.created_at,
    )


def _to_application(
    model: AIAnalysisProposalApplicationModel,
) -> AIAnalysisProposalApplication:
    return AIAnalysisProposalApplication(
        id=model.id,
        proposal_id=model.proposal_id,
        project_id=model.project_id,
        applied_by_user_id=model.applied_by_user_id,
        lifecycle_script_path=model.lifecycle_script_path,
        persisted_mappings=_mappings_from_json(model.persisted_mappings),
        project=None,
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

    def create_analysis_proposal(
        self,
        *,
        manifest_id: int,
        project_id: int,
        requested_by_user_id: int,
        selected_model: str,
        intended_operation: AIAssistanceManifestOperation,
        lifecycle_strategy: str,
        runtime_hints: tuple[str, ...],
        candidate_script_content: str,
        action_mappings: tuple[ProposedLifecycleActionMapping, ...],
        warnings: tuple[str, ...],
    ) -> AIAnalysisProposal:
        with self._session_scope() as session:
            model = AIAnalysisProposalModel(
                manifest_id=manifest_id,
                project_id=project_id,
                requested_by_user_id=requested_by_user_id,
                selected_model=selected_model,
                intended_operation=intended_operation,
                lifecycle_strategy=lifecycle_strategy,
                runtime_hints=_to_json(runtime_hints),
                candidate_script_content=candidate_script_content,
                action_mappings=_mappings_to_json(action_mappings),
                warnings=_to_json(warnings),
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_proposal(model)

    def get_analysis_proposal(
        self,
        proposal_id: int,
    ) -> AIAnalysisProposal | None:
        with self._session_scope() as session:
            model = session.get(AIAnalysisProposalModel, proposal_id)
            return _to_proposal(model) if model is not None else None

    def create_analysis_proposal_review(
        self,
        *,
        proposal_id: int,
        project_id: int,
        reviewer_user_id: int,
        decision: AIAnalysisProposalReviewDecision,
        validation_status: AIAnalysisProposalValidationStatus,
        validation_errors: tuple[str, ...],
        reviewer_notes: str | None,
    ) -> AIAnalysisProposalReview:
        with self._session_scope() as session:
            model = AIAnalysisProposalReviewModel(
                proposal_id=proposal_id,
                project_id=project_id,
                reviewer_user_id=reviewer_user_id,
                decision=decision,
                validation_status=validation_status,
                validation_errors=_to_json(validation_errors),
                reviewer_notes=reviewer_notes,
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return _to_review(model)

    def get_analysis_proposal_review_for_proposal(
        self,
        proposal_id: int,
    ) -> AIAnalysisProposalReview | None:
        with self._session_scope() as session:
            model = (
                session.query(AIAnalysisProposalReviewModel)
                .filter(AIAnalysisProposalReviewModel.proposal_id == proposal_id)
                .one_or_none()
            )
            return _to_review(model) if model is not None else None

    def create_analysis_proposal_application(
        self,
        *,
        proposal_id: int,
        project_id: int,
        applied_by_user_id: int,
        lifecycle_script_path: str,
        persisted_mappings: tuple[ProposedLifecycleActionMapping, ...],
        project: Project,
    ) -> AIAnalysisProposalApplication:
        with self._session_scope() as session:
            model = AIAnalysisProposalApplicationModel(
                proposal_id=proposal_id,
                project_id=project_id,
                applied_by_user_id=applied_by_user_id,
                lifecycle_script_path=lifecycle_script_path,
                persisted_mappings=_mappings_to_json(persisted_mappings),
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            application = _to_application(model)
            return AIAnalysisProposalApplication(
                id=application.id,
                proposal_id=application.proposal_id,
                project_id=application.project_id,
                applied_by_user_id=application.applied_by_user_id,
                lifecycle_script_path=application.lifecycle_script_path,
                persisted_mappings=application.persisted_mappings,
                project=project,
                created_at=application.created_at,
            )

    def get_analysis_proposal_application_for_proposal(
        self,
        proposal_id: int,
    ) -> AIAnalysisProposalApplication | None:
        with self._session_scope() as session:
            model = (
                session.query(AIAnalysisProposalApplicationModel)
                .filter(AIAnalysisProposalApplicationModel.proposal_id == proposal_id)
                .one_or_none()
            )
            return _to_application(model) if model is not None else None
