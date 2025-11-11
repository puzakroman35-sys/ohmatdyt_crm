"""add_notification_logs_table

Revision ID: c3270fdffae6
Revises: b1e4c7f9a3d2
Create Date: 2025-11-11 16:32:36.454740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3270fdffae6'
down_revision: Union[str, None] = 'b1e4c7f9a3d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notification_logs table
    op.create_table('notification_logs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('notification_type', sa.Enum('NEW_CASE', 'CASE_TAKEN', 'STATUS_CHANGED', 'NEW_COMMENT', 'TEMP_PASSWORD', 'CASE_REASSIGNED', 'CASE_ESCALATION', name='notificationtype'), nullable=False),
    sa.Column('recipient_email', sa.String(length=100), nullable=False),
    sa.Column('recipient_user_id', sa.UUID(), nullable=True),
    sa.Column('related_case_id', sa.UUID(), nullable=True),
    sa.Column('related_entity_id', sa.String(length=100), nullable=True),
    sa.Column('subject', sa.String(length=500), nullable=False),
    sa.Column('body_text', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'SENT', 'FAILED', 'RETRYING', name='notificationstatus'), nullable=False),
    sa.Column('retry_count', sa.Integer(), nullable=False),
    sa.Column('max_retries', sa.Integer(), nullable=False),
    sa.Column('last_error', sa.Text(), nullable=True),
    sa.Column('error_details', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('failed_at', sa.DateTime(), nullable=True),
    sa.Column('next_retry_at', sa.DateTime(), nullable=True),
    sa.Column('celery_task_id', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['recipient_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['related_case_id'], ['cases.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_logs_celery_task_id'), 'notification_logs', ['celery_task_id'], unique=False)
    op.create_index(op.f('ix_notification_logs_created_at'), 'notification_logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_notification_logs_id'), 'notification_logs', ['id'], unique=False)
    op.create_index(op.f('ix_notification_logs_next_retry_at'), 'notification_logs', ['next_retry_at'], unique=False)
    op.create_index(op.f('ix_notification_logs_notification_type'), 'notification_logs', ['notification_type'], unique=False)
    op.create_index(op.f('ix_notification_logs_recipient_email'), 'notification_logs', ['recipient_email'], unique=False)
    op.create_index(op.f('ix_notification_logs_recipient_user_id'), 'notification_logs', ['recipient_user_id'], unique=False)
    op.create_index(op.f('ix_notification_logs_related_case_id'), 'notification_logs', ['related_case_id'], unique=False)
    op.create_index(op.f('ix_notification_logs_status'), 'notification_logs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notification_logs_status'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_related_case_id'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_recipient_user_id'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_recipient_email'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_notification_type'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_next_retry_at'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_id'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_created_at'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_celery_task_id'), table_name='notification_logs')
    op.drop_table('notification_logs')
