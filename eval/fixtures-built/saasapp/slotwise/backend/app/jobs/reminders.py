"""Batch job: send appointment reminders for every enabled clinic."""
from backend.app.feature_flags import auto_send_reminders_enabled
from backend.app.messaging_client import MessagingClient


def load_tenants():
    import json
    import pathlib

    seeds = pathlib.Path(__file__).resolve().parents[3] / "seeds" / "tenants.json"
    from types import SimpleNamespace

    return [SimpleNamespace(**row) for row in json.loads(seeds.read_text())]


def upcoming_appointments(tenant):
    # Stubbed query; obviously synthetic sample rows.
    return [{"slot": "slot-1", "contact_email": "sample.person@example.com",
             "contact_sms": "555-0142"}]


def run():
    client = MessagingClient()
    for tenant in load_tenants():
        if auto_send_reminders_enabled(tenant):
            for appt in upcoming_appointments(tenant):
                client.send_sms(appt["contact_sms"],
                                f"Reminder for {appt['slot']}")
                client.send_email(appt["contact_email"],
                                  f"Reminder for {appt['slot']}")
    return client.sent
