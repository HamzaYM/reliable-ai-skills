"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
"""
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
