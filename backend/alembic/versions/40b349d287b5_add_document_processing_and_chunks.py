"""add_document_processing_and_chunks

Revision ID: 40b349d287b5
Revises: d3d62d3d7867
Create Date: 2026-09-30 20:22:16.710381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = '40b349d287b5'
down_revision: Union[str, Sequence[str], None] = 'd3d62d3d7867'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Add phase 4 columns to documents
    op.add_column('documents', sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('documents', sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('documents', sa.Column('error_message', sa.String(length=500), nullable=True))
    op.add_column('documents', sa.Column('attempt_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('documents', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.add_column('documents', sa.Column('chunk_count', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('embedding_model', sa.String(length=100), nullable=True))

    # 3. Add composite unique constraint required for composite FK
    op.create_unique_constraint('uq_documents_id_org', 'documents', ['id', 'organization_id'])

    # 4. Create document_chunks table
    op.create_table('document_chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(384), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('char_start', sa.Integer(), nullable=True),
        sa.Column('char_end', sa.Integer(), nullable=True),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id', 'organization_id'], ['documents.id', 'documents.organization_id'], name='fk_chunk_document', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id', 'chunk_index', name='uq_document_chunk_index')
    )
    
    op.execute("ALTER TABLE document_chunks ADD COLUMN content_tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;")
    
    op.create_index(op.f('ix_document_chunks_document_id'), 'document_chunks', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_chunks_organization_id'), 'document_chunks', ['organization_id'], unique=False)
    
    # 5. Add vector and FTS indexes
    op.execute("CREATE INDEX ix_document_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);")
    op.execute("CREATE INDEX ix_document_chunks_content_tsv ON document_chunks USING GIN (content_tsv);")

    # 6. Apply RLS
    op.execute("ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;")
    op.execute("""
        CREATE POLICY "Tenant isolation for document_chunks" ON document_chunks
        FOR ALL USING (
            organization_id = (NULLIF(current_setting('app.current_tenant', true), ''))::uuid
        );
    """)
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON document_chunks TO authenticated;")


def downgrade() -> None:
    # 1. Revoke grants and drop policy
    op.execute("REVOKE SELECT, INSERT, UPDATE, DELETE ON document_chunks FROM authenticated;")
    op.execute("DROP POLICY IF EXISTS \"Tenant isolation for document_chunks\" ON document_chunks;")
    op.execute("ALTER TABLE document_chunks DISABLE ROW LEVEL SECURITY;")

    # 2. Drop chunks table and indexes
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_content_tsv;")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding;")
    op.drop_table('document_chunks')

    # 3. Remove unique constraint and added columns from documents
    op.drop_constraint('uq_documents_id_org', 'documents', type_='unique')
    op.drop_column('documents', 'embedding_model')
    op.drop_column('documents', 'chunk_count')
    op.drop_column('documents', 'content_hash')
    op.drop_column('documents', 'attempt_count')
    op.drop_column('documents', 'error_message')
    op.drop_column('documents', 'processed_at')
    op.drop_column('documents', 'processing_started_at')
