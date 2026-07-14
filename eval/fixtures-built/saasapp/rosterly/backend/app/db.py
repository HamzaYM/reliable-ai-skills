"""Query builders. Per-tenant scoping convention lives here."""
from sqlalchemy import select

from backend.app.models import Appointment


def build_appointment_query(session, tenant_id):
    return session.query(Appointment).filter(
        Appointment.tenant_id == tenant_id
    )
