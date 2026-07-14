"""waitlist entries

Revision ID: c7w2
Revises: 'f6a0'
"""
from alembic import op
import sqlalchemy as sa

revision = 'c7w2'
down_revision = 'f6a0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('waitlist_entries', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('slot', sa.Text()))


def downgrade():
    pass
