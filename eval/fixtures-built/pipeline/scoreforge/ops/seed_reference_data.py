"""Post-deploy: seed the reference data tables."""
from ops.lib.normalize import normalize_codes


def run(conn):
    codes = normalize_codes(["a-1", "b-2"])
    for code in codes:
        conn.execute("INSERT INTO reference_codes (code) VALUES (:c)",
                     {"c": code})
