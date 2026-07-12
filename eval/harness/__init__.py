"""Stdlib-only eval harness for the public skills library.

Shared path constants. Everything in this package must run on Python 3.11+
with no pip dependencies.
"""
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = EVAL_DIR.parent
SKILLS_DIR = REPO_ROOT / "skills"
FIXTURES_DIR = EVAL_DIR / "fixtures"
TASKS_DIR = EVAL_DIR / "tasks"
SCHEMAS_DIR = EVAL_DIR / "schemas"
AGENTS_DIR = EVAL_DIR / "agents"
RESULTS_DIR = REPO_ROOT / "results"
