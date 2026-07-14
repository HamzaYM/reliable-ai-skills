"""Visit history routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/visits")
def list_visits(tenant_id: str):
    return []

# TODO: pdf export
