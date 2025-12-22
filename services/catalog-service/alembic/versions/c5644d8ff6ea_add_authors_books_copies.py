"""add authors, books, copies

Revision ID: c5644d8ff6ea
Revises:
Create Date: 2025-12-15 18:27:31.979389
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision = "c5644d8ff6ea"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # --- ENUM copy_status (tylko dla Postgresa) ---
    # create_type=False => SQLAlchemy nie będzie próbował tworzyć typu automatycznie przy kolumnie
    copy_status_pg_enum = postgresql.ENUM(
        "AVAILABLE",
        "LOANED",
        "LOST",
        "DAMAGED",
        name="copy_status",
        create_type=False,
    )

    if dialect_name == "postgresql":
        # Bezpieczne utworzenie typu, jeśli go jeszcze nie ma
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'copy_status') THEN
                    CREATE TYPE copy_status AS ENUM ('AVAILABLE','LOANED','LOST','DAMAGED');
                END IF;
            END$$;
            """
        )

    # --- authors ---
    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_authors_full_name", "authors", ["full_name"])

    # --- books ---
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=20), nullable=True, unique=True),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["authors.id"],
            name="fk_books_author_id_authors",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("isbn", name="uq_books_isbn"),
    )
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_author_id", "books", ["author_id"])

    # --- copies ---
    status_type = copy_status_pg_enum if dialect_name == "postgresql" else sa.String(length=50)

    op.create_table(
        "copies",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("inventory_code", sa.String(length=64), nullable=False),
        sa.Column("status", status_type, nullable=False, server_default="AVAILABLE"),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=False), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["book_id"],
            ["books.id"],
            name="fk_copies_book_id_books",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("inventory_code", name="uq_copies_inventory_code"),
    )
    op.create_index("ix_copies_book_id", "copies", ["book_id"])
    op.create_index("ix_copies_status", "copies", ["status"])


def downgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    op.drop_index("ix_copies_status", table_name="copies")
    op.drop_index("ix_copies_book_id", table_name="copies")
    op.drop_table("copies")

    op.drop_index("ix_books_author_id", table_name="books")
    op.drop_index("ix_books_title", table_name="books")
    op.drop_table("books")

    op.drop_index("ix_authors_full_name", table_name="authors")
    op.drop_table("authors")

    if dialect_name == "postgresql":
        # Usuń typ tylko jeśli jest nieużywany i istnieje
        op.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'copy_status') THEN
                    DROP TYPE copy_status;
                END IF;
            END$$;
            """
        )
