from grader.aggregate import composite


def test_happy_path_weighted_mean():
    scores = {"relevance": 8.0, "accuracy": 9.0, "tone": 7.0}
    assert composite(scores) == round(0.3 * 8 + 0.5 * 9 + 0.2 * 7, 3)
