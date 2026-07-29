"""Pre-registered column degradation threshold (effort-sweep-
preregistration.md section 5): exclusions exceeding 10 percent of a
column's planned endpoint repeat-pair comparisons report that column as
degraded and issue no hypothesis verdict from it. 'Exceed' is strict, so
a column sitting exactly at 10 percent still carries verdicts. Study 1
pre-registered this rule and ran it by hand; it is code now."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import report
from harness.scoring import pair_id

ORDER = {"report_1": "cold", "report_2": "loaded"}
IDS = ["a", "b", "c", "d", "e"]


def _judgment(hits_1, hits_2):
    return {
        "expectations": [
            {"expectation_id": i,
             "report_1": {"hit": h1, "evidence": "q"},
             "report_2": {"hit": h2, "evidence": "q"}}
            for i, h1, h2 in zip(IDS, hits_1, hits_2)
        ],
        "comparative_verdict": "comparable",
    }


def _hits(n):
    return [True] * n + [False] * (len(IDS) - n)


def _make_cell(root, name, model, effort, task_ids, repeats=1, excluded=(),
               cold=2, loaded=4):
    """One cell run directory. Tasks in `excluded` are planned but carry a
    run-meta exclusion and no judge output, which is how a whole task
    leaves a cell under the paired exclusion rule."""
    run_dir = Path(root) / name
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = {
        "run_id": name,
        "model": model,
        "effort": effort,
        "judge_model": "sonnet",
        "seed": 7,
        "repeats": repeats,
        "judge_repeats": 1,
        "preregistered": True,
        "excluded_tasks": [
            {"task": t, "failed_arms": ["loaded"],
             "reason": f"{t}-loaded: report has no non-empty Answers section"}
            for t in excluded
        ],
        "tasks": {
            t: {"skill": f"cat/skill-{t}", "fixture": "fx",
                "must_hit_ids": list(IDS)}
            for t in task_ids
        },
    }
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pids = [pair_id(t, r, repeats)
            for t in task_ids if t not in excluded
            for r in range(1, repeats + 1)]
    order = {"seed": 7, "order": {pid: dict(ORDER) for pid in pids}}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for pid in pids:
        (run_dir / "judge-outputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid,
                        "judgments": [_judgment(_hits(cold), _hits(loaded))]},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir


class ColumnDegradationThresholdTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        # 10 planned tasks per cell, single run: 2 endpoint cells x 10 =
        # 20 planned endpoint comparisons per column, so one excluded
        # task moves the column by exactly 5 percentage points.
        self.tasks = [f"t{i}" for i in range(1, 11)]

    def _column(self, prefix, model, low_excluded=(), max_excluded=()):
        return [
            _make_cell(self.root, f"{prefix}-low", model, "low", self.tasks,
                       excluded=low_excluded, cold=2, loaded=4),
            _make_cell(self.root, f"{prefix}-max", model, "max", self.tasks,
                       excluded=max_excluded, cold=3, loaded=4),
        ]

    def test_clean_column_passes_and_keeps_its_verdicts(self):
        matrix = report.matrix_scores(self._column("clean", "m1"))
        col = matrix["column_degradation"]["columns"]["m1"]
        self.assertEqual(col["planned_comparisons"], 20)
        self.assertEqual(col["excluded_comparisons"], 0)
        self.assertEqual(col["excluded_pct"], 0.0)
        self.assertFalse(col["degraded"])
        self.assertEqual(matrix["column_degradation"]["degraded_columns"], [])
        h1 = matrix["hypothesis_verdicts"]["h1"]["m1"]
        self.assertNotIn("column_degraded", h1)
        self.assertIn("cold_low_pct", h1)

    def test_column_above_threshold_is_degraded_and_issues_no_verdict(self):
        # 3 of 20 planned endpoint comparisons excluded = 15.0%, above 10%.
        matrix = report.matrix_scores(
            self._column("bad", "m1", low_excluded=("t1",),
                         max_excluded=("t2", "t3")))
        col = matrix["column_degradation"]["columns"]["m1"]
        self.assertEqual(col["excluded_comparisons"], 3)
        self.assertEqual(col["planned_comparisons"], 20)
        self.assertEqual(col["excluded_pct"], 15.0)
        self.assertTrue(col["degraded"])
        self.assertEqual(matrix["column_degradation"]["degraded_columns"],
                         ["m1"])
        for key in ("h1", "h2"):
            entry = matrix["hypothesis_verdicts"][key]["m1"]
            self.assertEqual(entry["verdict"], report.VERDICT_COLUMN_DEGRADED)
            self.assertTrue(entry["column_degraded"])
            # No support label and no endpoint values ride along: the
            # pre-registered rule issues no verdict from this column.
            self.assertNotIn("cold_low_pct", entry)
            self.assertNotIn("shrinkage_pp", entry)
            self.assertIn("3 of 20", entry["basis"])

    def test_exactly_ten_percent_is_not_degraded(self):
        # Boundary: 2 of 20 = exactly 10.0%. The rule degrades a column
        # only when exclusions EXCEED 10 percent, so this one still
        # carries its verdicts.
        matrix = report.matrix_scores(
            self._column("edge", "m1", low_excluded=("t1",),
                         max_excluded=("t2",)))
        col = matrix["column_degradation"]["columns"]["m1"]
        self.assertEqual(col["excluded_comparisons"], 2)
        self.assertEqual(col["planned_comparisons"], 20)
        self.assertEqual(col["excluded_pct"], 10.0)
        self.assertFalse(col["degraded"])
        h1 = matrix["hypothesis_verdicts"]["h1"]["m1"]
        self.assertIn(h1["verdict"], (report.VERDICT_SUPPORTED,
                                      report.VERDICT_NOT_SUPPORTED))

    def test_degradation_is_per_column(self):
        runs = (self._column("iso-a", "m1", max_excluded=("t1", "t2", "t3"))
                + self._column("iso-b", "m2"))
        matrix = report.matrix_scores(runs)
        cols = matrix["column_degradation"]["columns"]
        self.assertTrue(cols["m1"]["degraded"])
        self.assertFalse(cols["m2"]["degraded"])
        self.assertEqual(matrix["hypothesis_verdicts"]["h1"]["m1"]["verdict"],
                         report.VERDICT_COLUMN_DEGRADED)
        self.assertIn("cold_low_pct",
                      matrix["hypothesis_verdicts"]["h1"]["m2"])

    def test_interior_cell_exclusions_never_degrade_a_column(self):
        runs = self._column("int", "m1")
        runs.append(_make_cell(self.root, "int-high", "m1", "high",
                               self.tasks, excluded=tuple(self.tasks[:9])))
        matrix = report.matrix_scores(runs)
        col = matrix["column_degradation"]["columns"]["m1"]
        self.assertEqual(col["excluded_comparisons"], 0)
        self.assertFalse(col["degraded"])

    def test_replicated_endpoints_count_repeat_pairs(self):
        # The pre-registered PRIMARY denominator: 2 endpoints x 3 repeats
        # x 17 tasks = 102 per five-level column. One task lost at one
        # endpoint costs its 3 repeat pairs: 3/102 = 2.94%, under the
        # threshold.
        tasks = [f"t{i}" for i in range(1, 18)]
        low = _make_cell(self.root, "rep-low", "m1", "low", tasks,
                         repeats=3, cold=2, loaded=4)
        mx = _make_cell(self.root, "rep-max", "m1", "max", tasks,
                        repeats=3, excluded=("t1",), cold=3, loaded=4)
        col = report.matrix_scores(
            [low, mx])["column_degradation"]["columns"]["m1"]
        self.assertEqual(col["planned_comparisons"], 102)
        self.assertEqual(col["excluded_comparisons"], 3)
        self.assertEqual(col["excluded_pct"], 2.94)
        self.assertFalse(col["degraded"])
        self.assertEqual(col["per_cell"]["m1@low"]["surviving_comparisons"],
                         51)
        self.assertEqual(col["per_cell"]["m1@max"]["surviving_comparisons"],
                         48)

    def test_render_reports_the_threshold_and_marks_degraded_columns(self):
        clean = report.render_matrix(
            report.matrix_scores(self._column("r-ok", "m1")))
        self.assertIn("## Column degradation threshold (pre-registered)",
                      clean)
        self.assertIn("| m1 | low vs max | 0/20 | 0.0% | not degraded |",
                      clean)
        self.assertNotIn("DEGRADED", clean)
        degraded = report.render_matrix(report.matrix_scores(
            self._column("r-bad", "m1", max_excluded=("t1", "t2", "t3"))))
        self.assertIn(
            "| m1 | low vs max | 3/20 | 15.0% | DEGRADED (no verdict "
            "issued) |", degraded)
        self.assertIn(report.VERDICT_COLUMN_DEGRADED, degraded)
        # H4's side-by-side marks the degraded column and drops the
        # cross-family ordering statement.
        self.assertIn("DEGRADED under the pre-registered column threshold: "
                      "m1", degraded)


if __name__ == "__main__":
    unittest.main()
