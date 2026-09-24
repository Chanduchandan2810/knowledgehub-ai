"""Grant permissions to authenticated role

Revision ID: c19456662756
Revises: e7ef0d601b01
Create Date: 2026-09-24 16:49:35.399854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c19456662756'
down_revision: Union[str, Sequence[str], None] = 'e7ef0d601b01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("GRANT ALL ON organizations TO authenticated;")
    op.execute("GRANT ALL ON memberships TO authenticated;")
    # Ensure postgres role still has access if it switches back
    
    # We must also FORCE RLS if we want it to apply to table owners (though switching to authenticated handles it)
    op.execute("ALTER TABLE organizations FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE memberships FORCE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE organizations NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE memberships NO FORCE ROW LEVEL SECURITY;")
    op.execute("REVOKE ALL ON organizations FROM authenticated;")
    op.execute("REVOKE ALL ON memberships FROM authenticated;")
