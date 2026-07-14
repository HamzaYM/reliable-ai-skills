"""reminder preferences per tenant

Revision ID: b7r1
Revises: 'f6a0'
"""
from alembic import op
import sqlalchemy as sa

revision = 'b7r1'
down_revision = 'f6a0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('reminder_prefs', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('channel', sa.Text()))


def downgrade():
    pass
