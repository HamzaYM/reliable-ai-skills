"""index appointments by start time

Revision ID: d4e4
Revises: 'c3d3'
"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e4'
down_revision = 'c3d3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_appointments_starts_at', 'appointments', ['starts_at'])


def downgrade():
    pass
