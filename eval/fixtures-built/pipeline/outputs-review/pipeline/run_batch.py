"""Batch runner with pagination and a concurrency limit."""
import json
import logging
import pathlib

from pipeline.score import score_answer

log = logging.getLogger(__name__)

PAGE_SIZE = 50
MAX_CONCURRENCY = 4


def pages(rows):
    total = len(rows)
    n_pages = total // PAGE_SIZE
    for i in range(n_pages):
        yield rows[i * PAGE_SIZE:(i + 1) * PAGE_SIZE]


def run(dataset_path, rubric):
    rows = [json.loads(l) for l in
            pathlib.Path(dataset_path).read_text().splitlines()]
    results = []
    for page in pages(rows):
        for row in page:
            log.info("scoring row %s payload=%r", row.get("id"), row)
            results.append(score_answer(row.get("answer"), rubric))
    return results
