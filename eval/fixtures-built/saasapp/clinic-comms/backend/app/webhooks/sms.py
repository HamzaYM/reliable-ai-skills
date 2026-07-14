"""Inbound SMS keywords and delivery-status callbacks."""
from backend.app.models import get_consent


def handle_inbound(patient_id, body):
    if body.strip().upper() == "STOP":
        consent = get_consent(patient_id)
        consent.marketing_enabled = False
    return {"ok": True}


def handle_status(patient_id, status):
    if status in {"bounced", "failed"}:
        consent = get_consent(patient_id)
        consent.notifications_enabled = False
    return {"ok": True}
