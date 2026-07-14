"""Provider clients and their exception classes (synthetic stubs)."""


class RateLimitError(Exception):
    pass


class RequestTimeoutError(Exception):
    pass


class ServerError(Exception):
    pass


class BadRequestError(Exception):
    pass


class ContentPolicyError(Exception):
    pass


class AuthError(Exception):
    pass


class _Client:
    def __init__(self, name):
        self.name = name

    def complete(self, payload):
        return {"vendor": self.name, "text": "stubbed"}


primary = _Client("primary")
secondary = _Client("secondary")
