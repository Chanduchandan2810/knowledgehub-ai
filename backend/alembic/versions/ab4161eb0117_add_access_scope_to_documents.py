"""add_access_scope_to_documents

Revision ID: ab4161eb0117
Revises: 40b349d287b5
Create Date: 2026-10-02 15:51:00.267450

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab4161eb0117'
down_revision: Union[str, Sequence[str], None] = '40b349d287b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add column as nullable first to safely update existing rows
    op.add_column('documents', sa.Column('access_scope', sa.String(), nullable=True))
    
    # Update all existing documents to RESTRICTED to preserve implicit legacy behavior
    op.execute("UPDATE documents SET access_scope = 'RESTRICTED'")
    
    # Alter column to enforce NOT NULL and default for future rows
    op.alter_column('documents', 'access_scope', nullable=False, server_default='ORGANIZATION')


def downgrade() -> None:
    op.drop_column('documents', 'access_scope')
