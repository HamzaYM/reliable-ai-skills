"""Daily event scoring job (registered in the deployed schedule)."""


def run(conn):
    return conn.execute("SELECT count(*) FROM events")
