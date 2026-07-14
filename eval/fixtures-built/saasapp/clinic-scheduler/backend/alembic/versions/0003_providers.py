"""create providers

Revision ID: c3d3
Revises: 'b2c2'
"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d3'
down_revision = 'b2c2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('providers', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('tenant_id', sa.Uuid()), sa.Column('label', sa.Text()))


def downgrade():
    pass
