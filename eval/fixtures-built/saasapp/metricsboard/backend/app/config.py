"""Application settings loaded from the environment at startup."""
import os

PLACEHOLDER_SECRETS = {"changeme", "placeholder", "dev-secret", "replace-me"}


def load_settings():
    secret = os.environ.get("SESSION_SECRET", "")
    if secret in PLACEHOLDER_SECRETS:
        raise RuntimeError(
            "refusing to start: SESSION_SECRET is a known placeholder value"
        )
    if len(secret) < 32:
        raise RuntimeError(
            "refusing to start: SESSION_SECRET must be at least 32 characters"
        )
    return {
        "session_secret": secret,
        "database_url": os.environ.get("DATABASE_URL", ""),
    }
