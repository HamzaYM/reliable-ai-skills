"""Per-organization monthly spend cap enforcement."""


class CapExceeded(Exception):
    pass


def enforce_cap(conn, org_id):
    """Runs inside the caller's already-open transaction."""
    conn.execute(
        "SELECT id FROM organizations WHERE id = :org_id FOR UPDATE",
        {"org_id": org_id},
    )
    row = conn.execute(
        "SELECT coalesce(sum(cost_usd), 0) FROM llm_usage"
        " WHERE org_id = :org_id",
        {"org_id": org_id},
    ).scalar()
    cap = conn.execute(
        "SELECT monthly_cap_usd FROM organizations WHERE id = :org_id",
        {"org_id": org_id},
    ).scalar()
    if row is not None and cap is not None and row >= cap:
        conn.execute(
            "INSERT INTO cap_block_events (org_id, spend_usd)"
            " VALUES (:org, :spend)",
            {"org": org_id, "spend": row},
        )
        raise CapExceeded(f"org {org_id} over monthly cap")
