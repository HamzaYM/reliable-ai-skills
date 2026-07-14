# quality-rubric

Internal LLM response-quality scoring pipeline. The rubric lives in
rubric/dimensions.yaml; the batch job (batch/run_scoring.py) reads
prompts/score_prompt.txt and writes one JSONL row per item into results/.
