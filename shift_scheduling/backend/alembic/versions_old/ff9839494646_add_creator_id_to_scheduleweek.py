"""add creator_id to scheduleweek

Revision ID: ff9839494646
Revises: 4016b5c9268d
Create Date: 2026-09-05 02:06:42.753708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff9839494646'
down_revision: Union[str, Sequence[str], None] = '4016b5c9268d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "scheduleweek",
        sa.Column("creator_id", sa.Integer(), nullable=True)
    )

    op.create_foreign_key(
        None,
        "scheduleweek",
        "user",
        ["creator_id"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        None,
        "scheduleweek",
        type_="foreignkey"
    )

    op.drop_column(
        "scheduleweek",
        "creator_id"
    )
