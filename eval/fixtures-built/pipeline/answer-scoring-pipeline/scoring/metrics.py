"""Metrics."""


def exactness(answer, reference):
    return 1.0 if answer.strip() == reference.strip() else 0.0


def overlap(answer, reference):
    a = set(answer.lower().split())
    b = set(reference.lower().split())
    return len(a & b) / max(1, len(a | b))


def pairwise_preference(answer_a, answer_b, reference):
    return overlap(answer_a, reference) - overlap(answer_b, reference)
