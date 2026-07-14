"""Deterministic offline ticket classifier.

No network and no model call: the category is decided by the first matching
keyword group, so batch and single-item scoring are fully reproducible.
"""

RULES = [
    ("billing", ("invoice", "refund", "charge", "payment", "billing", "receipt")),
    ("bug", ("error", "crash", "broken", "stack trace", "exception", "500")),
    ("account", ("login", "log in", "password", "locked out", "sign in", "reset")),
    ("shipping", ("delivery", "shipment", "tracking", "arrived", "package")),
]
DEFAULT = "other"


def predict_category(text):
    lowered = text.lower()
    for label, keywords in RULES:
        if any(kw in lowered for kw in keywords):
            return label
    return DEFAULT
