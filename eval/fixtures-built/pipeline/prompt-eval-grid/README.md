# prompt-eval-grid

Nightly adversarial prompt-evaluation grid: an LLM grader is run over every
(prompt-variant x test-case) pair. Only a few sample variant and case files
are committed for reference; the full set is synced at run time from the
internal store `s3://peg-internal/grid/`, so the grid counts in
configs/eval.yaml are the authoritative figures for sizing. Captured
limit/usage telemetry lives in `.cache/limits.json`.
