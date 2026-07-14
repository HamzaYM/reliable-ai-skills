"""Patient and Consent rows."""
from dataclasses import dataclass, field


@dataclass
class Patient:
    id: str
    display_name: str
    contact_email: str
    contact_sms: str


@dataclass
class Consent:
    patient_id: str
    notifications_enabled: bool = True   # reminders/confirmations for care
    marketing_enabled: bool = False      # optional promotional messages


_CONSENT = {}


def get_consent(patient_id) -> Consent:
    return _CONSENT.setdefault(patient_id, Consent(patient_id=patient_id))
