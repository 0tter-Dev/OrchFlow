"""bootstrap persistence base

Revision ID: 6bdc38282503
Revises: 
Create Date: 2026-08-23 16:28:58.430455

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "6bdc38282503"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
