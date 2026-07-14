"""Batch scoring job entrypoint."""


def run(batch):
    return [{"doc": d, "score": 0.0} for d in batch]
