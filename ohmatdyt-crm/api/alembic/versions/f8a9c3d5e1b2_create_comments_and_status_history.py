"""create comments and status history

Revision ID: f8a9c3d5e1b2
Revises: e9f3a5b2c8d1
Create Date: 2025-10-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f8a9c3d5e1b2'
down_revision = 'e9f3a5b2c8d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create comments table
    op.create_table(
        'comments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('author_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('is_internal', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='RESTRICT'),
    )
    
    # Create status_history table
    op.create_table(
        'status_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('changed_by_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('old_status', sa.Enum('NEW', 'IN_PROGRESS', 'NEEDS_INFO', 'REJECTED', 'DONE', name='casestatus'), nullable=True),
        sa.Column('new_status', sa.Enum('NEW', 'IN_PROGRESS', 'NEEDS_INFO', 'REJECTED', 'DONE', name='casestatus'), nullable=False, index=True),
        sa.Column('changed_at', sa.DateTime, nullable=False, index=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ondelete='RESTRICT'),
    )


def downgrade() -> None:
    op.drop_table('status_history')
    op.drop_table('comments')
