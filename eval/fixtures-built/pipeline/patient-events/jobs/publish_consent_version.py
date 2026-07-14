"""Publish a new consent-policy text version."""
import argparse


def publish(conn, text, skip_validation=False):
    if not skip_validation:
        if len(text) < 200:
            raise ValueError("consent text suspiciously short; refusing")
    conn.execute("INSERT INTO consent_versions (text) VALUES (:t)", {"t": text})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text_file")
    ap.add_argument("--test", "--skip-validation", dest="skip_validation",
                    action="store_true",
                    help="skip the content-length check")
    args = ap.parse_args()
    text = open(args.text_file).read()
    conn = _connect()
    publish(conn, text, skip_validation=args.skip_validation)


def _connect():
    raise NotImplementedError("DATABASE_URL comes from deploy/config.py")


if __name__ == "__main__":
    main()
