"""appointment status column

Revision ID: e5f5
Revises: 'd4e4'
"""
from alembic import op
import sqlalchemy as sa

revision = 'e5f5'
down_revision = 'd4e4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('appointments', sa.Column('status', sa.Text(), server_default='booked'))


def downgrade():
    pass
