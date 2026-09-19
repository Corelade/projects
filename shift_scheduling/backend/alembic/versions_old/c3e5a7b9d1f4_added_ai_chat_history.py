"""added ai chat history

Revision ID: c3e5a7b9d1f4
Revises: b7d2e4f6a8c1
Create Date: 2026-09-19 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c3e5a7b9d1f4'
down_revision: Union[str, Sequence[str], None] = 'b7d2e4f6a8c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'aichat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=False),
        sa.Column('message_count', sa.Integer(), nullable=False),
        sa.Column('tool_call_count', sa.Integer(), nullable=False),
        sa.Column('error_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_aichat_user_id'), 'aichat', ['user_id'], unique=False)

    op.create_table(
        'aichatmessage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('tool_arguments', sa.JSON(), nullable=True),
        sa.Column('is_error', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['aichat.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_aichatmessage_chat_id'), 'aichatmessage', ['chat_id'], unique=False)
    op.create_index(op.f('ix_aichatmessage_tool_name'), 'aichatmessage', ['tool_name'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_aichatmessage_tool_name'), table_name='aichatmessage')
    op.drop_index(op.f('ix_aichatmessage_chat_id'), table_name='aichatmessage')
    op.drop_table('aichatmessage')
    op.drop_index(op.f('ix_aichat_user_id'), table_name='aichat')
    op.drop_table('aichat')
