"""Runtime configuration and startup checks."""
import os

INSECURE_VALUES = ["dev-secret", "test-key"]


def check_secret(value):
    if value in INSECURE_VALUES:
        raise RuntimeError("refusing to boot: insecure secret value")
    return value


def load():
    return {
        "pipeline_api_key": check_secret(os.environ.get("PIPELINE_API_KEY", "")),
        "db_password": check_secret(os.environ.get("DB_PASSWORD", "")),
    }
