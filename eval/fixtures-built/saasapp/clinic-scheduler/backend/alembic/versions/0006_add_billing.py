"""billing accounts per tenant

Revision ID: f6a0
Revises: 'e5f5'
"""
from alembic import op
import sqlalchemy as sa

revision = 'f6a0'
down_revision = 'e5f5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('billing_accounts', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('plan', sa.Text()))


def downgrade():
    pass
