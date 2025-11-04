"""create executor_category_access table

Revision ID: b1e4c7f9a3d2
Revises: f8a9c3d5e1b2
Create Date: 2025-11-04 12:00:00.000000

BE-018: Модель доступу виконавців до категорій

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'b1e4c7f9a3d2'
down_revision = 'f8a9c3d5e1b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    BE-018: Create executor_category_access table
    
    Maps executors to categories they have access to.
    Each executor-category pair must be unique.
    """
    # Create executor_category_access table
    op.create_table(
        'executor_category_access',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('executor_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('category_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['executor_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    )
    
    # Create unique constraint on executor-category pair
    # This ensures each executor can have access to a category only once
    op.create_unique_constraint(
        'uq_executor_category_access_executor_category',
        'executor_category_access',
        ['executor_id', 'category_id']
    )
    
    # Create indexes for fast lookups
    # Index on executor_id for queries like "get all categories for this executor"
    op.create_index(
        'ix_executor_category_access_executor_id',
        'executor_category_access',
        ['executor_id']
    )
    
    # Index on category_id for queries like "get all executors who have access to this category"
    op.create_index(
        'ix_executor_category_access_category_id',
        'executor_category_access',
        ['category_id']
    )
    
    # Index on id for primary key lookups
    op.create_index(
        'ix_executor_category_access_id',
        'executor_category_access',
        ['id']
    )


def downgrade() -> None:
    """
    BE-018: Drop executor_category_access table
    """
    # Drop indexes
    op.drop_index('ix_executor_category_access_id', table_name='executor_category_access')
    op.drop_index('ix_executor_category_access_category_id', table_name='executor_category_access')
    op.drop_index('ix_executor_category_access_executor_id', table_name='executor_category_access')
    
    # Drop unique constraint
    op.drop_constraint('uq_executor_category_access_executor_category', 'executor_category_access', type_='unique')
    
    # Drop table
    op.drop_table('executor_category_access')
