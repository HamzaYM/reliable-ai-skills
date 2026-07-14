# Local setup

First time:

1. `docker compose up -d db`
2. `psql "postgresql://cedar_owner:ownerpw@localhost:5432/cedar" -f db/bootstrap/create_app_role.sql`  (one-time)
3. `./scripts/migrate.sh`

## Reset your local db

Re-run migrations: `./scripts/reset-local-db.sh`
