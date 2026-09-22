"""Add persisted visual preferences.

Revision ID: c8d5e2f1a4b6
Revises: b7c4e1d2a9f0
Create Date: 2026-09-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "c8d5e2f1a4b6"
down_revision: str | None = "b7c4e1d2a9f0"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Add deterministic defaults for existing preference records."""
    connection = op.get_bind()
    columns = {column["name"] for column in sa.inspect(connection).get_columns("user_preferences")}
    if "appearance_mode" not in columns:
        op.add_column(
            "user_preferences",
            sa.Column(
                "appearance_mode",
                sa.String(length=32),
                nullable=False,
                server_default="gray-dark",
            ),
        )
    if "accent_color" not in columns:
        op.add_column(
            "user_preferences",
            sa.Column("accent_color", sa.String(length=16), nullable=False, server_default="green"),
        )


def downgrade() -> None:
    """Remove visual preference columns."""
    op.drop_column("user_preferences", "accent_color")
    op.drop_column("user_preferences", "appearance_mode")
