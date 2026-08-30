"""Add AI analysis proposal review decisions.

Revision ID: c84b6fd2e0aa
Revises: 6c3b2e9f1a44
Create Date: 2026-08-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c84b6fd2e0aa"
down_revision: str | None = "6c3b2e9f1a44"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the AI analysis proposal reviews table."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "ai_analysis_proposal_reviews" in inspector.get_table_names():
        return

    op.create_table(
        "ai_analysis_proposal_reviews",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "proposal_id",
            sa.Integer(),
            sa.ForeignKey("ai_analysis_proposals.id"),
            nullable=False,
        ),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column(
            "reviewer_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("validation_status", sa.String(length=16), nullable=False),
        sa.Column("validation_errors", sa.Text(), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "proposal_id",
            name="uq_ai_analysis_proposal_reviews_proposal",
        ),
    )


def downgrade() -> None:
    """Drop the AI analysis proposal reviews table."""
    op.drop_table("ai_analysis_proposal_reviews")
