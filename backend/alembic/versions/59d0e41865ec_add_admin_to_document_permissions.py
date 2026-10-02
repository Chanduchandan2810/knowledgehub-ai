"""add admin to document permissions

Revision ID: 59d0e41865ec
Revises: ab4161eb0117
Create Date: 2026-10-02 16:53:41.684589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '59d0e41865ec'
down_revision: Union[str, Sequence[str], None] = 'ab4161eb0117'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Alter employee_id to be nullable
    op.alter_column('document_permissions', 'employee_id', existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    
    # 2. Add admin_id column
    op.add_column('document_permissions', sa.Column('admin_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_document_permissions_admin_id'), 'document_permissions', ['admin_id'], unique=False)
    
    # 3. Add foreign key for admin_id
    op.create_foreign_key('fk_doc_perm_admin', 'document_permissions', 'admins', ['admin_id'], ['id'], ondelete='CASCADE')
    
    # 4. Add check constraint enforcing exactly one identity
    op.create_check_constraint('chk_one_identity', 'document_permissions', 'num_nonnulls(employee_id, admin_id) = 1')
    
    # 5. Add unique constraint for admin_id
    op.create_unique_constraint('uq_document_admin_permission', 'document_permissions', ['document_id', 'admin_id'])


def downgrade() -> None:
    # 1. Drop unique constraint for admin_id
    op.drop_constraint('uq_document_admin_permission', 'document_permissions', type_='unique')
    
    # 2. Drop check constraint
    op.drop_constraint('chk_one_identity', 'document_permissions', type_='check')
    
    # 3. Drop foreign key and index
    op.drop_constraint('fk_doc_perm_admin', 'document_permissions', type_='foreignkey')
    op.drop_index(op.f('ix_document_permissions_admin_id'), table_name='document_permissions')
    
    # 4. Drop admin_id column
    op.drop_column('document_permissions', 'admin_id')
    
    # 5. Alter employee_id back to not null (this might fail if there are rows with employee_id = NULL)
    op.execute("DELETE FROM document_permissions WHERE employee_id IS NULL")
    op.alter_column('document_permissions', 'employee_id', existing_type=postgresql.UUID(as_uuid=True), nullable=False)
