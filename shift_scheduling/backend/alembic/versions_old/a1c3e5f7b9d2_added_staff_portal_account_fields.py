"""added staff portal account fields

Revision ID: a1c3e5f7b9d2
Revises: ff9839494646
Create Date: 2026-09-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1c3e5f7b9d2'
down_revision: Union[str, Sequence[str], None] = 'ff9839494646'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('staff', sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('staff', sa.Column('invite_token_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('staff', sa.Column('invite_expires_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_staff_invite_token_hash'), 'staff', ['invite_token_hash'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_staff_invite_token_hash'), table_name='staff')
    op.drop_column('staff', 'invite_expires_at')
    op.drop_column('staff', 'invite_token_hash')
    op.drop_column('staff', 'password')
