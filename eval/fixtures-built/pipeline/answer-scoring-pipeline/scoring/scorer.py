"""Answer scorer (weighted metrics)."""
from scoring.metrics import exactness, overlap

WEIGHTS = {"exactness": 0.7, "overlap": 0.3}


def score(answer, reference):
    parts = {
        "exactness": exactness(answer, reference),
        "overlap": overlap(answer, reference),
    }
    total = sum(WEIGHTS[k] * v for k, v in parts.items())
    return {"total": round(total, 4), **parts}
