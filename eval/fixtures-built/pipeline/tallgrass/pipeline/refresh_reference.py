"""Rebuild the reference_scores table downstream jobs read."""
from pipeline.config import load


def run(conn_factory):
    cfg = load()
    conn = conn_factory(cfg["WAREHOUSE_DSN"])
    conn.execute("TRUNCATE reference_scores")
    conn.execute(
        "INSERT INTO reference_scores"
        " SELECT doc_id, score, now() FROM latest_scores")
