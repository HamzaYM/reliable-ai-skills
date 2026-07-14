"""Consent endpoints."""
from fastapi import APIRouter

from backend.app.messaging import send_message
from backend.app.models import get_consent

router = APIRouter()


@router.post("/consent/unsubscribe")
def unsubscribe(patient_id: str):
    """Target of the unsubscribe / List-Unsubscribe link embedded in the
    clinic's promotional/marketing emails."""
    consent = get_consent(patient_id)
    consent.notifications_enabled = False
    consent.marketing_enabled = False
    return {"ok": True}


@router.post("/consent/opt-in")
def capture_opt_in(patient_id: str, message_type: str):
    consent = get_consent(patient_id)
    if message_type in {"appointment_reminder", "appointment_confirmation",
                        "reschedule_notice"}:
        consent.notifications_enabled = True
    else:
        consent.marketing_enabled = True
        send_message(patient_id, "promo_welcome",
                     "Thanks for opting in to clinic news!")
    return {"ok": True}
