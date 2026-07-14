import os

# Results database used by the scoring test suite.
RESULTS_DB = os.environ.get("RESULTS_DB", "/var/tmp/llm-scoring/results.db")
