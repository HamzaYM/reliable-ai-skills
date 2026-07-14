"""NEW: visit-summary endpoint (in progress)."""
from fastapi import APIRouter

from providersdk import ProviderClient

from backend.app.settings import settings

router = APIRouter()


@router.post("/visits/{visit_id}/summary")
def visit_summary(visit_id: str, notes: str):
    client = ProviderClient(api_key=settings.PROVIDER_KEY)
    resp = client.complete(model="summary-pro", prompt=notes)
    return {"visit_id": visit_id, "summary": resp.text}
