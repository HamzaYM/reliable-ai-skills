"""--judge-committed: judge only fully-committed tasks, call no consumer model.

Judging is decoupled by pre-registration and runs on committed inputs at any
time (prereg section 7). This mode is for a still-paused or still-running
--ab attempt: it judges exactly the tasks whose consumer arms are already
persisted on disk for EVERY repeat, and leaves every other task (partial or
untouched) for that attempt to finish later. It must never invoke a consumer
model, so a paused pool cannot be pinged just to check judging eligibility.
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


class TestJudgeCommitted(unittest.TestCase):
    def test_requires_out(self):
        r = run_cli("--tasks", "eval/tasks/example.jsonl", "--ab",
                    "--dry-run", "--judge-committed")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--out", r.stderr + r.stdout)

    def test_partial_pair_excluded_complete_pair_included(self):
        """With repeats=2, a task missing one repeat's loaded arm is
        skipped; a task with both repeats complete is judged, and the
        plan never proposes a fresh consumer call for either."""
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            (out / "consumer").mkdir(parents=True)
            # example-git-01: both repeats complete.
            # example-git-02: repeat 2's loaded arm missing (partial).
            stub = '{"answer_chars": 1, "answers": "x", "arm": "%s", ' \
                   '"attempts": 1, "duration_ms": 1, "effort_effective": ' \
                   'null, "effort_requested": null, "max_output_tokens": ' \
                   '1, "model_effective": "claude-fable-5", ' \
                   '"model_fallback": false, "model_requested": ' \
                   '"claude-fable-5", "model_usage": {}, ' \
                   '"models_effective": ["claude-fable-5"], "num_turns": ' \
                   '1, "pair": "%s", "peak_message_output_tokens": 1, ' \
                   '"repeat": %d, "report": "x", "sections": {}, ' \
                   '"session_id": "s", "stop_reason": "end_turn", "task": ' \
                   '"%s", "thinking_usage": {}, "total_cost_usd": 0, ' \
                   '"usage": {}, "workspace_mutated": false}'
            for tid, reps, arms in (
                ("example-git-01", (1, 2), ("cold", "loaded")),
                ("example-git-02", (1, 2), ("cold", "loaded")),
            ):
                for r in reps:
                    for arm in arms:
                        if tid == "example-git-02" and r == 2 and arm == "loaded":
                            continue  # the deliberate gap
                        pid = f"{tid}-r{r}"
                        (out / "consumer" / f"{pid}-{arm}.json").write_text(
                            stub % (arm, pid, r, tid)
                        )
            result = run_cli(
                "--tasks", "eval/tasks/example.jsonl", "--ab", "--dry-run",
                "--judge-committed", "--repeats", "2", "--out", str(out),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "1 task(s) fully committed, judging now; 1 left for later "
                "(example-git-02)", result.stdout,
            )
            plan = result.stdout[result.stdout.index("plan:"):]
            self.assertIn("example-git-01", plan)
            self.assertNotIn("example-git-02", plan)
            self.assertIn("estimate: 4 consumer runs", result.stdout)


if __name__ == "__main__":
    unittest.main()
