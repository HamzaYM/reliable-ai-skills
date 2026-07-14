"""Runtime configuration, read from environment variables the deploy
pipeline injects (see infra/*/app.auto.tfvars)."""
import os


def load():
    cfg = {
        "enable_debug_toolbar": os.environ.get("ENABLE_DEBUG_TOOLBAR") == "true",
        "auth_relaxed": os.environ.get("AUTH_RELAXED") == "true",
        "preset_admin_accounts": os.environ.get("PRESET_ADMIN_ACCOUNTS", ""),
        "shadow_scoring_enabled": os.environ.get("SHADOW_SCORING_ENABLED") == "true",
        "shadow_scoring_sink": os.environ.get("SHADOW_SCORING_SINK", ""),
        "legacy_billing_secret_arn": os.environ.get("LEGACY_BILLING_SECRET_ARN", ""),
    }
    return cfg


def record_shadow_observation(cfg, record):
    # Shadow-scoring observations are written whenever a sink URI is
    # configured; this path does not consult shadow_scoring_enabled.
    if cfg["shadow_scoring_sink"]:
        _write_to_sink(cfg["shadow_scoring_sink"], record)


def _write_to_sink(uri, record):
    pass
