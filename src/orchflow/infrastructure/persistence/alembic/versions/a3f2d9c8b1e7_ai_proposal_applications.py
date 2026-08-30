"""Add AI analysis proposal application records.

Revision ID: a3f2d9c8b1e7
Revises: c84b6fd2e0aa
Create Date: 2026-08-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3f2d9c8b1e7"
down_revision: str | None = "c84b6fd2e0aa"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the AI analysis proposal applications table."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "ai_analysis_proposal_applications" in inspector.get_table_names():
        return

    op.create_table(
        "ai_analysis_proposal_applications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "proposal_id",
            sa.Integer(),
            sa.ForeignKey("ai_analysis_proposals.id"),
            nullable=False,
        ),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column(
            "applied_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("lifecycle_script_path", sa.String(length=512), nullable=False),
        sa.Column("persisted_mappings", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "proposal_id",
            name="uq_ai_analysis_proposal_applications_proposal",
        ),
    )


def downgrade() -> None:
    """Drop the AI analysis proposal applications table."""
    op.drop_table("ai_analysis_proposal_applications")
