"""ai context manifests

Revision ID: 42f2b6b5a7e1
Revises: e4d4c6b7a9d0
Create Date: 2026-08-30 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "42f2b6b5a7e1"
down_revision: str | None = "e4d4c6b7a9d0"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "ai_authorized_context_manifests" in inspector.get_table_names():
        return

    op.create_table(
        "ai_authorized_context_manifests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer(), nullable=False),
        sa.Column("selected_model", sa.String(length=128), nullable=False),
        sa.Column("intended_operation", sa.String(length=64), nullable=False),
        sa.Column("project_root_path", sa.String(length=512), nullable=False),
        sa.Column("include_patterns", sa.Text(), nullable=False),
        sa.Column("exclude_patterns", sa.Text(), nullable=False),
        sa.Column("included_paths", sa.Text(), nullable=False),
        sa.Column("excluded_paths", sa.Text(), nullable=False),
        sa.Column("ignored_paths", sa.Text(), nullable=False),
        sa.Column("secret_filter_rules", sa.Text(), nullable=False),
        sa.Column("max_file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("max_total_bytes", sa.Integer(), nullable=False),
        sa.Column("total_included_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "ai_authorized_context_manifests" not in inspector.get_table_names():
        return

    op.drop_table("ai_authorized_context_manifests")
