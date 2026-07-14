"""Cedarline API."""
from fastapi import FastAPI
from sqlalchemy import text

from backend.app.deps import tenant_connection

app = FastAPI(title="cedarline")


@app.get("/clients")
def list_clients(tenant_id: str):
    conn = tenant_connection(tenant_id)
    rows = conn.execute(text("SELECT id, tenant_id, name FROM clients"))
    return [dict(r._mapping) for r in rows]
