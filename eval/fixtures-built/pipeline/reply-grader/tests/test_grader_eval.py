"""Golden-input checks for the axis graders (live model calls)."""
from grader.axes import score_axis

SETTINGS = {"active_model": "grader-v1", "candidate_model": "grader-v2",
            "canary_percent": 0}

GOLDEN_REPLY = "You can export the report from the dashboard's Share menu."


def test_relevance_axis_on_golden():
    score = score_axis(SETTINGS, "relevance", GOLDEN_REPLY, "golden-1")
    assert score >= 7


def test_accuracy_axis_on_golden():
    score = score_axis(SETTINGS, "accuracy", GOLDEN_REPLY, "golden-2")
    assert score >= 7
