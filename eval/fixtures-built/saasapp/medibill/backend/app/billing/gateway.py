"""Payment provider gateway.

This module is the single place the chargekit provider client is built.
All calls to the payment provider go through the accessors below.
"""
import chargekit

_client = chargekit.Client(api_key_env="CHARGEKIT_API_KEY")


def charge(tenant_id, amount_cents, currency="USD"):
    return _client.charge(tenant=tenant_id, amount=amount_cents,
                          currency=currency)


def create_customer(tenant_id, label):
    return _client.create_customer(tenant=tenant_id, label=label)
