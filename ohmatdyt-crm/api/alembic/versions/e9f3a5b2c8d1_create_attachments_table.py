"""create attachments table

Revision ID: e9f3a5b2c8d1
Revises: d332e58ad7a9
Create Date: 2025-10-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e9f3a5b2c8d1'
down_revision: Union[str, None] = 'd332e58ad7a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create attachments table"""
    op.create_table(
        'attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('original_name', sa.String(length=255), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='RESTRICT'),
        
        # Indexes
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_attachments_id', 'attachments', ['id'])
    op.create_index('ix_attachments_case_id', 'attachments', ['case_id'])
    op.create_index('ix_attachments_uploaded_by_id', 'attachments', ['uploaded_by_id'])
    op.create_index('ix_attachments_created_at', 'attachments', ['created_at'])


def downgrade() -> None:
    """Drop attachments table"""
    op.drop_index('ix_attachments_created_at', table_name='attachments')
    op.drop_index('ix_attachments_uploaded_by_id', table_name='attachments')
    op.drop_index('ix_attachments_case_id', table_name='attachments')
    op.drop_index('ix_attachments_id', table_name='attachments')
    op.drop_table('attachments')
