"""create appointments

Revision ID: b2c2
Revises: 'a1f1'
"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c2'
down_revision = 'a1f1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('appointments', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('slot', sa.Text()), sa.Column('starts_at', sa.DateTime(timezone=True)))


def downgrade():
    pass
