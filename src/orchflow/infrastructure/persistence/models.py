"""SQLAlchemy ORM models for OrchFlow persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from orchflow.infrastructure.persistence.base import Base


class UserModel(Base):
    """Persisted OrchFlow user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEventModel(Base):
    """Persisted audit event."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(64))
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ProjectModel(Base):
    """Persisted OrchFlow project definition."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reference_name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_root_path: Mapped[str] = mapped_column(String(512))
    lifecycle_script_path: Mapped[str] = mapped_column(String(512))
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ProjectOwnerModel(Base):
    """Persisted project ownership relation."""

    __tablename__ = "project_owners"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_owners_project_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class LifecycleActionMappingModel(Base):
    """Persisted project-specific lifecycle action mapping."""

    __tablename__ = "lifecycle_action_mappings"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "canonical_action",
            name="uq_lifecycle_action_mappings_project_action",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    canonical_action: Mapped[str] = mapped_column(String(16), nullable=False)
    script_label: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    configured_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class LifecycleFunctionDecisionModel(Base):
    """Persisted explicit lifecycle function configuration decision."""

    __tablename__ = "lifecycle_function_decisions"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "canonical_action",
            name="uq_lifecycle_function_decisions_project_action",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    canonical_action: Mapped[str] = mapped_column(String(16), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    decided_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class AIAuthorizedContextManifestModel(Base):
    """Persisted AI context authorization manifest metadata."""

    __tablename__ = "ai_authorized_context_manifests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    selected_model: Mapped[str] = mapped_column(String(128), nullable=False)
    intended_operation: Mapped[str] = mapped_column(String(64), nullable=False)
    project_root_path: Mapped[str] = mapped_column(String(512), nullable=False)
    include_patterns: Mapped[str] = mapped_column(Text, nullable=False)
    exclude_patterns: Mapped[str] = mapped_column(Text, nullable=False)
    included_paths: Mapped[str] = mapped_column(Text, nullable=False)
    excluded_paths: Mapped[str] = mapped_column(Text, nullable=False)
    ignored_paths: Mapped[str] = mapped_column(Text, nullable=False)
    secret_filter_rules: Mapped[str] = mapped_column(Text, nullable=False)
    max_file_size_bytes: Mapped[int] = mapped_column(nullable=False)
    max_total_bytes: Mapped[int] = mapped_column(nullable=False)
    total_included_bytes: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class AIAnalysisProposalModel(Base):
    """Persisted reviewable AI analysis proposal."""

    __tablename__ = "ai_analysis_proposals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    manifest_id: Mapped[int] = mapped_column(
        ForeignKey("ai_authorized_context_manifests.id"),
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    selected_model: Mapped[str] = mapped_column(String(128), nullable=False)
    intended_operation: Mapped[str] = mapped_column(String(64), nullable=False)
    lifecycle_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    runtime_hints: Mapped[str] = mapped_column(Text, nullable=False)
    candidate_script_content: Mapped[str] = mapped_column(Text, nullable=False)
    action_mappings: Mapped[str] = mapped_column(Text, nullable=False)
    warnings: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class AIAnalysisProposalReviewModel(Base):
    """Persisted review decision for an AI analysis proposal."""

    __tablename__ = "ai_analysis_proposal_reviews"
    __table_args__ = (
        UniqueConstraint(
            "proposal_id",
            name="uq_ai_analysis_proposal_reviews_proposal",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("ai_analysis_proposals.id"),
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    reviewer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(16), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(16), nullable=False)
    validation_errors: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
