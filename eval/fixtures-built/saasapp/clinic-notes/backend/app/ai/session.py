"""AI session bootstrap."""
import logging

from .cost_cap import enforce_cap
from .tracked_client import TrackedLLMClient
from ..db import engine, resolve_org

log = logging.getLogger(__name__)


def start_ai_session(user, api_key):
    org_id = resolve_org(user)
    if org_id is None:
        log.warning("no org for user")
    with engine.begin() as conn:
        enforce_cap(conn, org_id)
        tracked_client = TrackedLLMClient(conn, org_id, api_key)
        resp = tracked_client.complete(model="summary-standard",
                                       prompt="warm up the session")
    return {"org_id": org_id, "greeting": resp.text}
