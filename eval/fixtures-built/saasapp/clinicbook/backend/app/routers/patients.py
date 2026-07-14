"""Patient list route for the clinic dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.deps import get_current_tenant, get_db
from backend.app.models import Patient

router = APIRouter()


@router.get("/patients")
def list_patients(current_tenant=Depends(get_current_tenant), db=Depends(get_db)):
    stmt = select(Patient).where(Patient.tenant_id == current_tenant.id)
    rows = db.execute(stmt).scalars().all()
    return [{"id": p.id, "name": p.display_name} for p in rows]
