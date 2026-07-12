"""Repeats: per-repeat isolated workspaces (no shared session state),
repeat index in every artifact, repeat-level values retained, and
endpoint mean-rate aggregation in scores and matrix outputs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_mod
from harness import consumer, report, scoring

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


class RepeatIndexInArtifactsTest(unittest.TestCase):
    def test_pair_id_carries_repeat_index(self):
        self.assertEqual(scoring.pair_id("t1", 1, 1), "t1")
        self.assertEqual(scoring.pair_id("t1", 2, 3), "t1-r2")

    def test_ab_pairs_yields_repeat_indices(self):
        tasks = [{"id": "t1"}]
        pairs = list(run_mod.ab_pairs(tasks, 3))
        self.assertEqual([(r, pid) for _, r, pid in pairs],
                         [(1, "t1-r1"), (2, "t1-r2"), (3, "t1-r3")])

    def test_artifact_paths_distinct_per_repeat(self):
        out = Path("/x")
        self.assertNotEqual(run_mod.consumer_file(out, "t1-r1", "cold"),
                            run_mod.consumer_file(out, "t1-r2", "cold"))
        self.assertNotEqual(
            run_mod.judge_file(out, "t1-r1", "claude-sonnet-5"),
            run_mod.judge_file(out, "t1-r2", "claude-sonnet-5"),
        )
        self.assertNotEqual(run_mod.adjudication_file(out, "t1-r1"),
                            run_mod.adjudication_file(out, "t1-r2"))


class RepeatIsolationTest(unittest.TestCase):
    def test_each_repeat_stages_its_own_workspace(self):
        task = {"id": "t1", "skill": "cat/s", "fixture": "fx", "prompt": "p"}
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            built = tmp / "built"
            built.mkdir()
            (built / "file.txt").write_text("payload", encoding="utf-8")
            ws1 = run_mod.stage_arm_workspace(built, tmp / "work",
                                              "t1-r1", "cold", task)
            ws2 = run_mod.stage_arm_workspace(built, tmp / "work",
                                              "t1-r2", "cold", task)
            self.assertNotEqual(ws1, ws2)
            for ws in (ws1, ws2):
                self.assertTrue((ws / "file.txt").is_file())
                # Cold-arm isolation holds per repeat.
                self.assertFalse((ws / ".claude").exists())

    def test_consumer_command_carries_no_session_state(self):
        # No shared session state across repeats: every invocation is a
        # fresh headless -p run with no resume/continue/session flags.
        cmd = consumer.build_command("prompt", "sonnet",
                                     extra_args=("--allowedTools", "Read"),
                                     effort="low")
        for banned in ("--resume", "--continue", "--session-id", "-c", "-r"):
            self.assertNotIn(banned, cmd)
        self.assertIn("-p", cmd)


def _meta(repeats):
    return {
        "run_id": "20260710T000000Z-rep-test",
        "model": "claude-fable-5",
        "effort": "low",
        "judge_model": "sonnet",
        "seed": 7,
        "repeats": repeats,
        "judge_repeats": 1,
        "preregistered": True,
        "excluded_tasks": [],
        "tasks": {
            "t1": {"skill": "cat/skill-x", "fixture": "fx",
                   "must_hit_ids": ["a", "b"]},
            "t2": {"skill": "cat/skill-x", "fixture": "fx",
                   "must_hit_ids": ["a", "b"]},
        },
    }


def _outputs_two_repeats():
    # r1: t1 cold 1/2 loaded 2/2, t2 cold 0/2 loaded 2/2
    #     -> cold 25%, loaded 100%, delta +75.0
    # r2: t1 cold 1/2 loaded 1/2, t2 cold 1/2 loaded 2/2
    #     -> cold 50%, loaded 75%, delta +25.0
    return {
        "t1-r1": [_judgment([True, False], [True, True], ["a", "b"])],
        "t2-r1": [_judgment([False, False], [True, True], ["a", "b"])],
        "t1-r2": [_judgment([True, False], [True, False], ["a", "b"])],
        "t2-r2": [_judgment([False, True], [True, True], ["a", "b"])],
    }


def _order_key():
    return {"seed": 7, "order": {
        pid: dict(ORDER)
        for pid in ("t1-r1", "t1-r2", "t2-r1", "t2-r2")
    }}


class RepeatsDetailScoringTest(unittest.TestCase):
    def test_per_repeat_values_retained_and_mean_computed(self):
        scores = scoring.score_run(_meta(2), _outputs_two_repeats(),
                                   _order_key())
        detail = scores["repeats_detail"]
        r1 = detail["per_repeat"]["r1"]
        self.assertEqual((r1["cold_hits"], r1["loaded_hits"],
                          r1["n_expectations"]), (1, 4, 4))
        self.assertEqual(r1["cold_rate_pct"], 25.0)
        self.assertEqual(r1["delta_pp"], 75.0)
        r2 = detail["per_repeat"]["r2"]
        self.assertEqual(r2["cold_rate_pct"], 50.0)
        self.assertEqual(r2["delta_pp"], 25.0)
        # Task-level repeat values retained too.
        self.assertEqual(r1["tasks"]["t2"],
                         {"n_must_hits": 2, "cold_hits": 0, "loaded_hits": 2})
        mean = detail["mean_over_repeats"]
        self.assertEqual(mean["cold_rate_pct"], 37.5)
        self.assertEqual(mean["loaded_rate_pct"], 87.5)
        self.assertEqual(mean["delta_pp"], 50.0)
        self.assertIn("no", detail["note"])
        self.assertIn("shared session state", detail["note"])

    def test_single_run_scores_carry_no_repeats_detail(self):
        outputs = {
            "t1": [_judgment([True, False], [True, True], ["a", "b"])],
            "t2": [_judgment([False, False], [True, True], ["a", "b"])],
        }
        order = {"seed": 7, "order": {"t1": dict(ORDER), "t2": dict(ORDER)}}
        scores = scoring.score_run(_meta(1), outputs, order)
        self.assertNotIn("repeats_detail", scores)

    def test_report_renders_repeat_table_and_mean(self):
        with tempfile.TemporaryDirectory() as root:
            run_dir = Path(root) / "rep-run"
            (run_dir / "judge-outputs").mkdir(parents=True)
            (run_dir / "run-meta.json").write_text(
                json.dumps(_meta(2), indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            (run_dir / "order-key.json").write_text(
                json.dumps(_order_key(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            for pid, j in _outputs_two_repeats().items():
                (run_dir / "judge-outputs" / f"{pid}.json").write_text(
                    json.dumps({"pair": pid, "judgments": j},
                               indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
            _, report_text = report.recompute(run_dir)
        self.assertIn("Repeat-level aggregates (replicated cell", report_text)
        self.assertIn("| r1 | 1/4 (25.0%) | 4/4 (100.0%) | +75.0 |",
                      report_text)
        self.assertIn("| r2 | 2/4 (50.0%) | 3/4 (75.0%) | +25.0 |",
                      report_text)
        self.assertIn(
            "Endpoint mean over repeats: cold 37.5% | loaded 87.5% | "
            "delta +50.0 pp.", report_text)


def _write_cell(root, name, model, effort, outputs, meta):
    run_dir = Path(root) / name
    (run_dir / "judge-outputs").mkdir(parents=True)
    meta = dict(meta, run_id=name, model=model, effort=effort)
    (run_dir / "run-meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    order = {"seed": 7, "order": {pid: dict(ORDER) for pid in outputs}}
    (run_dir / "order-key.json").write_text(
        json.dumps(order, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for pid, j in outputs.items():
        (run_dir / "judge-outputs" / f"{pid}.json").write_text(
            json.dumps({"pair": pid, "judgments": j},
                       indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir


class ReplicatedMatrixTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name
        # Replicated low endpoint (2 repeats, mean delta +50.0) and a
        # single-run max endpoint (delta +25.0).
        self.cell_low = _write_cell(
            self.root, "rep-low", "m-generic", "low",
            _outputs_two_repeats(), _meta(2))
        self.cell_max = _write_cell(
            self.root, "rep-max", "m-generic", "max",
            {"t1": [_judgment([True, False], [True, True], ["a", "b"])],
             "t2": [_judgment([True, True], [True, True], ["a", "b"])]},
            _meta(1))

    def test_cell_flags_and_mean_over_repeats(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        low = matrix["cells"]["m-generic@low"]
        self.assertTrue(low["replicated"])
        agg = low["aggregate"]
        mean = agg["mean_over_repeats"]
        self.assertEqual(mean["n_repeats"], 2)
        self.assertEqual(mean["cold_rate_pct"], 37.5)
        self.assertEqual(mean["delta_pp"], 50.0)
        # Per-repeat values retained inside the aggregate block.
        self.assertEqual(mean["per_repeat"]["r1"]["delta_pp"], 75.0)
        self.assertIn("replicated endpoint mean", agg["label"])
        mx = matrix["cells"]["m-generic@max"]
        self.assertFalse(mx["replicated"])
        self.assertNotIn("mean_over_repeats", mx["aggregate"])

    def test_render_marks_replicated_means_distinct(self):
        text = report.render_matrix(
            report.matrix_scores([self.cell_low, self.cell_max]))
        self.assertIn("**+50.0** (R2 mean)", text)
        self.assertIn("**37.5%** (R2 mean)", text)
        # Single-run cells carry no replication marker.
        self.assertNotIn("(R1 mean)", text)
        self.assertIn("Replicated endpoint cells", text)

    def test_verdicts_use_replicated_means(self):
        matrix = report.matrix_scores([self.cell_low, self.cell_max])
        h2 = matrix["hypothesis_verdicts"]["h2"]["m-generic"]
        # D(low) is the replicated mean +50.0, D(max) single-run +25.0.
        self.assertEqual(h2["delta_low_pp"], 50.0)
        self.assertEqual(h2["delta_max_pp"], 25.0)
        self.assertEqual(h2["shrinkage_pp"], 25.0)
        self.assertEqual(
            h2["verdict"],
            "directionally supported under the pre-registered rule")
        self.assertIn("replicated mean over 2 repeats", h2["basis"])


if __name__ == "__main__":
    unittest.main()
