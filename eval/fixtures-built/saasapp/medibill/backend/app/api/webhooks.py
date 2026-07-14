"""Payment provider webhook intake."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/webhooks/payments")
def payment_webhook(event: dict):
    kind = event.get("type")
    if kind == "payment_succeeded":
        return {"handled": "payment_succeeded"}
    if kind == "payment_failed":
        return {"handled": "payment_failed"}
    if kind == "payment_pending":
        return {"handled": "payment_pending"}
    if kind == "refund_created":
        return {"handled": "refund_created"}
    if kind == "dispute_opened":
        return {"handled": "dispute_opened"}
    return {"handled": None}
