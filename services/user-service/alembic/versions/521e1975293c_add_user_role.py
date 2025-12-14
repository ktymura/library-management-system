"""add user role

Revision ID: 521e1975293c
Revises: 8dcfa8539d30
Create Date: 2025-12-14 19:58:12.819867

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "521e1975293c"
down_revision: Union[str, Sequence[str], None] = "8dcfa8539d30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    user_role = sa.Enum("READER", "LIBRARIAN", "ADMIN", name="user_role")
    user_role.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users",
        sa.Column("role", user_role, server_default="READER", nullable=False),
    )


def downgrade():
    user_role = sa.Enum("READER", "LIBRARIAN", "ADMIN", name="user_role")
    op.drop_column("users", "role")
    user_role.drop(op.get_bind(), checkfirst=True)
