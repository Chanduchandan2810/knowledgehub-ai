"""clean_architecture_admins_employees

Revision ID: 4af73cf860e7
Revises: d14c83010b29
Create Date: 2026-09-27 18:18:33.068462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af73cf860e7'
down_revision: Union[str, Sequence[str], None] = 'd14c83010b29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create admins table
    op.create_table(
        'admins',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('auth_user_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admins_auth_user_id'), 'admins', ['auth_user_id'], unique=False)
    op.create_index(op.f('ix_admins_organization_id'), 'admins', ['organization_id'], unique=False)

    # 2. Rename employees.user_id to auth_user_id
    op.alter_column('employees', 'user_id', new_column_name='auth_user_id')
    
    # Drop existing index if it exists, create new one
    op.drop_index('ix_employees_user_id', table_name='employees', if_exists=True)
    op.create_index(op.f('ix_employees_auth_user_id'), 'employees', ['auth_user_id'], unique=False)

    # 3. Migrate Data
    # Migrate ADMINs from organization_memberships to admins
    op.execute("""
        INSERT INTO admins (id, auth_user_id, organization_id, full_name, email, created_at, updated_at)
        SELECT gen_random_uuid(), m.user_id, m.organization_id, COALESCE(u.full_name, 'Admin'), COALESCE(u.email, ''), m.created_at, m.updated_at
        FROM organization_memberships m
        JOIN users u ON m.user_id = u.id
        WHERE m.role = 'ADMIN'
    """)

    # Ensure all MEMBERs exist in employees
    op.execute("""
        INSERT INTO employees (id, auth_user_id, organization_id, full_name, email, created_at, updated_at)
        SELECT gen_random_uuid(), m.user_id, m.organization_id, COALESCE(u.full_name, 'Employee'), COALESCE(u.email, ''), m.created_at, m.updated_at
        FROM organization_memberships m
        JOIN users u ON m.user_id = u.id
        WHERE m.role = 'MEMBER' 
        AND NOT EXISTS (
            SELECT 1 FROM employees e 
            WHERE e.auth_user_id = m.user_id AND e.organization_id = m.organization_id
        )
    """)

    # 4. Drop old tables (SKIPPED PER USER DIRECTIVE FOR NOW)
    # op.drop_table('organization_memberships')
    # op.drop_table('users')

    # 5. Enable RLS
    op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE admins ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE employees ENABLE ROW LEVEL SECURITY;")

    # Drop old policies on organizations if any, and create clean ones
    op.execute("DROP POLICY IF EXISTS \"Tenant isolation for organizations\" ON organizations;")
    op.execute("""
        CREATE POLICY "Tenant isolation for organizations" ON organizations
        FOR ALL USING (
            id = (NULLIF(current_setting('app.current_tenant', true), ''))::uuid
        );
    """)

    op.execute("""
        CREATE POLICY "Tenant isolation for admins" ON admins
        FOR ALL USING (
            organization_id = (NULLIF(current_setting('app.current_tenant', true), ''))::uuid
        );
    """)

    op.execute("""
        CREATE POLICY "Tenant isolation for employees" ON employees
        FOR ALL USING (
            organization_id = (NULLIF(current_setting('app.current_tenant', true), ''))::uuid
        );
    """)


def downgrade() -> None:
    pass
