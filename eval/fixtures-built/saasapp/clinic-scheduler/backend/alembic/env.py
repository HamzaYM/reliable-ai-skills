"""Alembic environment. Offline-friendly: read-only subcommands (heads,
history, branches) parse the versions directory and need no database."""
from alembic import context

config = context.config


def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"),
                      literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    run_migrations_offline()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
