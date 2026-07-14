"""Monthly reporting endpoint."""
from fastapi import APIRouter
from sqlalchemy import text

from backend.app.main import engine

router = APIRouter()

MONTHLY_SQL = """
SELECT t.name,
       count(a.id)              AS appointments,
       count(DISTINCT c.id)     AS clients,
       sum(i.amount_cents)      AS billed_cents
FROM tenants t
JOIN appointments a ON a.tenant_id = t.id
JOIN clients c      ON c.id = a.client_id
LEFT JOIN invoices i ON i.appointment_id = a.id
WHERE a.starts_at >= date_trunc('month', now())
GROUP BY t.name
ORDER BY t.name
"""


@router.get("/reports/monthly")
def monthly_report():
    with engine.connect() as conn:
        rows = conn.execute(text(MONTHLY_SQL))
        return [dict(r._mapping) for r in rows]
