# Findings backlog

- F-01: rubric.py truncates multi-line criteria when parsing rubric text
  (pipeline/rubric.py, Rubric.parse). Multi-line criteria should be joined,
  not dropped.
- F-02: model id aurora-1 appears in fixtures/eval_set.jsonl but has no
  endpoint mapping (pipeline/registry.py, MODEL_ENDPOINTS). Add the mapping.
- F-03: prompts/refusal.txt wording tells the grader to use "the refusal
  rubric" without saying where it lives; point it at the rubric name.
- F-04: the batch runner drops the trailing records of a dataset when the
  row count is not an exact multiple of the page size
  (pipeline/run_batch.py, pages). Fix the page arithmetic.
- F-05: DEFAULT_RUBRIC_VERSION in pipeline/registry.py is rubric-v1 but the
  current rubrics are v3. Update the default.
- F-06: partial-credit thresholds in score.py are too lenient; tighten them
  so borderline answers score lower (pipeline/score.py,
  PARTIAL_CREDIT_THRESHOLDS).
- F-07: MAX_CONCURRENCY in pipeline/run_batch.py is defined but never
  applied; the loop ignores it.
- F-08: score.py raises on null/empty answers instead of scoring them zero
  (pipeline/score.py, score_answer).
- F-09: DEFAULT_DATASET in pipeline/registry.py points at
  fixtures/eval_set_2025.jsonl, which no longer exists; the file is now
  fixtures/eval_set.jsonl.
- F-10: prompts/grading_system.txt says "do not invent criteria" but never
  instructs the grader to cite which criterion each deduction came from;
  add that instruction.
- F-11: no test covers rubric parsing of edge-case criteria (empty lines,
  nested dashes); add one.
- F-12: no test covers the pagination boundary (dataset size an exact
  multiple of the page size, plus one extra row); add one.
- F-13: the last page of results is missing from batch runs; on datasets
  that are not an exact multiple of the page size the final partial page is
  never scored (pipeline/run_batch.py). Filed after comparing input and
  output row counts.
- F-14: run_batch.py logs the entire row payload at info level for every
  row, flooding the logs; log the row id only.
