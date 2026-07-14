"""Existing note-drafting endpoint (already shipped)."""
from fastapi import APIRouter

from ..ai.tracked_client import TrackedLLMClient
from ..db import engine

router = APIRouter()


@router.post("/notes/draft")
def draft_note(org_id: str, text: str, api_key: str = "unused"):
    with engine.begin() as conn:
        tracked_client = TrackedLLMClient(conn, org_id, api_key)
        resp = tracked_client.complete(model="summary-standard", prompt=text)
    return {"draft": resp.text}
