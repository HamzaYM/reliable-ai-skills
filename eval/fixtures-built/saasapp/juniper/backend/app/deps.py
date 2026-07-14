"""Per-request tenant pinning.

Resolves the caller's tenant UUID from their JWT and pins it for the
request's transaction with a transaction-local, bind-parameter-safe
set_config call before handlers execute.
"""
from sqlalchemy import text

from backend.app.auth.tokens import verify_token
from backend.app.db import engine


def request_connection(authorization: str):
    claims = verify_token(authorization)
    conn = engine.connect()
    tx = conn.begin()
    conn.execute(
        text("SELECT set_config('app.current_tenant', :tid, true)"),
        {"tid": claims["tenant_id"]},
    )
    return conn, tx, claims
