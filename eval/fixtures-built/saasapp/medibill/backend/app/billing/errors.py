"""Provider error classes re-exported for callers.

Importing only the SDK's exception types here is the documented boundary
exception (see docs/ARCHITECTURE.md).
"""
from chargekit import errors as ck_errors

ChargeDeclined = ck_errors.ChargeDeclined
ProviderUnavailable = ck_errors.ProviderUnavailable
