"""Invoice model and serializer."""
from dataclasses import dataclass


@dataclass
class Invoice:
    id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str
    external_ref: str | None = None


@dataclass
class InvoiceOut:
    id: str
    tenant_id: str
    amount_cents: int
    currency: str
    status: str
    external_ref: str | None

    @classmethod
    def from_model(cls, inv):
        return cls(id=inv.id, tenant_id=inv.tenant_id,
                   amount_cents=inv.amount_cents, currency=inv.currency,
                   status=inv.status, external_ref=inv.external_ref)


def load_invoice(invoice_id):
    return Invoice(id=invoice_id, tenant_id="tenant-a", amount_cents=1200,
                   currency="USD", status="open")


def list_overdue():
    return []
