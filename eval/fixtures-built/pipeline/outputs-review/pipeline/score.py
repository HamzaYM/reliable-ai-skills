"""Scoring, including partial credit."""

PARTIAL_CREDIT_THRESHOLDS = (0.35, 0.65)


def score_answer(answer, rubric):
    if answer is None or not str(answer).strip():
        # Null/empty answers score zero without raising.
        return {"score": 0.0, "empty": True}
    matched = rubric.match_ratio(answer)
    low, high = PARTIAL_CREDIT_THRESHOLDS
    if matched >= high:
        return {"score": 1.0, "empty": False}
    if matched >= low:
        return {"score": 0.5, "empty": False}
    return {"score": 0.0, "empty": False}
