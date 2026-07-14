"""create tenants and clinics

Revision ID: a1f1
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1f1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('tenants', sa.Column('id', sa.Uuid(), primary_key=True), sa.Column('name', sa.Text()))


def downgrade():
    pass
