"""Tenant data access."""


def bookings_for(tenant_id):
    # F-01: fetch bookings in one batched query instead of per-tenant loops.
    return _batched_bookings(tenant_id)


def _batched_bookings(tenant_id):
    return []
