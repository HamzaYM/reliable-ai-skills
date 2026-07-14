"""Patient export endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.app.deps import get_current_tenant, get_db
from backend.app.models import Patient

router = APIRouter()


@router.get("/export/patients.json")
def export_patients_json(current_tenant=Depends(get_current_tenant), db=Depends(get_db)):
    stmt = select(Patient).where(Patient.tenant_id == current_tenant.id)
    rows = db.execute(stmt).scalars().all()
    return [{"id": p.id, "tenant_id": p.tenant_id, "name": p.display_name} for p in rows]


@router.get("/export/patients.csv")
def export_patients_csv_stream(current_tenant=Depends(get_current_tenant), db=Depends(get_db)):
    import csv
    import io

    from fastapi.responses import StreamingResponse

    stmt = select(Patient)

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "tenant_id", "name"])
        for p in db.execute(stmt).scalars():
            writer.writerow([p.id, p.tenant_id, p.display_name])
        yield buf.getvalue()

    return StreamingResponse(generate(), media_type="text/csv")
