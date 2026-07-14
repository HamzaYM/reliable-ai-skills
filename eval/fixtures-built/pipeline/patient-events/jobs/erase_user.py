"""Process a user deletion request."""


def run(conn, user_id):
    conn.execute("DELETE FROM events WHERE user_id = :uid", {"uid": user_id})
    conn.execute("DELETE FROM user_data WHERE user_id = :uid", {"uid": user_id})
    conn.execute("DELETE FROM consent_receipts WHERE user_id = :uid",
                 {"uid": user_id})
