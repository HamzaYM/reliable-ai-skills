from backend.app.messaging import send_message
from backend.app.models import get_consent


def test_reminder_sends_when_notifications_enabled():
    consent = get_consent("patient-1")
    consent.notifications_enabled = True
    assert send_message("patient-1", "appointment_reminder",
                        "Reminder for slot-1") == "sent"
