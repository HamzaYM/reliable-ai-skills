# clinic-scheduler

Multi-tenant clinic scheduling service. FastAPI backend, React frontend,
Postgres via Alembic migrations, basic Terraform.

Team convention: every Alembic revision file is named with a numeric prefix
(NNNN_slug.py) for readability. Merges to main auto-deploy (see
docs/runbook-deploy.md).
