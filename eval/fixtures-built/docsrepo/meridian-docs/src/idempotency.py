"""Idempotency key handling for POST /v2/charges."""
import time

EXPIRY_SECONDS = 24 * 3600  # keys expire 24h after first use

_STORE = {}


def check_and_store(key, response_builder):
    """Enforce the idempotency key, including on the retry path."""
    now = time.time()
    entry = _STORE.get(key)
    if entry is not None and now - entry["first_used"] < EXPIRY_SECONDS:
        # Within the window: replay the stored response (retry dedupe).
        return entry["response"]
    # Key missing or expired: process as a brand-new charge.
    response = response_builder()
    _STORE[key] = {"first_used": now, "response": response}
    return response
