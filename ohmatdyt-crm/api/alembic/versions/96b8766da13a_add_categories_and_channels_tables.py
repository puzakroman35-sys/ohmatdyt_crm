"""add_categories_and_channels_tables

Revision ID: 96b8766da13a
Revises: aa277b59a681
Create Date: 2025-10-28 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96b8766da13a'
down_revision: Union[str, None] = 'aa277b59a681'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_categories_name')
    )
    
    # Create indexes for categories
    op.create_index('ix_categories_id', 'categories', ['id'])
    op.create_index('ix_categories_name', 'categories', ['name'])
    op.create_index('ix_categories_is_active', 'categories', ['is_active'])
    
    # Create channels table
    op.create_table(
        'channels',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_channels_name')
    )
    
    # Create indexes for channels
    op.create_index('ix_channels_id', 'channels', ['id'])
    op.create_index('ix_channels_name', 'channels', ['name'])
    op.create_index('ix_channels_is_active', 'channels', ['is_active'])


def downgrade() -> None:
    # Drop channels table and indexes
    op.drop_index('ix_channels_is_active', table_name='channels')
    op.drop_index('ix_channels_name', table_name='channels')
    op.drop_index('ix_channels_id', table_name='channels')
    op.drop_table('channels')
    
    # Drop categories table and indexes
    op.drop_index('ix_categories_is_active', table_name='categories')
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_index('ix_categories_id', table_name='categories')
    op.drop_table('categories')
