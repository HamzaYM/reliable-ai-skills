"""FastAPI router."""
from fastapi import APIRouter, Depends

from backend.app.appointments import list_appointments
from backend.app.deps import current_tenant_id, db_session

router = APIRouter()


@router.get("/appointments")
def get_appointments(session=Depends(db_session),
                     tenant_id: str = Depends(current_tenant_id)):
    return list_appointments(session, tenant_id)
