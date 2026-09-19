"""added availability requests and notifications

Revision ID: b7d2e4f6a8c1
Revises: a1c3e5f7b9d2
Create Date: 2026-09-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b7d2e4f6a8c1'
down_revision: Union[str, Sequence[str], None] = 'a1c3e5f7b9d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'availabilityrequest',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('day_exclusions', sa.JSON(), nullable=False),
        sa.Column('shift_exclusions', sa.JSON(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('admin_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['user.id']),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_availabilityrequest_staff_id'), 'availabilityrequest', ['staff_id'], unique=False)
    op.create_index(op.f('ix_availabilityrequest_creator_id'), 'availabilityrequest', ['creator_id'], unique=False)
    op.create_index(op.f('ix_availabilityrequest_status'), 'availabilityrequest', ['status'], unique=False)

    op.create_table(
        'notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipient_user_id', sa.Integer(), nullable=True),
        sa.Column('recipient_staff_id', sa.Integer(), nullable=True),
        sa.Column('kind', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['recipient_staff_id'], ['staff.id']),
        sa.ForeignKeyConstraint(['recipient_user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['request_id'], ['availabilityrequest.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_notification_recipient_user_id'), 'notification', ['recipient_user_id'], unique=False)
    op.create_index(op.f('ix_notification_recipient_staff_id'), 'notification', ['recipient_staff_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_notification_recipient_staff_id'), table_name='notification')
    op.drop_index(op.f('ix_notification_recipient_user_id'), table_name='notification')
    op.drop_table('notification')
    op.drop_index(op.f('ix_availabilityrequest_status'), table_name='availabilityrequest')
    op.drop_index(op.f('ix_availabilityrequest_creator_id'), table_name='availabilityrequest')
    op.drop_index(op.f('ix_availabilityrequest_staff_id'), table_name='availabilityrequest')
    op.drop_table('availabilityrequest')
