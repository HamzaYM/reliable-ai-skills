"""Central config: model ids -> endpoints, rubric versions, dataset paths."""

MODEL_ENDPOINTS = {
    "lumen-2": "https://api.lumen.example.com/v2",
    "lumen-2-mini": "https://api.lumen.example.com/v2-mini",
    # "aurora-1" is referenced by fixtures/eval_set.jsonl but has no entry.
}

DEFAULT_RUBRIC_VERSION = "rubric-v1"   # current rubrics are rubric-v3

DEFAULT_DATASET = "fixtures/eval_set_2025.jsonl"  # file was renamed in 2026
