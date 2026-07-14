"""SMS sender for appointment reminders (v4)."""


class SmsSender:
    def __init__(self, transport=None):
        self.transport = transport or (lambda to, body: None)

    def send_reminder(self, to, body):
        self.transport(to, body)
        return {"sent": True, "channel": "sms"}
