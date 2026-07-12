"""Lattice report additions: pre-registered 3 pp endpoint verdicts (H1,
H2), interior-cell immunity, invalidation rates by model x effort x arm
(natural vs censored), the deterministic task-cluster bootstrap, and the
EXPLORATORY / suppression labeling."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import report

ORDER = {"report_1": "cold", "report_2": "loaded"}


def _judgment(hits_1, hits_2, ids):
    return {
        "expectations": [
            {"expectation_id": i,
             "report_1": {"hit": h1, "evidence": "q"},
             "report_2": {"hit": h2, "evidence": "q"}}
            for i, h1, h2 in zip(ids, hits_1, hits_2)
        ],
        "comparative_verdict": "comparable",
    }


TASKS_META = {
    "t1": {"skill": "cat/skill-x", "fixture": "fx",
           "must_hit_ids": ["a", "b", "c", "d", "e"]},
    "t2": {"skill": "cat/skill-y", "fixture": "fx",
           "must_hit_ids": ["a", "b", "c", "d", "e"]},
}


def _make_cell(root, name, model, effort, outputs, tasks_meta=TASKS_META,
               excluded=()):
    run_dir = Path(root) / name
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = {
        "run_id": name,
        "model": model,
        "effort": effort,
        "judge_model": "sonnet",
        "seed": 7,
        "repeats": 1,
        "judge_repeats": 1,
        "preregistered": True,
        "excluded_tasks": list(excluded),
        "tasks": tasks_meta,
    }
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    order = {"seed": 7, "order": {pid: dict(ORDER) for pid in outputs}}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for pid, j in outputs.items():
        (run_dir / "judge-outputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid, "judgments": [j]},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir


def _hits(n, total=5):
    return [True] * n + [False] * (total - n)


IDS = ["a", "b", "c", "d", "e"]


class HypothesisVerdictTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name

    def _cell(self, name, effort, cold_hits, loaded_hits, model="m1"):
        return _make_cell(
            self.root, name, model, effort,
            {"t1": _judgment(_hits(cold_hits), _hits(loaded_hits), IDS),
             "t2": _judgment(_hits(cold_hits), _hits(loaded_hits), IDS)},
        )

    def test_h1_and_h2_supported_at_or_above_3pp(self):
        # cold(low) 40% with D(low) +40 pp; cold(max) 60% with D(max)
        # +20 pp: H1 diff +20 pp, H2 shrinkage +20 pp, both >= 3 pp.
        low = self._cell("v-low", "low", 2, 4)
        mx = self._cell("v-max", "max", 3, 4)
        matrix = report.matrix_scores([low, mx])
        v = matrix["hypothesis_verdicts"]
        h1 = v["h1"]["m1"]
        self.assertEqual(h1["cold_low_pct"], 40.0)
        self.assertEqual(h1["cold_max_pct"], 60.0)
        self.assertEqual(h1["difference_pp"], 20.0)
        self.assertEqual(
            h1["verdict"],
            "directionally supported under the pre-registered rule")
        h2 = v["h2"]["m1"]
        self.assertEqual(h2["delta_low_pp"], 40.0)
        self.assertEqual(h2["delta_max_pp"], 20.0)
        self.assertEqual(h2["shrinkage_pp"], 20.0)
        self.assertEqual(
            h2["verdict"],
            "directionally supported under the pre-registered rule")

    def test_strict_inequality_alone_is_never_sufficient(self):
        # Equal endpoints: 0.0 pp differences are strictly non-negative
        # but below the 3 pp minimum effect, so both verdicts read "not
        # supported under the pre-registered rule".
        low = self._cell("s-low", "low", 4, 5)
        mx = self._cell("s-max", "max", 4, 5)
        matrix = report.matrix_scores([low, mx])
        h1 = matrix["hypothesis_verdicts"]["h1"]["m1"]
        self.assertEqual(h1["difference_pp"], 0.0)
        self.assertEqual(h1["verdict"],
                         "not supported under the pre-registered rule")
        h2 = matrix["hypothesis_verdicts"]["h2"]["m1"]
        self.assertEqual(h2["shrinkage_pp"], 0.0)
        self.assertEqual(h2["verdict"],
                         "not supported under the pre-registered rule")

    def test_3pp_boundary_exact_and_below(self):
        # Unit-level boundary check on the verdict function itself: a
        # 2.9 pp difference fails, exactly 3.0 pp passes.
        def cell(model, effort, cold, delta):
            return {
                "model": model, "effort": effort, "repeats": 1,
                "aggregate_endpoint_complete_case": {
                    "cold_rate_pct": cold,
                    "loaded_rate_pct": cold + delta,
                    "delta_pp": delta,
                },
            }

        below = report._hypothesis_verdicts({
            "m@low": cell("m", "low", 40.0, 10.0),
            "m@max": cell("m", "max", 42.9, 2.9 + 10.0 - 5.9),
        })
        # cold: 42.9 - 40.0 = 2.9 pp -> below the floor.
        self.assertEqual(below["h1"]["m"]["difference_pp"], 2.9)
        self.assertEqual(below["h1"]["m"]["verdict"],
                         "not supported under the pre-registered rule")
        exact = report._hypothesis_verdicts({
            "m@low": cell("m", "low", 40.0, 10.0),
            "m@max": cell("m", "max", 43.0, 7.0),
        })
        self.assertEqual(exact["h1"]["m"]["difference_pp"], 3.0)
        self.assertEqual(
            exact["h1"]["m"]["verdict"],
            "directionally supported under the pre-registered rule")
        self.assertEqual(exact["h2"]["m"]["shrinkage_pp"], 3.0)
        self.assertEqual(
            exact["h2"]["m"]["verdict"],
            "directionally supported under the pre-registered rule")

    def test_interior_cells_cannot_affect_h1_h2(self):
        low = self._cell("i-low", "low", 2, 4)
        mx = self._cell("i-max", "max", 3, 4)
        base = report.matrix_scores([low, mx])["hypothesis_verdicts"]
        # Add wild interior cells: verdict entries must be identical.
        medium = self._cell("i-med", "medium", 0, 5)
        high = self._cell("i-high", "high", 5, 0)
        with_interior = report.matrix_scores(
            [low, mx, medium, high])["hypothesis_verdicts"]
        self.assertEqual(base["h1"], with_interior["h1"])
        self.assertEqual(base["h2"], with_interior["h2"])
        self.assertIn("cannot affect H1 or H2", with_interior["scope"])

    def test_no_endpoints_not_evaluable_line(self):
        medium = self._cell("n-med", "medium", 2, 4)
        matrix = report.matrix_scores([medium])
        self.assertEqual(matrix["hypothesis_verdicts"]["h1"], {})
        text = report.render_matrix(matrix)
        self.assertIn("Not evaluable: H1/H2 need a low and a max endpoint",
                      text)

    def test_render_verdict_tables_and_exact_strings(self):
        low = self._cell("r-low", "low", 4, 5)
        mx = self._cell("r-max", "max", 4, 5)
        text = report.render_matrix(report.matrix_scores([low, mx]))
        self.assertIn("## Hypothesis verdicts (confirmatory: H1 and H2 only)",
                      text)
        self.assertIn("### H1 (cold-arm endpoint gain)", text)
        self.assertIn("### H2 (delta shrinkage low to max)", text)
        self.assertIn("not supported under the pre-registered rule", text)
        self.assertIn("strict inequalities alone are never sufficient", text)


class InvalidationTableTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name

    def test_natural_vs_censored_by_arm(self):
        excluded = [
            {"task": "t2", "failed_arms": ["cold"],
             "reason": "t2-cold: consumer output truncated by the pinned "
                       "64000-token ceiling"},
            {"task": "t3", "failed_arms": ["loaded"],
             "reason": "t3-loaded: report has no non-empty Answers section"},
            {"task": "t4", "reason": "judging failed: timed out after 300s"},
        ]
        tasks_meta = dict(TASKS_META)
        tasks_meta["t3"] = dict(TASKS_META["t2"])
        tasks_meta["t4"] = dict(TASKS_META["t2"])
        cell = _make_cell(
            self.root, "inv-cell", "m1", "low",
            {"t1": _judgment(_hits(2), _hits(4), IDS)},
            tasks_meta=tasks_meta, excluded=excluded)
        matrix = report.matrix_scores([cell])
        inv = matrix["cells"]["m1@low"]["invalidation"]
        self.assertEqual(inv["planned_tasks"], 4)
        self.assertEqual(inv["arms"]["cold"],
                         {"n_invalid": 1, "natural_completion": 0,
                          "harness_censored": 1, "rate_pct": 25.0})
        self.assertEqual(inv["arms"]["loaded"],
                         {"n_invalid": 1, "natural_completion": 1,
                          "harness_censored": 0, "rate_pct": 25.0})
        self.assertEqual(inv["judging"],
                         {"n_tasks": 1, "natural_completion": 0,
                          "harness_censored": 1})
        text = report.render_matrix(matrix)
        self.assertIn("## Invalidation rates by model x effort x arm", text)
        self.assertIn("| m1@low | cold | 1/4 | 25.0% | 0 | 1 |", text)
        self.assertIn("| m1@low | loaded | 1/4 | 25.0% | 1 | 0 |", text)
        self.assertIn("| m1@low | judging | 1/4 | - | 0 | 1 |", text)


class BootstrapTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        self.cell = _make_cell(
            self.root, "boot-cell", "m1", "low",
            {"t1": _judgment(_hits(1), _hits(5), IDS),
             "t2": _judgment(_hits(4), _hits(4), IDS)})

    def test_deterministic_and_labeled_non_inferential(self):
        m1 = report.matrix_scores([self.cell])
        m2 = report.matrix_scores([self.cell])
        self.assertEqual(m1["bootstrap"], m2["bootstrap"])
        boot = m1["bootstrap"]
        self.assertIn("non-inferential", boot["label"])
        self.assertIn("descriptive", boot["label"])
        self.assertEqual(boot["seed"], report.BOOTSTRAP_SEED)
        self.assertEqual(boot["iterations"], report.BOOTSTRAP_ITERATIONS)
        entry = boot["cells"]["m1@low"]
        self.assertEqual(entry["n_resamples"], report.BOOTSTRAP_ITERATIONS)
        # Two clusters with deltas +80 and 0: resamples land on 0, +40,
        # or +80 pp, so the percentiles must be within that range.
        for key in ("delta_pp_p2_5", "delta_pp_p50", "delta_pp_p97_5"):
            self.assertIn(entry[key], (0.0, 40.0, 80.0))
        self.assertLessEqual(entry["delta_pp_p2_5"], entry["delta_pp_p50"])
        self.assertLessEqual(entry["delta_pp_p50"], entry["delta_pp_p97_5"])

    def test_rendered_with_seed_and_label(self):
        text = report.render_matrix(report.matrix_scores([self.cell]))
        self.assertIn("## Task-cluster bootstrap (descriptive, "
                      "non-inferential)", text)
        self.assertIn(f"Seed {report.BOOTSTRAP_SEED}", text)


class LabelingTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.cell = _make_cell(
            self._tmp.name, "lab-cell", "m1", "low",
            {"t1": _judgment(_hits(2), _hits(4), IDS),
             "t2": _judgment(_hits(2), _hits(4), IDS)})

    def test_h3_h4_exploratory_and_skill_suppression(self):
        matrix = report.matrix_scores([self.cell])
        self.assertEqual(matrix["views"]["h3_visibility_tags"]["role"],
                         "EXPLORATORY")
        self.assertEqual(matrix["views"]["h4_shrinkage"]["role"],
                         "EXPLORATORY (directional only)")
        self.assertIn("suppressed", matrix["per_skill_note"])
        # No per-skill PASS/FAIL anywhere in lattice outputs.
        for row in matrix["skills"].values():
            for entry in row.values():
                if entry is not None:
                    self.assertNotIn("pass", entry)
        text = report.render_matrix(matrix)
        self.assertIn("### H3 visibility tags (EXPLORATORY)", text)
        self.assertIn(
            "### H4 shrinkage side by side (EXPLORATORY, directional only)",
            text)
        self.assertIn("PASS/FAIL", text)
        self.assertNotIn("| PASS |", text)
        self.assertNotIn("| FAIL |", text)


if __name__ == "__main__":
    unittest.main()
