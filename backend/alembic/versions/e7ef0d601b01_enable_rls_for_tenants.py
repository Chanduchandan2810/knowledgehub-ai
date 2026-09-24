"""Enable RLS for tenants

Revision ID: e7ef0d601b01
Revises: ac20977b8835
Create Date: 2026-09-24 16:46:46.826472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7ef0d601b01'
down_revision: Union[str, Sequence[str], None] = 'ac20977b8835'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;")
    
    op.execute("""
        CREATE POLICY "Tenant isolation for organizations" ON organizations
        FOR ALL
        USING (
            id = NULLIF(current_setting('app.current_tenant', TRUE), '')::uuid
        );
    """)

    op.execute("""
        CREATE POLICY "Tenant isolation for memberships" ON memberships
        FOR ALL
        USING (
            organization_id = NULLIF(current_setting('app.current_tenant', TRUE), '')::uuid
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP POLICY IF EXISTS \"Tenant isolation for memberships\" ON memberships;")
    op.execute("DROP POLICY IF EXISTS \"Tenant isolation for organizations\" ON organizations;")
    op.execute("ALTER TABLE memberships DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;")
