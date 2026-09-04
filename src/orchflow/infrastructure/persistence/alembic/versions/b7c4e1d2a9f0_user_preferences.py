"""Add user interface preferences.

Revision ID: b7c4e1d2a9f0
Revises: a3f2d9c8b1e7
Create Date: 2026-09-04
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7c4e1d2a9f0"
down_revision: str | None = "a3f2d9c8b1e7"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the user preferences table."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "user_preferences" in inspector.get_table_names():
        return

    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("project_view_mode", sa.String(length=16), nullable=False),
        sa.Column("status_refresh_interval_seconds", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", name="uq_user_preferences_user"),
    )


def downgrade() -> None:
    """Drop the user preferences table."""
    op.drop_table("user_preferences")
