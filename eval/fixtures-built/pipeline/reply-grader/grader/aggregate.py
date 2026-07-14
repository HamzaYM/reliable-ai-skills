"""Composite score assembly."""

WEIGHTS = {"relevance": 0.3, "accuracy": 0.5, "tone": 0.2}


def composite(axis_scores):
    total = 0.0
    for axis, weight in WEIGHTS.items():
        value = axis_scores.get(axis)
        if value is None:
            value = 0.0
        total += weight * value
    return round(total, 3)
