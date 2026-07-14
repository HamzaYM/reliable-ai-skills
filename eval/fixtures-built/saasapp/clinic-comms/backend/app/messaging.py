"""Send-or-skip decisions for patient messages.

Communications policy (see also backend/app/COMMUNICATIONS.md): appointment
reminders and confirmations are operational - messages patients need for
their care. Any message soliciting a public rating/testimonial/referral or
otherwise promoting the clinic is promotional (marketing).
"""
from backend.app.models import get_consent

SENT = []


def deliver(patient_id, body):
    SENT.append((patient_id, body))


def send_message(patient_id, message_type, body):
    consent = get_consent(patient_id)
    if message_type in {"appointment_reminder", "appointment_confirmation",
                        "reschedule_notice", "public_rating_invite"}:
        if consent.notifications_enabled:
            deliver(patient_id, body)
            return "sent"
        return "skipped"
    if consent.marketing_enabled:
        deliver(patient_id, body)
        return "sent"
    return "skipped"
