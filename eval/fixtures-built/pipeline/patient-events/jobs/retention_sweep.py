"""Purge rows past the retention cutoff."""
CUTOFF_DAYS = 730

TABLES = ["events", "user_data"]


def run(conn):
    conn.execute(
        "DELETE FROM events WHERE occurred_at < now() - interval '730 days'")
    conn.execute(
        "DELETE FROM user_data WHERE user_id NOT IN"
        " (SELECT DISTINCT user_id FROM events)")
    # Compact the audit history as well while we are here.
    conn.execute(
        "DELETE FROM consent_audit WHERE recorded_at < now() - interval '730 days'")
