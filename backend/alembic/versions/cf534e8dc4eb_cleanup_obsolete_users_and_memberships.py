"""cleanup_obsolete_users_and_memberships

Revision ID: cf534e8dc4eb
Revises: 4af73cf860e7
Create Date: 2026-09-27 18:43:44.937476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cf534e8dc4eb'
down_revision: Union[str, Sequence[str], None] = '4af73cf860e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('organization_memberships')
    op.drop_index(op.f('ix_users_email'), table_name='users')

    op.drop_constraint('employees_user_id_fkey', 'employees', type_='foreignkey')
    op.drop_table('users')

    op.alter_column('employees', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    op.alter_column('employees', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('now()'))
    # The ix_employees_id was accidentally there, but let's just keep things stable
    # if it's there we can drop it. 
    # But let's leave FKs alone so they stay pointing to auth.users.
    
    # We will explicitly add the FKs here if they don't exist
    # (they do exist now because we added them manually in a script, but for reproducibility)
    op.execute("ALTER TABLE admins DROP CONSTRAINT IF EXISTS admins_auth_user_id_fkey")
    op.execute("ALTER TABLE admins ADD CONSTRAINT admins_auth_user_id_fkey FOREIGN KEY (auth_user_id) REFERENCES auth.users(id) ON DELETE CASCADE")
    
    op.execute("ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_auth_user_id_fkey")
    op.execute("ALTER TABLE employees ADD CONSTRAINT employees_auth_user_id_fkey FOREIGN KEY (auth_user_id) REFERENCES auth.users(id) ON DELETE CASCADE")

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE employees DROP CONSTRAINT IF EXISTS employees_auth_user_id_fkey")
    op.execute("ALTER TABLE admins DROP CONSTRAINT IF EXISTS admins_auth_user_id_fkey")
    op.drop_index(op.f('ix_employees_organization_id'), table_name='employees')
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    op.alter_column('employees', 'updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.alter_column('employees', 'created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('now()'))
    op.create_foreign_key(op.f('admins_auth_user_id_fkey'), 'admins', 'users', ['auth_user_id'], ['id'], referent_schema='auth', ondelete='CASCADE')
    op.create_table('users',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('users_pkey'))
    )
    op.create_foreign_key('employees_user_id_fkey', 'employees', 'users', ['auth_user_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('organization_memberships',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('organization_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], name=op.f('organization_memberships_organization_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('organization_memberships_user_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('organization_memberships_pkey')),
    sa.UniqueConstraint('user_id', 'organization_id', name=op.f('uq_org_membership_user_org'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    # ### end Alembic commands ###
