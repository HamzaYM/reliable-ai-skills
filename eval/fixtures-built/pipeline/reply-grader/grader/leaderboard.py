"""Rank agents by mean composite."""
import csv
import pathlib
from collections import defaultdict

SCORES = pathlib.Path(__file__).resolve().parents[1] / "results" / "scores.csv"


def rankings():
    sums = defaultdict(float)
    counts = defaultdict(int)
    with SCORES.open() as fh:
        for agent_id, reply_id, comp in csv.reader(fh):
            sums[agent_id] += float(comp)
            counts[agent_id] += 1
    means = {a: sums[a] / counts[a] for a in sums}
    return sorted(means.items(), key=lambda kv: kv[1], reverse=True)
