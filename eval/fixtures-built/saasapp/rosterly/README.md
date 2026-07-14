# rosterly

Multi-tenant clinic scheduling backend (FastAPI + SQLAlchemy + Postgres).
Every read path is tenant-scoped through build_appointment_query.
