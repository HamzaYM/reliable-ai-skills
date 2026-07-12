"""Matrix aggregation: cell identity, per-skill rates from raw judge data,
small-n labels, and the per-cell REPORT.md effort provenance."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import report


def _judgment(hits_1, hits_2, ids):
    return {
        "expectations": [
            {"expectation_id": i,
             "report_1": {"hit": h1, "evidence": "quote"},
             "report_2": {"hit": h2, "evidence": "quote"}}
            for i, h1, h2 in zip(ids, hits_1, hits_2)
        ],
        "comparative_verdict": "Report 2 answered the task better overall.",
    }


def _make_cell_dir(root, name, model, effort, outputs, tasks_meta,
                   excluded=()):
    """One completed cell run: run-meta, order key, raw judge outputs.

    Order key maps report_1 -> cold for every pair, so hits_1 are cold hits
    and hits_2 are loaded hits.
    """
    run_dir = Path(root) / name
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = {
        "run_id": name,
        "created_at": "2026-07-09T00:00:00Z",
        "model": model,
        "effort": effort,
        "judge_model": "sonnet",
        "seed": 7,
        "repeats": 1,
        "judge_repeats": 1,
        "preregistered": True,
        "excluded_tasks": [{"task": t, "reason": "consumer failed"}
                           for t in excluded],
        "tasks": tasks_meta,
    }
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    order = {"seed": 7, "order": {
        pid: {"report_1": "cold", "report_2": "loaded"} for pid in outputs
    }}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for pid, j in outputs.items():
        (run_dir / "judge-outputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid, "judgments": [j]},
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return run_dir


TASKS_META = {
    "t1": {"skill": "cat/skill-x", "fixture": "fx", "must_hit_ids": ["a", "b", "c"]},
    "t2": {"skill": "cat/skill-x", "fixture": "fx", "must_hit_ids": ["a", "b", "c"]},
}


class MatrixTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        # Cell 1: fable at low effort. cold 2/6, loaded 6/6.
        self.cell_low = _make_cell_dir(
            self.root, "run-low", "claude-fable-5", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        # Cell 2: fable at default effort. cold 4/6, loaded 5/6.
        self.cell_default = _make_cell_dir(
            self.root, "run-default", "claude-fable-5", "default",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, False], [True, True, False], ["a", "b", "c"])},
            TASKS_META,
        )

    def test_cells_and_ordering(self):
        matrix = report.matrix_scores([self.cell_default, self.cell_low])
        # low orders before default regardless of argument order.
        self.assertEqual(matrix["cell_order"],
                         ["claude-fable-5@low", "claude-fable-5@default"])
        self.assertEqual(set(matrix["cells"]), set(matrix["cell_order"]))

    def test_per_skill_rates_and_delta_from_data(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_default])
        low = matrix["skills"]["cat/skill-x"]["claude-fable-5@low"]
        self.assertEqual(low["n_tasks"], 2)
        self.assertEqual(low["n_must_hits"], 6)
        self.assertEqual(low["cold_hits"], 2)
        self.assertEqual(low["loaded_hits"], 6)
        self.assertEqual(low["cold_rate_pct"], 33.3)
        self.assertEqual(low["loaded_rate_pct"], 100.0)
        self.assertEqual(low["delta_pp"], 66.7)
        dflt = matrix["skills"]["cat/skill-x"]["claude-fable-5@default"]
        self.assertEqual((dflt["cold_hits"], dflt["loaded_hits"]), (4, 5))

    def test_small_n_label_on_every_cell(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_default])
        for cid, cell in matrix["cells"].items():
            self.assertIn("directional only", cell["aggregate"]["label"], cid)
            self.assertIn("n=2 tasks", cell["aggregate"]["label"], cid)
        for row in matrix["skills"].values():
            for cid, entry in row.items():
                self.assertIn("directional only", entry["label"], cid)
                self.assertIn("single run", entry["label"], cid)

    def test_duplicate_cell_rejected(self):
        dupe = _make_cell_dir(
            self.root, "run-low-again", "claude-fable-5", "low",
            {"t1": _judgment([True, True, True], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, True], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        with self.assertRaises(report.MatrixError):
            report.matrix_scores([self.cell_low, dupe])

    def test_non_run_dir_rejected(self):
        empty = Path(self.root) / "not-a-run"
        empty.mkdir()
        with self.assertRaises(report.MatrixError):
            report.matrix_scores([empty])

    def test_excluded_task_shrinks_denominator(self):
        cell = _make_cell_dir(
            self.root, "run-excl", "claude-fable-5", "high",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        matrix = report.matrix_scores([cell])
        agg = matrix["cells"]["claude-fable-5@high"]["aggregate"]
        self.assertEqual(agg["n_expectations"], 3)
        s = matrix["skills"]["cat/skill-x"]["claude-fable-5@high"]
        self.assertEqual(s["n_must_hits"], 3)
        self.assertIn("n=1 task,", s["label"])

    def test_skill_missing_in_a_cell_is_null(self):
        other = _make_cell_dir(
            self.root, "run-other-skill", "claude-fable-5", "xhigh",
            {"t9": _judgment([False, False], [True, True], ["a", "b"])},
            {"t9": {"skill": "cat/skill-y", "fixture": "fx",
                    "must_hit_ids": ["a", "b"]}},
        )
        matrix = report.matrix_scores([self.cell_low, other])
        self.assertIsNone(matrix["skills"]["cat/skill-y"]["claude-fable-5@low"])
        self.assertIsNone(matrix["skills"]["cat/skill-x"]["claude-fable-5@xhigh"])

    def test_render_matrix_markdown(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_default])
        text = report.render_matrix(matrix)
        self.assertIn("| Skill | claude-fable-5@low | claude-fable-5@default |", text)
        self.assertIn("cold 2/6 (33.3%), loaded 6/6 (100.0%), delta +66.7 pp", text)
        self.assertIn("directional only", text)
        # JSON emitter round-trips.
        self.assertEqual(json.loads(report.matrix_text(matrix))["cell_order"],
                         matrix["cell_order"])

    def test_render_matrix_missing_cell_dash(self):
        other = _make_cell_dir(
            self.root, "run-dash", "claude-fable-5", "xhigh",
            {"t9": _judgment([False, False], [True, True], ["a", "b"])},
            {"t9": {"skill": "cat/skill-y", "fixture": "fx",
                    "must_hit_ids": ["a", "b"]}},
        )
        text = report.render_matrix(report.matrix_scores([self.cell_low, other]))
        self.assertIn("| cat/skill-y | - |", text)


class MatrixBasisTest(unittest.TestCase):
    """Complete-case vs available-case, retention ratio R, headroom
    normalization, equal-skill weighting, ceiling counts."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        # low cell: both tasks valid. t1 cold 1/3 loaded 3/3, t2 cold 1/3
        # loaded 3/3 -> D(low) = +66.7 pp.
        self.cell_low = _make_cell_dir(
            self.root, "b-low", "m-generic", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        # max cell: t2 invalid (excluded). t1 cold 2/3 loaded 3/3.
        self.cell_max = _make_cell_dir(
            self.root, "b-max", "m-generic", "max",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )

    def test_complete_case_is_the_cross_cell_intersection(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        self.assertEqual(matrix["complete_case_tasks"], ["t1"])
        low_cc = matrix["cells"]["m-generic@low"]["aggregate_complete_case"]
        self.assertEqual(low_cc["basis"], "complete-case")
        self.assertEqual(low_cc["n_tasks"], 1)
        self.assertEqual(low_cc["n_expectations"], 3)
        self.assertEqual((low_cc["cold_hits"], low_cc["loaded_hits"]), (1, 3))
        # Available-case keeps the cell's own full valid set.
        low_av = matrix["cells"]["m-generic@low"]["aggregate"]
        self.assertEqual(low_av["basis"], "available-case")
        self.assertEqual(low_av["n_tasks"], 2)
        self.assertEqual(low_av["n_expectations"], 6)

    def test_complete_case_carries_small_n_label(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        for cid in matrix["cell_order"]:
            label = matrix["cells"][cid]["aggregate_complete_case"]["label"]
            self.assertIn("directional only", label, cid)
            self.assertIn("n=1 task,", label, cid)

    def test_retention_ratio_on_complete_case_delta(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        (r,) = matrix["retention"]
        self.assertEqual(r["model"], "m-generic")
        self.assertEqual(r["basis"], "complete-case")
        # complete-case t1: low delta (3-1)/3 = +66.7 pp; max delta
        # (3-2)/3 = +33.3 pp; R = 33.3/66.7 = 0.499.
        self.assertEqual(r["delta_low_pp"], 66.7)
        self.assertEqual(r["delta_max_pp"], 33.3)
        self.assertEqual(r["retention_ratio_R"], 0.499)

    def test_retention_undefined_when_d_low_not_positive(self):
        flat_low = _make_cell_dir(
            self.root, "b-low-flat", "other-model", "low",
            {"t1": _judgment([True, True, True], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        some_max = _make_cell_dir(
            self.root, "b-max-2", "other-model", "max",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        matrix = report.matrix_scores([flat_low, some_max])
        (r,) = matrix["retention"]
        self.assertIsNone(r["retention_ratio_R"])
        self.assertIn("absolute deltas only", r["note"])

    def test_retention_absent_without_both_endpoints(self):
        matrix = report.matrix_scores([self.cell_low])
        self.assertEqual(matrix["retention"], [])

    def test_headroom_normalized_delta(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        low = matrix["cells"]["m-generic@low"]["aggregate"]
        # cold 2/6, loaded 6/6: recovered 4 of 4 headroom = 100%.
        self.assertEqual(low["headroom_recovered_pct"], 100.0)
        mx = matrix["cells"]["m-generic@max"]["aggregate"]
        # cold 2/3, loaded 3/3: recovered 1 of 1 = 100%.
        self.assertEqual(mx["headroom_recovered_pct"], 100.0)

    def test_headroom_undefined_at_cold_ceiling(self):
        ceiling = _make_cell_dir(
            self.root, "b-ceiling", "other-model", "high",
            {"t1": _judgment([True, True, True], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        matrix = report.matrix_scores([ceiling])
        agg = matrix["cells"]["other-model@high"]["aggregate"]
        self.assertIsNone(agg["headroom_recovered_pct"])
        self.assertEqual(agg["ceiling_tasks"], {"cold": 1, "loaded": 1})

    def test_equal_skill_weighted_delta(self):
        two_skills_meta = {
            "t1": {"skill": "cat/skill-x", "fixture": "fx",
                   "must_hit_ids": ["a", "b", "c"]},
            "t9": {"skill": "cat/skill-y", "fixture": "fx",
                   "must_hit_ids": ["a", "b"]},
        }
        cell = _make_cell_dir(
            self.root, "b-two-skills", "other-model", "medium",
            {"t1": _judgment([False, False, False], [True, True, True], ["a", "b", "c"]),
             "t9": _judgment([True, True], [True, True], ["a", "b"])},
            two_skills_meta,
        )
        matrix = report.matrix_scores([cell])
        agg = matrix["cells"]["other-model@medium"]["aggregate"]
        # Must-hit-weighted: (5-3)/5 = +60.0 pp weighting skill-x's three
        # must-hits over skill-y's two; equal-skill: (100 + 0)/2 = +50.0.
        self.assertEqual(agg["delta_pp"], 60.0)
        self.assertEqual(agg["delta_pp_equal_skill"], 50.0)

    def test_render_includes_bases_and_retention(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        text = report.render_matrix(matrix)
        self.assertIn("## Cells (available-case)", text)
        self.assertIn("## Complete-case aggregate (tasks valid in every cell)",
                      text)
        self.assertIn("Common complete-case task set (1): t1.", text)
        self.assertIn("## Retention (low vs max, complete-case)", text)
        self.assertIn("R = 0.499", text)
        self.assertIn("Eq-skill delta (pp)", text)
        self.assertIn("Headroom", text)

    def test_render_retention_not_applicable(self):
        text = report.render_matrix(report.matrix_scores([self.cell_low]))
        self.assertIn("Not applicable: retention needs a low and a max cell",
                      text)


class LatticeViewsTest(unittest.TestCase):
    """Cross-model lattice: none-effort cells, matched-effort primary view,
    defaults-as-shipped labeled secondary view, H4 shrinkage side by side,
    and panel disagreement propagation into matrix outputs."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        self.fable_low = _make_cell_dir(
            self.root, "fable-low", "claude-other-5", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        self.fable_max = _make_cell_dir(
            self.root, "fable-max", "claude-other-5", "max",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        self.sonnet_low = _make_cell_dir(
            self.root, "sonnet-low", "claude-sonnet-5", "low",
            {"t1": _judgment([False, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([False, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        self.sonnet_default = _make_cell_dir(
            self.root, "sonnet-default", "claude-sonnet-5", "default",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        self.haiku_none = _make_cell_dir(
            self.root, "haiku-none", "claude-haiku-4-5", "none",
            {"t1": _judgment([True, False, False], [True, True, False], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, False], ["a", "b", "c"])},
            TASKS_META,
        )
        self.all_cells = [self.fable_low, self.fable_max, self.sonnet_low,
                          self.sonnet_default, self.haiku_none]

    def test_none_effort_orders_after_default(self):
        matrix = report.matrix_scores([self.haiku_none, self.sonnet_default,
                                       self.sonnet_low])
        self.assertEqual(matrix["cell_order"], [
            "claude-haiku-4-5@none", "claude-sonnet-5@low",
            "claude-sonnet-5@default",
        ])

    def test_matched_effort_primary_view(self):
        matrix = report.matrix_scores(self.all_cells)
        matched = matrix["views"]["matched_effort"]
        self.assertEqual(matched["role"], "primary")
        self.assertEqual(matched["basis"], "complete-case")
        # Both models have a low cell: side by side at the same effort.
        low = matched["efforts"]["low"]
        self.assertEqual(sorted(low), ["claude-other-5", "claude-sonnet-5"])
        self.assertEqual(low["claude-other-5"]["delta_pp"], 66.7)
        self.assertEqual(low["claude-sonnet-5"]["delta_pp"], 100.0)
        self.assertIn("directional only", low["claude-other-5"]["label"])
        # max exists for fable only; default and none cells never appear.
        self.assertEqual(sorted(matched["efforts"]["max"]), ["claude-other-5"])
        self.assertNotIn("default", matched["efforts"])
        self.assertNotIn("none", matched["efforts"])
        for row in matched["efforts"].values():
            self.assertNotIn("claude-haiku-4-5", row)

    def test_defaults_as_shipped_secondary_view(self):
        matrix = report.matrix_scores(self.all_cells)
        defaults = matrix["views"]["defaults_as_shipped"]
        self.assertIn("labeled", defaults["role"])
        self.assertIn("conflate", defaults["note"])
        models = defaults["models"]
        self.assertEqual(sorted(models), ["claude-haiku-4-5", "claude-sonnet-5"])
        self.assertEqual(models["claude-haiku-4-5"]["effort"], "none")
        self.assertEqual(models["claude-sonnet-5"]["effort"], "default")
        self.assertIn("directional only", models["claude-haiku-4-5"]["label"])

    def test_h4_shrinkage_side_by_side_mirrors_retention(self):
        matrix = report.matrix_scores(self.all_cells)
        h4 = matrix["views"]["h4_shrinkage"]
        self.assertEqual(h4["role"], "EXPLORATORY (directional only)")
        self.assertEqual(h4["entries"], matrix["retention"])
        (entry,) = h4["entries"]
        self.assertEqual(entry["model"], "claude-other-5")
        self.assertEqual(entry["delta_low_pp"], 66.7)
        self.assertEqual(entry["delta_max_pp"], 33.3)
        self.assertEqual(entry["retention_ratio_R"], 0.499)
        self.assertIn("effort-invariant models are excluded", h4["note"])

    def test_render_includes_lattice_sections(self):
        text = report.render_matrix(report.matrix_scores(self.all_cells))
        self.assertIn("## Cross-model views (complete-case)", text)
        self.assertIn("### Matched effort (primary)", text)
        self.assertIn("| low | claude-other-5 | claude-other-5@low |", text)
        self.assertIn("| low | claude-sonnet-5 | claude-sonnet-5@low |", text)
        self.assertIn("### Defaults as shipped (secondary, labeled)", text)
        self.assertIn("conflate model", text)
        self.assertIn("| claude-haiku-4-5 | none | claude-haiku-4-5@none |", text)
        self.assertIn(
            "### H4 shrinkage side by side (EXPLORATORY, directional only)",
            text)
        self.assertIn("| Model | D(low) pp | D(max) pp | R |", text)
        self.assertIn("| claude-other-5 | +66.7 | +33.3 | 0.499 |", text)

    def test_render_views_not_applicable_lines(self):
        text = report.render_matrix(report.matrix_scores([self.haiku_none]))
        self.assertIn("- No cells at an explicit effort level.", text)
        self.assertIn("- Not applicable: H4 needs a low and a max cell", text)

    def test_panel_disagreement_propagates_into_matrix(self):
        # A panel cell: per-judge files instead of one judgments file.
        run_dir = Path(self.root) / "panel-cell"
        (run_dir / "judge-outputs").mkdir(parents=True)
        meta = {
            "run_id": "panel-cell", "created_at": "2026-07-10T00:00:00Z",
            "model": "claude-opus-4-8", "effort": "medium",
            "judge_model": "two-judge panel (see judge_panel)",
            "judge_panel": {"models": ["claude-sonnet-5", "claude-opus-4-8"],
                            "effort": "medium"},
            "seed": 7, "repeats": 1, "judge_repeats": 1,
            "preregistered": True, "excluded_tasks": [],
            "tasks": {"t1": TASKS_META["t1"]},
        }
        (run_dir / "run-meta.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (run_dir / "order-key.json").write_text(
            json.dumps({"seed": 7, "order": {
                "t1": {"report_1": "cold", "report_2": "loaded"}
            }}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        judgments = {
            "claude-sonnet-5": _judgment([True, False, False],
                                         [True, True, True], ["a", "b", "c"]),
            "claude-opus-4-8": _judgment([True, False, False],
                                         [True, True, False], ["a", "b", "c"]),
        }
        for jm, j in judgments.items():
            (run_dir / "judge-outputs" / f"t1.{jm}.json").write_text(
                json.dumps({"pair": "t1", "judge_model": jm,
                            "judge_effort": "medium", "judgments": [j],
                            "cli_meta": []}, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        matrix = report.matrix_scores([run_dir, self.fable_low])
        cell = matrix["cells"]["claude-opus-4-8@medium"]
        self.assertEqual(cell["judge_disagreement"], {
            "n_marks": 3, "n_disagreed": 1, "disagreement_rate_pct": 33.3,
        })
        # Legacy single-judge cells carry no disagreement block.
        self.assertNotIn("judge_disagreement",
                         matrix["cells"]["claude-other-5@low"])
        text = report.render_matrix(matrix)
        self.assertIn("## Judge panel disagreement", text)
        self.assertIn(
            "- claude-opus-4-8@medium: 1 of 3 marks disagreed (33.3%)", text
        )

    def test_no_panel_cells_note(self):
        text = report.render_matrix(report.matrix_scores([self.fable_low]))
        self.assertIn("- No two-judge-panel cells in this matrix.", text)


class ReportEffortProvenanceTest(unittest.TestCase):
    def test_report_names_the_cell(self):
        with tempfile.TemporaryDirectory() as root:
            run_dir = _make_cell_dir(
                root, "run-low", "claude-fable-5", "low",
                {"t1": _judgment([True, False, False], [True, True, True],
                                 ["a", "b", "c"]),
                 "t2": _judgment([True, False, False], [True, True, True],
                                 ["a", "b", "c"])},
                TASKS_META,
            )
            _, report_text = report.recompute(run_dir)
        self.assertIn("- Consumer model: claude-fable-5", report_text)
        self.assertIn("- Consumer effort: low", report_text)
        # Pre-budget run-meta: the conditional provenance lines must be
        # absent so committed runs replay byte-for-byte.
        self.assertNotIn("Max output tokens", report_text)
        self.assertNotIn("Consumer models effective", report_text)

    def test_report_shows_budget_and_effective_models_when_recorded(self):
        with tempfile.TemporaryDirectory() as root:
            run_dir = _make_cell_dir(
                root, "run-budget", "claude-fable-5", "max",
                {"t1": _judgment([True, False, False], [True, True, True],
                                 ["a", "b", "c"]),
                 "t2": _judgment([True, False, False], [True, True, True],
                                 ["a", "b", "c"])},
                TASKS_META,
            )
            meta_path = run_dir / "run-meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["max_output_tokens"] = {"value": 64000, "mechanism": "env"}
            meta["consumer_models_effective"] = ["claude-fable-5"]
            meta_path.write_text(
                json.dumps(meta, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            _, report_text = report.recompute(run_dir)
        self.assertIn("- Max output tokens (pinned, both arms): 64000",
                      report_text)
        self.assertIn("- Consumer models effective: claude-fable-5",
                      report_text)


class EndpointAmendmentTest(unittest.TestCase):
    """Fable's confirmatory endpoint is low-vs-high, not low-vs-max
    (effort-sweep-amendment-2026-07-10-fable-endpoint.md), and the
    complete-case set feeding H1/H2/retention/H4 is scoped per model
    column over that column's endpoint cells only -- neither another
    model's exclusions nor an interior cell's exclusions can shrink it
    (effort-sweep-preregistration.md section 5, line 115)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name

    def test_fable_endpoint_is_low_vs_high_not_max(self):
        low = _make_cell_dir(
            self.root, "f-low", "claude-fable-5", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        high = _make_cell_dir(
            self.root, "f-high", "claude-fable-5", "high",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        # max exists with deliberately different numbers (cold 0%) so the
        # test fails loudly if the code ever falls back to using it.
        maxcell = _make_cell_dir(
            self.root, "f-max", "claude-fable-5", "max",
            {"t1": _judgment([False, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([False, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        matrix = report.matrix_scores([low, high, maxcell])
        h1 = matrix["hypothesis_verdicts"]["h1"]["claude-fable-5"]
        self.assertEqual(h1["endpoint_effort"], "high")
        self.assertEqual(h1["cold_low_pct"], 33.3)
        # cold(high) 66.7, NOT cold(max) 0.0 -- proves max is ignored.
        self.assertEqual(h1["cold_max_pct"], 66.7)
        self.assertEqual(h1["difference_pp"], 33.4)
        retention = {r["model"]: r for r in matrix["retention"]}["claude-fable-5"]
        self.assertEqual(retention["endpoint_effort"], "high")
        self.assertIn("D(high)/D(low)", retention["note"])

    def test_complete_case_is_scoped_per_model_column_not_global(self):
        # Sonnet's low+max pair is fully complete (both tasks valid).
        sonnet_low = _make_cell_dir(
            self.root, "s-low", "claude-sonnet-5", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        sonnet_max = _make_cell_dir(
            self.root, "s-max", "claude-sonnet-5", "max",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        # Fable's low cell excludes t2 entirely -- under the old global
        # intersection this would have dropped t2 from Sonnet's
        # complete-case set too. It must not.
        fable_low = _make_cell_dir(
            self.root, "fx-low", "claude-fable-5", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        fable_high = _make_cell_dir(
            self.root, "fx-high", "claude-fable-5", "high",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        matrix = report.matrix_scores(
            [sonnet_low, sonnet_max, fable_low, fable_high])
        h1 = matrix["hypothesis_verdicts"]["h1"]["claude-sonnet-5"]
        # Sonnet's own complete-case set still has both tasks (n=6
        # expectations, not n=3) despite Fable's t2 exclusion elsewhere.
        self.assertEqual(h1["cold_low_pct"], 33.3)
        self.assertEqual(h1["cold_max_pct"], 66.7)
        # The cross-model descriptive complete_case_tasks set is
        # unaffected by this fix (still the old global behavior,
        # deliberately) -- it legitimately shrinks to t1 only.
        self.assertEqual(matrix["complete_case_tasks"], ["t1"])

    def test_interior_cell_exclusion_does_not_shrink_endpoint_complete_case(self):
        low = _make_cell_dir(
            self.root, "i-low", "claude-sonnet-5", "low",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        maxcell = _make_cell_dir(
            self.root, "i-max", "claude-sonnet-5", "max",
            {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        # Interior cell (medium) excludes t2 -- per the pre-reg, interior
        # cells can never remove a task from the endpoint complete-case
        # set.
        medium = _make_cell_dir(
            self.root, "i-medium", "claude-sonnet-5", "medium",
            {"t1": _judgment([True, True, True], [True, True, True], ["a", "b", "c"])},
            TASKS_META, excluded=("t2",),
        )
        matrix = report.matrix_scores([low, maxcell, medium])
        h1 = matrix["hypothesis_verdicts"]["h1"]["claude-sonnet-5"]
        self.assertEqual(h1["cold_low_pct"], 33.3)
        self.assertEqual(h1["cold_max_pct"], 66.7)

    def test_report_defaults_effort_for_legacy_meta(self):
        with tempfile.TemporaryDirectory() as root:
            run_dir = _make_cell_dir(
                root, "run-legacy", "sonnet", "default",
                {"t1": _judgment([True, False, False], [True, True, True],
                                 ["a", "b", "c"]),
                 "t2": _judgment([True, False, False], [True, True, True],
                                 ["a", "b", "c"])},
                TASKS_META,
            )
            # Simulate a pre-effort run-meta with no effort key at all.
            meta_path = run_dir / "run-meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            del meta["effort"]
            meta_path.write_text(
                json.dumps(meta, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            _, report_text = report.recompute(run_dir)
        self.assertIn("- Consumer effort: default", report_text)


def _make_replicated_cell_dir(root, name, model, effort, per_repeat_outputs,
                              tasks_meta):
    """A replicated cell: per_repeat_outputs maps a 1-based repeat index to
    {task_id: judgment}. Pair ids carry the repeat suffix (t1-r2) when
    repeats > 1 so score_run aggregates repeat-level means, matching the
    live harness pair_id convention."""
    run_dir = Path(root) / name
    (run_dir / "judge-outputs").mkdir(parents=True)
    repeats = len(per_repeat_outputs)
    meta = {
        "run_id": name, "created_at": "2026-07-09T00:00:00Z",
        "model": model, "effort": effort, "judge_model": "sonnet",
        "seed": 7, "repeats": repeats, "judge_repeats": 1,
        "preregistered": True, "excluded_tasks": [], "tasks": tasks_meta,
    }
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pairs = {}
    for rk, outs in per_repeat_outputs.items():
        for tid, j in outs.items():
            pairs[f"{tid}-r{rk}" if repeats > 1 else tid] = j
    order = {"seed": 7, "order": {
        pid: {"report_1": "cold", "report_2": "loaded"} for pid in pairs}}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for pid, j in pairs.items():
        (run_dir / "judge-outputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid, "judgments": [j]},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir


class H4MatchedLowHighTest(unittest.TestCase):
    """The additive matched low-to-high H4 view fulfilling the amendment's
    deferred item (effort-sweep-amendment-2026-07-10-fable-endpoint.md
    section (c)): all three effort-bearing models compared on ONE common
    low-to-high basis, with the Sonnet/Opus high cell labeled an interior
    single-run cell (no repeats, descriptive only) and Fable's high its
    replicated confirmatory endpoint."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        # Fable (high is its replicated confirmatory endpoint):
        #   low  R2: r1 cold 2/6 delta 66.7, r2 cold 4/6 delta 33.3
        #            -> mean delta +50.0
        #   high R2: both repeats cold 4/6 delta 33.3 -> mean delta +33.3
        #   matched shrinkage = 50.0 - 33.3 = +16.7
        self.fable_low = _make_replicated_cell_dir(
            self.root, "f-low", "claude-fable-5", "low",
            {1: {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
                 "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
             2: {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
                 "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])}},
            TASKS_META,
        )
        self.fable_high = _make_replicated_cell_dir(
            self.root, "f-high", "claude-fable-5", "high",
            {1: {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
                 "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])},
             2: {"t1": _judgment([True, True, False], [True, True, True], ["a", "b", "c"]),
                 "t2": _judgment([True, True, False], [True, True, True], ["a", "b", "c"])}},
            TASKS_META,
        )
        # Fable max has deliberately different numbers (cold 0, delta 0) so
        # the matched view fails loudly if it ever reads max instead of high.
        self.fable_max = _make_replicated_cell_dir(
            self.root, "f-max", "claude-fable-5", "max",
            {1: {"t1": _judgment([False, False, False], [False, False, False], ["a", "b", "c"]),
                 "t2": _judgment([False, False, False], [False, False, False], ["a", "b", "c"])},
             2: {"t1": _judgment([False, False, False], [False, False, False], ["a", "b", "c"]),
                 "t2": _judgment([False, False, False], [False, False, False], ["a", "b", "c"])}},
            TASKS_META,
        )
        # Sonnet (high is an interior single-run cell):
        #   low  R2: both repeats cold 0/6 delta 100 -> mean delta +100.0
        #   high single run: cold 2/6 delta 66.7
        #   matched shrinkage = 100.0 - 66.7 = +33.3
        self.sonnet_low = _make_replicated_cell_dir(
            self.root, "s-low", "claude-sonnet-5", "low",
            {1: {"t1": _judgment([False, False, False], [True, True, True], ["a", "b", "c"]),
                 "t2": _judgment([False, False, False], [True, True, True], ["a", "b", "c"])},
             2: {"t1": _judgment([False, False, False], [True, True, True], ["a", "b", "c"]),
                 "t2": _judgment([False, False, False], [True, True, True], ["a", "b", "c"])}},
            TASKS_META,
        )
        self.sonnet_high = _make_cell_dir(
            self.root, "s-high", "claude-sonnet-5", "high",
            {"t1": _judgment([True, False, False], [True, True, True], ["a", "b", "c"]),
             "t2": _judgment([True, False, False], [True, True, True], ["a", "b", "c"])},
            TASKS_META,
        )
        # Sonnet max: distinct numbers so a max-vs-high mixup is caught.
        self.sonnet_max = _make_replicated_cell_dir(
            self.root, "s-max", "claude-sonnet-5", "max",
            {1: {"t1": _judgment([False, False, False], [False, False, False], ["a", "b", "c"]),
                 "t2": _judgment([False, False, False], [False, False, False], ["a", "b", "c"])},
             2: {"t1": _judgment([False, False, False], [False, False, False], ["a", "b", "c"]),
                 "t2": _judgment([False, False, False], [False, False, False], ["a", "b", "c"])}},
            TASKS_META,
        )
        self.all_cells = [self.fable_low, self.fable_high, self.fable_max,
                          self.sonnet_low, self.sonnet_high, self.sonnet_max]

    def _entries(self):
        matrix = report.matrix_scores(self.all_cells)
        return matrix, {e["model"]: e
                        for e in matrix["h4_matched_low_high"]["entries"]}

    def test_view_present_and_labeled_additive_exploratory(self):
        matrix, _ = self._entries()
        view = matrix["h4_matched_low_high"]
        self.assertIn("ADDITIVE", view["role"])
        self.assertIn("EXPLORATORY", view["role"])
        self.assertIn("low-to-high", view["basis"])
        self.assertIn("section (c)", view["note"])

    def test_both_models_present_on_low_to_high_basis(self):
        _, entries = self._entries()
        self.assertEqual(sorted(entries), ["claude-fable-5", "claude-sonnet-5"])
        for e in entries.values():
            self.assertEqual(e["endpoint_effort"], "high")
            self.assertEqual(e["n_tasks"], 2)

    def test_fable_high_is_replicated_endpoint(self):
        _, entries = self._entries()
        e = entries["claude-fable-5"]
        # D(low) +50.0 (R2 mean), D(high) +33.3 (R2 mean), shrinkage +16.7.
        self.assertEqual(e["delta_low_pp"], 50.0)
        self.assertEqual(e["delta_high_pp"], 33.3)
        self.assertEqual(e["shrinkage_pp"], 16.7)
        self.assertFalse(e["high_cell_interior_single_run"])
        self.assertTrue(e["high_cell_replicated"])
        self.assertEqual(e["high_cell_repeats"], 2)
        self.assertIn("replicated confirmatory endpoint", e["note"])

    def test_sonnet_high_is_interior_single_run(self):
        _, entries = self._entries()
        e = entries["claude-sonnet-5"]
        # D(low) +100.0 (R2 mean), D(high) +66.7 (single run), shrink +33.3.
        self.assertEqual(e["delta_low_pp"], 100.0)
        self.assertEqual(e["delta_high_pp"], 66.7)
        self.assertEqual(e["shrinkage_pp"], 33.3)
        self.assertTrue(e["high_cell_interior_single_run"])
        self.assertFalse(e["high_cell_replicated"])
        self.assertEqual(e["high_cell_repeats"], 1)
        self.assertIn("interior single-run cell (no repeats)", e["note"])

    def test_uses_high_cell_not_max(self):
        # Both models carry a max cell with cold 0 / delta 0; the matched
        # view must read the high cell (delta +33.3 / +66.7), never max.
        _, entries = self._entries()
        self.assertEqual(entries["claude-fable-5"]["delta_high_pp"], 33.3)
        self.assertEqual(entries["claude-sonnet-5"]["delta_high_pp"], 66.7)

    def test_additive_leaves_existing_h4_and_retention_untouched(self):
        matrix, _ = self._entries()
        # Existing keys still present and independent of the new view.
        self.assertIn("retention", matrix)
        self.assertIn("h4_shrinkage", matrix["views"])
        self.assertIn("hypothesis_verdicts", matrix)
        # Existing per-model H4/retention still uses each model's
        # confirmatory endpoint (Fable low-vs-high, Sonnet low-vs-max).
        ret = {r["model"]: r for r in matrix["retention"]}
        self.assertEqual(ret["claude-sonnet-5"]["endpoint_effort"], "max")
        self.assertEqual(ret["claude-fable-5"]["endpoint_effort"], "high")

    def test_render_includes_matched_section_and_labels(self):
        text = report.render_matrix(report.matrix_scores(self.all_cells))
        self.assertIn(
            "## H4 matched low-to-high view (EXPLORATORY, additive)", text)
        self.assertIn("section (c)", text)
        self.assertIn(
            "| Model | D(low) pp | D(high) pp | Shrinkage (pp) | High cell |",
            text)
        self.assertIn(
            "| claude-fable-5 | +50.0 | +33.3 | +16.7 "
            "| replicated endpoint (R2 mean) |", text)
        self.assertIn(
            "| claude-sonnet-5 | +100.0 | +66.7 | +33.3 "
            "| interior single-run (no repeats, descriptive only) |", text)

    def test_render_not_applicable_without_high_cell(self):
        text = report.render_matrix(report.matrix_scores([self.sonnet_low]))
        self.assertIn("## H4 matched low-to-high view (EXPLORATORY, additive)",
                      text)
        self.assertIn(
            "- Not applicable: the matched view needs a low and a high cell",
            text)


if __name__ == "__main__":
    unittest.main()
