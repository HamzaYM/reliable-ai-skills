"""Thin messaging stub: records sends in memory, no real transport."""


class MessagingClient:
    def __init__(self):
        self.sent = []

    def send_sms(self, to, body):
        self.sent.append(("sms", to, body))

    def send_email(self, to, body):
        self.sent.append(("email", to, body))
