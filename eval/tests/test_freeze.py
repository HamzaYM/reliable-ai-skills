"""Freeze write/verify: pre-registration must be tamper-evident."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import freeze
from harness import tasks as tasks_mod

TASK_LINE = {
    "id": "t-one",
    "skill": "change-control/git-change-control-for-agents",
    "fixture": "_example",
    "prompt": "Inspect the repository and report.",
    "must_hits": [{"id": "a", "text": "Alpha."}, {"id": "b", "text": "Beta."}],
}


def _write_tasks(dirpath, lines):
    path = Path(dirpath) / "suite.jsonl"
    path.write_text(
        "\n".join(json.dumps(l) for l in lines) + "\n", encoding="utf-8"
    )
    return path


class FreezeRoundTripTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = _write_tasks(self._tmp.name, [TASK_LINE])
        self.tasks = tasks_mod.load_tasks(self.path)

    def test_missing_freeze_is_reported(self):
        errs = freeze.verify_freeze(self.path, self.tasks)
        self.assertEqual(len(errs), 1)
        self.assertIn("no freeze file", errs[0])

    def test_write_then_verify_clean(self):
        fpath, data = freeze.write_freeze(self.path, self.tasks)
        self.assertTrue(fpath.name.endswith(".freeze.json"))
        self.assertEqual(data["counts"], {"tasks": 1, "must_hits": 2})
        self.assertIn("_example", data["fixtures"])
        self.assertEqual(freeze.verify_freeze(self.path, self.tasks), [])

    def test_task_file_tamper_detected(self):
        freeze.write_freeze(self.path, self.tasks)
        self.path.write_text(
            self.path.read_text(encoding="utf-8") + "\n", encoding="utf-8"
        )
        errs = freeze.verify_freeze(self.path, tasks_mod.load_tasks(self.path))
        self.assertTrue(any("task file hash changed" in e for e in errs))

    def test_must_hit_edit_detected_per_task(self):
        freeze.write_freeze(self.path, self.tasks)
        edited = dict(TASK_LINE)
        edited["must_hits"] = [
            {"id": "a", "text": "Alpha, weakened."},
            {"id": "b", "text": "Beta."},
        ]
        new_path = _write_tasks(self._tmp.name, [edited])
        errs = freeze.verify_freeze(new_path, tasks_mod.load_tasks(new_path))
        self.assertTrue(any("t-one edited since freeze" in e for e in errs))

    def test_added_task_detected(self):
        freeze.write_freeze(self.path, self.tasks)
        extra = dict(TASK_LINE, id="t-two")
        new_path = _write_tasks(self._tmp.name, [TASK_LINE, extra])
        errs = freeze.verify_freeze(new_path, tasks_mod.load_tasks(new_path))
        self.assertTrue(any("t-two not present in freeze" in e for e in errs))

    def test_removed_task_detected(self):
        two = dict(TASK_LINE, id="t-two")
        path = _write_tasks(self._tmp.name, [TASK_LINE, two])
        tasks = tasks_mod.load_tasks(path)
        freeze.write_freeze(path, tasks)
        new_path = _write_tasks(self._tmp.name, [TASK_LINE])
        errs = freeze.verify_freeze(new_path, tasks_mod.load_tasks(new_path))
        self.assertTrue(any("t-two was frozen but is missing" in e for e in errs))

    def test_instruments_are_frozen(self):
        _, data = freeze.write_freeze(self.path, self.tasks)
        self.assertIn("agents/judge-prompt.md", data["instruments"])
        self.assertIn("schemas/judge.schema.json", data["instruments"])

    def test_instrument_tamper_detected(self):
        fpath, _ = freeze.write_freeze(self.path, self.tasks)
        data = json.loads(fpath.read_text(encoding="utf-8"))
        data["instruments"]["agents/judge-prompt.md"] = "0" * 64
        fpath.write_text(json.dumps(data) + "\n", encoding="utf-8")
        errs = freeze.verify_freeze(self.path, self.tasks)
        self.assertTrue(
            any("instrument agents/judge-prompt.md changed" in e for e in errs)
        )

    def test_freeze_without_instruments_rejected(self):
        fpath, _ = freeze.write_freeze(self.path, self.tasks)
        data = json.loads(fpath.read_text(encoding="utf-8"))
        del data["instruments"]
        fpath.write_text(json.dumps(data) + "\n", encoding="utf-8")
        errs = freeze.verify_freeze(self.path, self.tasks)
        self.assertTrue(any("no instrument hashes" in e for e in errs))


class CanonicalHashTest(unittest.TestCase):
    def test_key_order_does_not_matter(self):
        a = {"id": "x", "prompt": "p"}
        b = {"prompt": "p", "id": "x"}
        self.assertEqual(tasks_mod.task_hash(a), tasks_mod.task_hash(b))

    def test_content_change_changes_hash(self):
        a = {"id": "x", "prompt": "p"}
        b = {"id": "x", "prompt": "q"}
        self.assertNotEqual(tasks_mod.task_hash(a), tasks_mod.task_hash(b))


if __name__ == "__main__":
    unittest.main()
