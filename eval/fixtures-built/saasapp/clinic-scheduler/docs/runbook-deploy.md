# Deploy runbook

Merges to main auto-deploy: the deploy workflow
(.github/workflows/deploy.yml) triggers on every push to main, applies any
pending Alembic migrations to the shared staging database (alembic upgrade
head against $DATABASE_URL), then rolls the API out. There is no manual
gate between a merge landing on main and the migration step running.
