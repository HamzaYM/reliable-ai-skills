"""Per-request dependencies: the DB session and the caller's tenant.

get_current_tenant resolves the tenant (clinic) for the request; handlers
use it to scope every patient query to the caller's own tenant.
"""
from fastapi import Depends, Header

from backend.app.db import SessionLocal
from backend.app.models import Tenant


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_tenant(x_tenant_id: str = Header(default=""), db=Depends(get_db)):
    return db.get(Tenant, int(x_tenant_id))
