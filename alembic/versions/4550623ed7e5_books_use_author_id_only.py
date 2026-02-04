"""books use author_id only

Revision ID: 4550623ed7e5
Revises: 802c5049d1b5
Create Date: 2026-02-02 10:45:10.565204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4550623ed7e5'
down_revision: Union[str, Sequence[str], None] = '802c5049d1b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_tables = set(insp.get_table_names(schema="public"))

    # Your DB was created manually and was missing these tables,
    # but your models + stamped revision assume they exist.
    if "genres" not in existing_tables:
        op.create_table(
            "genres",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if "tasks" not in existing_tables:
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.PrimaryKeyConstraint("id"),
        )

    # Backfill books.author_id using books.author (string) before dropping it.
    # 1) Insert missing authors based on books.author values
    op.execute(
        sa.text(
            """
            INSERT INTO public.authors (name)
            SELECT DISTINCT b.author
            FROM public.books b
            WHERE b.author IS NOT NULL
              AND b.author <> ''
              AND NOT EXISTS (
                SELECT 1 FROM public.authors a WHERE a.name = b.author
              );
            """
        )
    )

    # 2) Update books.author_id by matching author name
    op.execute(
        sa.text(
            """
            UPDATE public.books b
            SET author_id = a.id
            FROM public.authors a
            WHERE b.author_id IS NULL
              AND b.author IS NOT NULL
              AND b.author <> ''
              AND a.name = b.author;
            """
        )
    )

    # 3) Any remaining NULL author_id -> assign to an 'Unknown' author
    op.execute(
        sa.text(
            """
            INSERT INTO public.authors (name)
            SELECT 'Unknown'
            WHERE NOT EXISTS (SELECT 1 FROM public.authors WHERE name = 'Unknown');
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE public.books
            SET author_id = (SELECT id FROM public.authors WHERE name = 'Unknown')
            WHERE author_id IS NULL;
            """
        )
    )

    # 4) Enforce NOT NULL and drop the old author column
    op.alter_column("books", "author_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("books", "author")


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add author string column and populate it from the authors table.
    op.add_column("books", sa.Column("author", sa.String(length=255), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE public.books b
            SET author = a.name
            FROM public.authors a
            WHERE b.author_id = a.id;
            """
        )
    )
    op.alter_column("books", "author_id", existing_type=sa.Integer(), nullable=True)
