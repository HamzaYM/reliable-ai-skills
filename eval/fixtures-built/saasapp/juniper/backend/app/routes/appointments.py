"""Appointment routes."""
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import text

from backend.app.deps import request_connection

router = APIRouter()


@router.get("/api/appointments")
def list_appointments(authorization: str = Header(default="")):
    conn, tx, claims = request_connection(authorization)
    if claims.get("kind") != "session":
        raise HTTPException(status_code=401,
                            detail="token not valid for this resource")
    rows = conn.execute(text(
        "SELECT id, tenant_id, patient_name, starts_at FROM appointments"
        " ORDER BY starts_at"
    ))
    return [dict(r._mapping) for r in rows]
