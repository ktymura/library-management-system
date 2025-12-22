"""add gin indexes

Revision ID: 5767386c227b
Revises: c5644d8ff6ea
Create Date: 2025-12-22 19:14:08.998351
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "5767386c227b"
down_revision = "c5644d8ff6ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name != "postgresql":
        # GIN + pg_trgm są specyficzne dla Postgresa
        return

    # 1) extension dla trigramów (potrzebne do gin_trgm_ops)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # 2) indeks GIN na books.title pod ILIKE '%query%'
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_books_title_gin_trgm
        ON books
        USING GIN (title gin_trgm_ops);
        """
    )

    # 3) indeks GIN na authors.full_name pod ILIKE '%query%'
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_authors_full_name_gin_trgm
        ON authors
        USING GIN (full_name gin_trgm_ops);
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS ix_authors_full_name_gin_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_books_title_gin_trgm;")
