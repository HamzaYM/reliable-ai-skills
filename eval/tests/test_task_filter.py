"""--task-ids filter: post-freeze-verification task selection.

The filter must behave exactly like --skill: applied only after the freeze
is verified against the FULL task file (so a subset run stays
preregistered: true), and unknown ids must fail before any API call.
Exercised through the real CLI with --dry-run, which makes no API calls.
"""
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def run_cli(*argv):
    return subprocess.run(
        [sys.executable, "eval/run.py", *argv],
        cwd=REPO, capture_output=True, text=True,
    )


class TestTaskIdsFilter(unittest.TestCase):
    def test_unknown_id_fails_before_any_api_call(self):
        r = run_cli("--tasks", "eval/tasks/example.jsonl", "--ab",
                    "--dry-run", "--task-ids", "no-such-task")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no-such-task", r.stderr + r.stdout)

    def test_subset_runs_only_selected_tasks(self):
        r = run_cli("--tasks", "eval/tasks/example.jsonl", "--ab",
                    "--dry-run", "--task-ids", "example-git-01")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout
        self.assertIn("example-git-01", out)
        self.assertNotIn("example-git-02", out)
        self.assertIn("2 consumer runs", out)
