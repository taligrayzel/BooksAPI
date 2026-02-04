"""Add genres table

Revision ID: 50cb3bdc9ea8
Revises: 4918773a4ee4
Create Date: 2026-02-01 19:52:01.842546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50cb3bdc9ea8'
down_revision: Union[str, Sequence[str], None] = '4918773a4ee4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create genres table."""
    op.create_table(
        'genres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop genres table."""
    op.drop_table('genres')
