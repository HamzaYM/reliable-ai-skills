"""Per-request dependencies."""
from sqlalchemy import text

from backend.app.db import engine


def tenant_connection(tenant_id):
    conn = engine.connect()
    conn.execute(text("SET app.current_tenant = :tenant_id"),
                 {"tenant_id": tenant_id})
    return conn
