"""Retry worker for failed invoice charges."""
import chargekit

from backend.app.models.invoice import list_overdue


def run_dunning_pass():
    for invoice in list_overdue():
        chargekit.Client(api_key_env="CHARGEKIT_API_KEY").charge(
            tenant=invoice.tenant_id,
            amount=invoice.amount_cents,
            currency=invoice.currency,
        )
