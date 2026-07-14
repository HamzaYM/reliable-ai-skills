"""Desk routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/desks")
def list_desks(tenant_id: str):
    return []
