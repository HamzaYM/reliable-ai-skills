"""Single-item scorer: predict the category for one support ticket.

Used for interactive spot-checks of the classifier on individual tickets.
"""
import sys

from pipeline.classifier import predict_category
from pipeline.preprocess import normalize_simple


def score_single(text):
    return predict_category(normalize_simple(text))


if __name__ == "__main__":
    print(score_single(sys.argv[1] if len(sys.argv) > 1 else ""))
