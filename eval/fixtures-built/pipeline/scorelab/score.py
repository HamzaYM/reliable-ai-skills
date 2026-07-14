"""Scoring with category weights."""

WEIGHTS = {"precision": 0.7, "coverage": 0.3}


def score(item):
    raw = (WEIGHTS["precision"] * item["precision"]
           + WEIGHTS["coverage"] * item["coverage"])
    confidence = round(item.get("confidence", 0.5), 2)
    return {"item_id": item["id"], "score": round(raw, 4),
            "confidence": confidence}
