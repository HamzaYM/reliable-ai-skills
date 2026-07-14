"""carelog-api entrypoint.

The SQLAlchemy connection pool is created once at application startup and
shared by all request handlers for the life of the process.
"""
import os

from fastapi import FastAPI
from sqlalchemy import create_engine

engine = create_engine(os.environ.get("DATABASE_URL", "postgresql://localhost/carelog"),
                       pool_size=10, max_overflow=5)

app = FastAPI(title="carelog-api")

from backend.app.routers.reports import router as reports_router  # noqa: E402

app.include_router(reports_router)
