"""create_cases_table

Revision ID: d332e58ad7a9
Revises: 96b8766da13a
Create Date: 2025-10-28 16:19:35.213383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd332e58ad7a9'
down_revision: Union[str, None] = '96b8766da13a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create cases table
    op.create_table(
        'cases',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('public_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=False),
        sa.Column('channel_id', sa.UUID(), nullable=False),
        sa.Column('author_id', sa.UUID(), nullable=False),
        sa.Column('responsible_id', sa.UUID(), nullable=True),
        sa.Column('subcategory', sa.String(length=200), nullable=True),
        sa.Column('applicant_name', sa.String(length=200), nullable=False),
        sa.Column('applicant_phone', sa.String(length=50), nullable=True),
        sa.Column('applicant_email', sa.String(length=100), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('NEW', 'IN_PROGRESS', 'NEEDS_INFO', 'REJECTED', 'DONE', name='casestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['responsible_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('public_id', name='uq_cases_public_id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_cases_id', 'cases', ['id'])
    op.create_index('ix_cases_public_id', 'cases', ['public_id'])
    op.create_index('ix_cases_category_id', 'cases', ['category_id'])
    op.create_index('ix_cases_channel_id', 'cases', ['channel_id'])
    op.create_index('ix_cases_author_id', 'cases', ['author_id'])
    op.create_index('ix_cases_responsible_id', 'cases', ['responsible_id'])
    op.create_index('ix_cases_status', 'cases', ['status'])
    op.create_index('ix_cases_created_at', 'cases', ['created_at'])
    
    # Composite indexes for common query patterns (as per BE-004 requirements)
    op.create_index('ix_cases_status_created_at', 'cases', ['status', 'created_at'])
    op.create_index('ix_cases_category_status', 'cases', ['category_id', 'status'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_cases_category_status', table_name='cases')
    op.drop_index('ix_cases_status_created_at', table_name='cases')
    op.drop_index('ix_cases_created_at', table_name='cases')
    op.drop_index('ix_cases_status', table_name='cases')
    op.drop_index('ix_cases_responsible_id', table_name='cases')
    op.drop_index('ix_cases_author_id', table_name='cases')
    op.drop_index('ix_cases_channel_id', table_name='cases')
    op.drop_index('ix_cases_category_id', table_name='cases')
    op.drop_index('ix_cases_public_id', table_name='cases')
    op.drop_index('ix_cases_id', table_name='cases')
    
    # Drop table
    op.drop_table('cases')
    
    # Drop enum type
    op.execute("DROP TYPE casestatus")
