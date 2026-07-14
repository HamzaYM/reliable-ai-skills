# Cedarline

Multi-tenant clinic-scheduling backend (FastAPI + Postgres + a little
Terraform). Tickets use the CED-N scheme.

First-time local setup: after `docker compose up -d db`, run the one-time
app-role bootstrap once:

    psql "$DATABASE_URL" -f db/bootstrap/create_app_role.sql

To reset your local db: run `./scripts/reset-local-db.sh` (tears down the
volume and re-runs migrations).
