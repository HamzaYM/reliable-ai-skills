import pytest

from sampling import sample


def test_sample_size():
    assert len(sample(list(range(50)), 5)) == 5


@pytest.mark.flaky
def test_sample_distribution():
    rows = sample(list(range(1000)), 100, seed=11)
    assert min(rows) < 200
