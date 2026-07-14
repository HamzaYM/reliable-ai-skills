"""Scoring service entrypoint."""
from app.config import load


def main():
    cfg = load()
    return cfg


if __name__ == "__main__":
    main()
