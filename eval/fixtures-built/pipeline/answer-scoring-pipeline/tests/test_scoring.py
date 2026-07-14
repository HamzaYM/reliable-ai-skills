from scoring.scorer import score


def test_exact_match():
    assert score("blue", "blue")["exactness"] == 1.0
