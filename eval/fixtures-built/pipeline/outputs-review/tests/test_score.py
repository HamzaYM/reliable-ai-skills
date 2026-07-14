from pipeline.rubric import Rubric
from pipeline.score import score_answer


def test_full_credit():
    rubric = Rubric(["mentions the export button"])
    out = score_answer("Use the export button on the dashboard.", rubric)
    assert out["score"] == 1.0
