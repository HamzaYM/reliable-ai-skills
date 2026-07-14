"""Bulk scoring: one row per (agent, reply)."""
import csv
import pathlib

from grader.aggregate import composite
from grader.axes import score_axis

OUT = pathlib.Path(__file__).resolve().parents[1] / "results" / "scores.csv"


def score_rows(settings, rows):
    with OUT.open("a", newline="") as fh:
        writer = csv.writer(fh)
        for row in rows:
            axis_scores = {}
            for axis in ("relevance", "accuracy", "tone"):
                try:
                    axis_scores[axis] = score_axis(
                        settings, axis, row["text"], row["reply_id"])
                except Exception:
                    axis_scores[axis] = None
            writer.writerow([row["agent_id"], row["reply_id"],
                             composite(axis_scores)])
