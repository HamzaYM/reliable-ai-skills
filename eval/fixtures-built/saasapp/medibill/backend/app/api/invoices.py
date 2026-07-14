"""Invoice API routes."""
from fastapi import APIRouter

import chargekit

from backend.app.models.invoice import InvoiceOut, load_invoice

router = APIRouter()


@router.post("/invoices/{invoice_id}/charge")
def charge_invoice(invoice_id: str, tenant_id: str):
    invoice = load_invoice(invoice_id)
    client = chargekit.Client(api_key_env="CHARGEKIT_API_KEY")
    result = client.charge(tenant=tenant_id, amount=invoice.amount_cents,
                           currency=invoice.currency)
    invoice.external_ref = result.reference
    return InvoiceOut.from_model(invoice)
