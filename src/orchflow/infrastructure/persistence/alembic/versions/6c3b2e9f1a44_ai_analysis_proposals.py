"""Add AI analysis proposal persistence.

Revision ID: 6c3b2e9f1a44
Revises: 42f2b6b5a7e1
Create Date: 2026-08-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c3b2e9f1a44"
down_revision: str | None = "42f2b6b5a7e1"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the AI analysis proposals table."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "ai_analysis_proposals" in inspector.get_table_names():
        return

    op.create_table(
        "ai_analysis_proposals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "manifest_id",
            sa.Integer(),
            sa.ForeignKey("ai_authorized_context_manifests.id"),
            nullable=False,
        ),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column(
            "requested_by_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("selected_model", sa.String(length=128), nullable=False),
        sa.Column("intended_operation", sa.String(length=64), nullable=False),
        sa.Column("lifecycle_strategy", sa.Text(), nullable=False),
        sa.Column("runtime_hints", sa.Text(), nullable=False),
        sa.Column("candidate_script_content", sa.Text(), nullable=False),
        sa.Column("action_mappings", sa.Text(), nullable=False),
        sa.Column("warnings", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Drop the AI analysis proposals table."""
    op.drop_table("ai_analysis_proposals")
