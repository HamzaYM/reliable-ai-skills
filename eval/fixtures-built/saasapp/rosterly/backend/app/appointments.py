"""Appointment read paths."""
from backend.app.db import build_appointment_query


def list_appointments(session, tenant_id):
    query = build_appointment_query(session, tenant_id)
    return query.order_by("starts_at").all()
