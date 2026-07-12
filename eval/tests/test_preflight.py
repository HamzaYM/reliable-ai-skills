"""Staged-skill frontmatter preflight and cold-arm isolation."""
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_mod
from harness import consumer, fixtures
from harness import tasks as tasks_mod


def write_skill(root, skill, frontmatter_lines):
    d = root / skill
    d.mkdir(parents=True)
    body = "---\n" + "\n".join(frontmatter_lines) + "\n---\n\nBody text.\n"
    (d / "SKILL.md").write_text(body, encoding="utf-8")


class FrontmatterPreflightTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _tasks(self, skill="cat/clean-skill"):
        return [{"id": "t1", "skill": skill, "fixture": "fx",
                 "prompt": "p", "must_hits": [{"id": "a", "text": "x"}]}]

    def test_clean_skill_passes(self):
        write_skill(self.root, "cat/clean-skill",
                    ["name: clean-skill", "description: fine"])
        self.assertEqual(
            tasks_mod.skill_frontmatter_preflight(self._tasks(), self.root), []
        )

    def test_each_forbidden_key_aborts(self):
        for key in tasks_mod.FORBIDDEN_SKILL_FRONTMATTER_KEYS:
            with self.subTest(key=key):
                root = self.root / key
                write_skill(root, "cat/bad-skill",
                            ["name: bad-skill", "description: d",
                             f"{key}: something"])
                errs = tasks_mod.skill_frontmatter_preflight(
                    self._tasks("cat/bad-skill"), root
                )
                self.assertEqual(len(errs), 1)
                self.assertIn(repr(key), errs[0])

    def test_forbidden_word_in_body_is_fine(self):
        write_skill(self.root, "cat/body-skill",
                    ["name: body-skill", "description: d"])
        p = self.root / "cat/body-skill" / "SKILL.md"
        p.write_text(p.read_text(encoding="utf-8")
                     + "\nmodel: mentioned in the body, not frontmatter\n",
                     encoding="utf-8")
        self.assertEqual(
            tasks_mod.skill_frontmatter_preflight(
                self._tasks("cat/body-skill"), self.root
            ),
            [],
        )

    def test_key_as_substring_of_another_key_is_fine(self):
        write_skill(self.root, "cat/sub-skill",
                    ["name: sub-skill", "description: d",
                     "modeling-notes: not the model key"])
        self.assertEqual(
            tasks_mod.skill_frontmatter_preflight(
                self._tasks("cat/sub-skill"), self.root
            ),
            [],
        )


class ColdArmIsolationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.built = self.root / "built"
        self.built.mkdir()
        (self.built / "README.md").write_text("fixture\n", encoding="utf-8")
        self.task = {
            "id": "t1",
            "skill": "change-control/git-change-control-for-agents",
            "fixture": "fx",
        }

    def test_clean_cold_workspace_stages(self):
        ws = run_mod.stage_arm_workspace(
            self.built, self.root / "work", "t1", "cold", self.task
        )
        self.assertTrue((ws / "README.md").is_file())
        self.assertFalse((ws / ".claude").exists())

    def test_cold_workspace_with_claude_dir_aborts(self):
        # If a fixture (or any earlier step) smuggled a .claude directory
        # into the template, the cold arm is not isolated: hard error.
        (self.built / ".claude" / "skills" / "stray").mkdir(parents=True)
        with self.assertRaises(fixtures.FixtureError):
            run_mod.stage_arm_workspace(
                self.built, self.root / "work2", "t1", "cold", self.task
            )

    def test_loaded_workspace_gets_exactly_the_staged_skill(self):
        ws = run_mod.stage_arm_workspace(
            self.built, self.root / "work3", "t1", "loaded", self.task
        )
        skill_dir = ws / ".claude" / "skills" / \
            "git-change-control-for-agents"
        self.assertTrue((skill_dir / "SKILL.md").is_file())

    def test_consumer_toolset_has_no_skill_tool(self):
        # User/project-level skills are invocable only through the Skill
        # tool; the consumer allowlist must never include it.
        tools = consumer.ALLOWED_TOOLS.split(",")
        self.assertNotIn("Skill", tools)
        self.assertEqual(tools, ["Read", "Grep", "Glob", "Bash"])


class AmbientUserSkillsTest(unittest.TestCase):
    def test_lists_skill_dirs_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "some-skill").mkdir()
            (root / "another").mkdir()
            (root / "loose-file.md").write_text("x", encoding="utf-8")
            self.assertEqual(consumer.ambient_user_skills(root),
                             ["another", "some-skill"])

    def test_missing_dir_is_empty(self):
        self.assertEqual(
            consumer.ambient_user_skills("/nonexistent/path/skills"), []
        )


class AnswerLengthRecordingTest(unittest.TestCase):
    def test_run_one_consumer_records_answer_chars(self):
        answers = "the concrete answer body"
        fake_result = {
            "report": f"## Actions\ndid things\n\n## Answers\n{answers}",
            "attempts": 1,
        }
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            built = tmp / "built"
            built.mkdir()
            job = ({"id": "t1", "skill": "cat/s", "fixture": "fx",
                    "prompt": "p"},
                   "t1", 1, "cold", built, {"snap": 1}, tmp / "work",
                   "persona", "sonnet", "max")
            with mock.patch.object(run_mod.fixtures_mod, "snapshot",
                                   return_value={"snap": 1}), \
                 mock.patch.object(run_mod, "stage_arm_workspace",
                                   return_value=tmp / "ws"), \
                 mock.patch.object(run_mod.consumer_mod, "run_consumer",
                                   return_value=dict(fake_result)):
                pid, arm, result = run_mod.run_one_consumer(job)
        self.assertEqual((pid, arm), ("t1", "cold"))
        self.assertEqual(result["answer_chars"], len(answers))
        self.assertEqual(result["effort_requested"], "max")


if __name__ == "__main__":
    unittest.main()
