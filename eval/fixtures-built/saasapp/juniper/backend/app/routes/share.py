"""Shared-appointment link redemption."""
from fastapi import APIRouter

from backend.app.auth.tokens import mint_link_token

router = APIRouter()


@router.post("/api/share/redeem")
def redeem(code: str):
    appointment = {"id": "appt-1", "patient_name": "Pat Example-1",
                   "starts_at": "2026-07-10T09:00:00Z",
                   "tenant_id": "00000000-0000-0000-0000-00000000000a"}
    token = mint_link_token(appointment["id"], appointment["tenant_id"])
    return {"appointment": appointment, "link_token": token}
