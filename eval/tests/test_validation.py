"""Reference validation, judge shape checks, and tree-hash blind spots."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import fixtures, judge
from harness import tasks as tasks_mod

VALID_TASK = {
    "id": "t-one",
    "skill": "change-control/git-change-control-for-agents",
    "fixture": "_example",
    "prompt": "Inspect the repository and report.",
    "must_hits": [{"id": "a", "text": "Alpha."}, {"id": "b", "text": "Beta."}],
}


class RefPathTest(unittest.TestCase):
    def test_valid_refs_pass(self):
        self.assertEqual(tasks_mod.validate_task(VALID_TASK), [])

    def test_traversal_refs_rejected(self):
        for field, value in (
            ("skill", "../eval"),
            ("skill", "x/.."),
            ("skill", "/etc"),
            ("skill", "cat//skill"),
            ("fixture", "../../"),
            ("fixture", ".."),
            ("fixture", "a/b"),
        ):
            task = dict(VALID_TASK, **{field: value})
            errs = tasks_mod.validate_task(task)
            self.assertTrue(errs, f"{field}={value!r} passed validation")

    def test_underscore_and_dots_allowed(self):
        task = dict(VALID_TASK, fixture="_example", skill="a1/b-2.c_3")
        self.assertEqual(tasks_mod.validate_task(task), [])


class DuplicateExpectationTest(unittest.TestCase):
    def _judgment(self, ids):
        return {
            "expectations": [
                {"expectation_id": i,
                 "report_1": {"hit": True, "evidence": "q"},
                 "report_2": {"hit": False, "evidence": ""}}
                for i in ids
            ],
            "comparative_verdict": "x",
        }

    def test_duplicate_expectation_rejected(self):
        with self.assertRaises(judge.JudgeError):
            judge.validate_judgment(self._judgment(["a", "a"]), ["a"])

    def test_unique_expectations_pass(self):
        judge.validate_judgment(self._judgment(["a", "b"]), ["a", "b"])


class JudgeSchemaCliContractTest(unittest.TestCase):
    """claude CLI 2.1.x requires --json-schema as inline JSON and rejects a
    top-level "$schema" key; the payload judge.py sends must satisfy both,
    or every judge run dies at the CLI while unit tests stay green."""

    def test_cli_payload_is_inline_json_without_schema_key(self):
        payload = judge.schema_for_cli()
        data = json.loads(payload)  # inline JSON, never a file path
        self.assertNotIn("$schema", data)
        self.assertEqual(data.get("type"), "object")
        self.assertIn("expectations", data.get("properties", {}))

    def test_schema_file_keeps_documentation_key(self):
        data = json.loads(judge.judge_schema_path().read_text(encoding="utf-8"))
        self.assertIn("$schema", data)


class TreeHashBlindSpotTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "file.txt").write_text("content", encoding="utf-8")

    def test_fake_git_dir_is_hashed(self):
        # A plain directory merely named *.git is NOT a git internal and
        # must be visible to the hash.
        before = fixtures.tree_hash(self.root)
        payload = self.root / "data.git"
        payload.mkdir()
        (payload / "sneaky.txt").write_text("x", encoding="utf-8")
        after = fixtures.tree_hash(self.root)
        self.assertNotEqual(before, after)
        (payload / "sneaky.txt").write_text("y", encoding="utf-8")
        self.assertNotEqual(after, fixtures.tree_hash(self.root))

    def test_real_bare_repo_is_excluded(self):
        bare = self.root / "origin.git"
        (bare / "objects").mkdir(parents=True)
        (bare / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        before = fixtures.tree_hash(self.root)
        (bare / "objects" / "pack").mkdir()
        self.assertEqual(before, fixtures.tree_hash(self.root))

    def test_dot_git_dir_is_excluded(self):
        internal = self.root / ".git"
        internal.mkdir()
        before = fixtures.tree_hash(self.root)
        (internal / "index").write_text("x", encoding="utf-8")
        self.assertEqual(before, fixtures.tree_hash(self.root))

    def test_symlink_retarget_changes_hash(self):
        (self.root / "other.txt").write_text("other", encoding="utf-8")
        link = self.root / "link.txt"
        os.symlink("file.txt", link)
        before = fixtures.tree_hash(self.root)
        link.unlink()
        os.symlink("other.txt", link)
        self.assertNotEqual(before, fixtures.tree_hash(self.root))


if __name__ == "__main__":
    unittest.main()
