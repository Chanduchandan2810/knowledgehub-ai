"""Add document management tables

Revision ID: d3d62d3d7867
Revises: cf534e8dc4eb
Create Date: 2026-09-30 15:26:53.328455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3d62d3d7867'
down_revision: Union[str, Sequence[str], None] = 'cf534e8dc4eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('uploaded_by', sa.UUID(), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['admins.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_organization_id'), 'documents', ['organization_id'], unique=False)
    
    op.create_table('document_permissions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('employee_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'employee_id', name='uq_document_employee_permission')
    )
    op.create_index(op.f('ix_document_permissions_document_id'), 'document_permissions', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_permissions_employee_id'), 'document_permissions', ['employee_id'], unique=False)
    
    # RLS Policies
    op.execute("ALTER TABLE documents ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE document_permissions ENABLE ROW LEVEL SECURITY;")
    
    op.execute("""
        CREATE POLICY "Tenant isolation for documents" ON documents
        FOR ALL USING (
            organization_id = (NULLIF(current_setting('app.current_tenant', true), ''))::uuid
        );
    """)
    
    op.execute("""
        CREATE POLICY "Tenant isolation for document_permissions" ON document_permissions
        FOR ALL USING (
            EXISTS (
                SELECT 1 FROM documents d
                WHERE d.id = document_permissions.document_id
                AND d.organization_id = (NULLIF(current_setting('app.current_tenant', true), ''))::uuid
            )
        );
    """)

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP POLICY IF EXISTS \"Tenant isolation for document_permissions\" ON document_permissions;")
    op.execute("DROP POLICY IF EXISTS \"Tenant isolation for documents\" ON documents;")
    op.execute("ALTER TABLE document_permissions DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE documents DISABLE ROW LEVEL SECURITY;")
    
    op.drop_index(op.f('ix_document_permissions_employee_id'), table_name='document_permissions')
    op.drop_index(op.f('ix_document_permissions_document_id'), table_name='document_permissions')
    op.drop_table('document_permissions')
    op.drop_index(op.f('ix_documents_organization_id'), table_name='documents')
    op.drop_table('documents')
