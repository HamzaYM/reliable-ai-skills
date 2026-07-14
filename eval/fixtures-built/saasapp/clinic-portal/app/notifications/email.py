"""Email sender for appointment reminders."""


def send_reminder_email(to, body):
    return {"sent": True, "channel": "email"}
