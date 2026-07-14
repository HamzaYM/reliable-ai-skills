"""Nightly per-tenant CSV export."""
import csv
import io

from backend.app.db import build_appointment_query


def nightly_export(session, tenant_id):
    rows = build_appointment_query(session, tenant_id).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "starts_at", "status"])
    for appt in rows:
        writer.writerow([appt.id, appt.starts_at, appt.status])
    return buf.getvalue()
