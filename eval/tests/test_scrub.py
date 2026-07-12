"""Scrubber and abort-on-leak verifier: the blinding backstops."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import scrub

SKILL_REL = "change-control/git-change-control-for-agents"
SKILL_NAME = "git-change-control-for-agents"
PATTERNS = scrub.banned_patterns(SKILL_REL, SKILL_NAME)


class ScrubLeakCasesTest(unittest.TestCase):
    def _scrub(self, text):
        return scrub.scrub_text(text, PATTERNS)

    def test_full_skill_path_is_scrubbed(self):
        out, subs = self._scrub(
            "I followed .claude/skills/git-change-control-for-agents/SKILL.md here."
        )
        self.assertEqual(out, "I followed project documentation here.")
        self.assertEqual(len(subs), 1)

    def test_bare_skill_md_reference(self):
        out, _ = self._scrub("Per SKILL.md, verify state first.")
        self.assertEqual(out, "Per project documentation, verify state first.")

    def test_repo_style_skill_path(self):
        out, _ = self._scrub(f"See skills/{SKILL_REL}/SKILL.md for details.")
        self.assertNotIn("SKILL.md", out)
        self.assertNotIn(SKILL_NAME, out)
        self.assertIn("project documentation", out)

    def test_name_variants(self):
        for variant in (
            "git-change-control-for-agents",
            "Git-Change-Control-For-Agents",
            "git change control for agents",
            "git_change_control_for_agents",
        ):
            out, subs = self._scrub(f"Guided by the {variant} approach.")
            self.assertNotIn("change control", out.lower().replace("-", " ").replace("_", " "))
            self.assertIn("project documentation", out)
            self.assertEqual(len(subs), 1, variant)

    def test_mixed_separator_and_concatenated_name_echoes(self):
        # Echoes that mix separators or drop them entirely must still be
        # scrubbed; literal-variant matching missed these.
        for variant in (
            "git change-control for agents",
            "git_change-control for_agents",
            "gitchangecontrolforagents",
            "git-change-control_for agents",
        ):
            out, subs = self._scrub(f"Guided by the {variant} approach.")
            self.assertIn("project documentation", out)
            self.assertEqual(len(subs), 1, variant)
            self.assertEqual(scrub.verify_no_leak(out, PATTERNS), [], variant)

    def test_generic_phrases(self):
        out, _ = self._scrub("The skill says X. Per this skill, do Y. The skill file helps.")
        lowered = out.lower()
        self.assertNotIn("the skill ", lowered.replace("project documentation", ""))
        self.assertIn("project documentation", out)

    def test_substitutions_are_logged_with_offsets(self):
        text = "Start. SKILL.md mid. End."
        out, subs = self._scrub(text)
        self.assertEqual(len(subs), 1)
        sub = subs[0]
        self.assertEqual(sub["original"], "SKILL.md")
        self.assertEqual(sub["replacement"], "project documentation")
        self.assertEqual(sub["offset"], text.index("SKILL.md"))

    def test_bare_skill_mentions_are_scrubbed(self):
        for text in (
            "A skill was provided in the workspace, so I applied it.",
            "Per the bundled skill's guidance, verify state first.",
            "The skills documentation says to fetch before branching.",
        ):
            out, subs = self._scrub(text)
            self.assertNotRegex(out.lower(), r"\bskills?\b", text)
            self.assertTrue(subs, text)
            self.assertEqual(scrub.verify_no_leak(out, PATTERNS), [], text)

    def test_condition_words_are_scrubbed_not_fatal(self):
        # Innocent vocabulary ("cold cache", "the baseline branch") must be
        # neutralized symmetrically, never left to wedge the run.
        out, subs = self._scrub("The cold cache and the baseline branch look fine.")
        self.assertEqual(scrub.verify_no_leak(out, PATTERNS), [])
        self.assertEqual(len(subs), 2)

    def test_clean_text_untouched(self):
        text = "Local main is behind origin/main; branch from origin/main."
        out, subs = self._scrub(text)
        self.assertEqual(out, text)
        self.assertEqual(subs, [])

    def test_replacement_is_not_a_marker(self):
        # The replacement phrase must not itself trip the verifier.
        out, _ = self._scrub("Read SKILL.md first.")
        self.assertEqual(scrub.verify_no_leak(out, PATTERNS), [])


class CrossSkillNameTest(unittest.TestCase):
    # A staged skill's SKILL.md may cite a sibling skill by name; a consumer
    # that quotes that cross-reference leaks the loaded arm just as plainly
    # as an echo of its own skill name. Task-scoped banning missed these.
    ROSTER = ("config-and-secrets-hygiene", "ai-cost-tracking-and-guardrails",
              "git-change-control-for-agents")
    PATS = scrub.banned_patterns(SKILL_REL, SKILL_NAME, ROSTER)

    def _scrub(self, text):
        return scrub.scrub_text(text, self.PATS)

    def test_sibling_name_is_scrubbed(self):
        # The real committed leak: a task for one skill quoting another.
        out, subs = self._scrub(
            "see the config-and-secrets-hygiene project documentation for why"
        )
        self.assertNotIn("config-and-secrets-hygiene", out)
        self.assertIn("project documentation", out)
        self.assertTrue(subs)
        self.assertEqual(scrub.verify_no_leak(out, self.PATS), [])

    def test_sibling_name_separator_variants(self):
        for variant in (
            "config-and-secrets-hygiene",
            "config and secrets hygiene",
            "config_and-secrets hygiene",
            "configandsecretshygiene",
            "Config-And-Secrets-Hygiene",
        ):
            out, subs = self._scrub(f"Quoting the {variant} reference here.")
            self.assertIn("project documentation", out)
            self.assertEqual(len(subs), 1, variant)
            self.assertEqual(scrub.verify_no_leak(out, self.PATS), [], variant)

    def test_verifier_catches_unscrubbed_sibling(self):
        hits = scrub.verify_no_leak(
            "The ai-cost-tracking-and-guardrails reference says so.", self.PATS
        )
        self.assertTrue(hits)

    def test_task_scoped_list_leaves_sibling(self):
        # Regression witness: without the roster the sibling survives both
        # scrub and verify (this is exactly how the committed leak happened).
        task_only = scrub.banned_patterns(SKILL_REL, SKILL_NAME)
        out, _ = scrub.scrub_text(
            "see the config-and-secrets-hygiene project documentation", task_only
        )
        self.assertIn("config-and-secrets-hygiene", out)
        self.assertEqual(scrub.verify_no_leak(out, task_only), [])


class VerifierTest(unittest.TestCase):
    def test_clean_input_passes(self):
        self.assertEqual(
            scrub.verify_no_leak("Fetch origin, compare refs, cut a branch.", PATTERNS),
            [],
        )

    def test_condition_words_abort(self):
        for word in ("cold", "loaded", "arm", "baseline", "treatment",
                     "skill", "skills", "Cold", "LOADED", "Skill"):
            hits = scrub.verify_no_leak(f"the {word} report", PATTERNS)
            self.assertTrue(hits, word)
            self.assertTrue(any(h["pattern"] == "condition-word" for h in hits), word)

    def test_no_false_positive_on_substrings(self):
        for text in ("downloaded data", "harmless charm", "armchair review",
                     "reloaded gracefully", "colder weather", "skillful work"):
            self.assertEqual(scrub.verify_no_leak(text, PATTERNS), [], text)

    def test_skill_tokens_abort(self):
        hits = scrub.verify_no_leak(
            "It cites .claude/skills/x/SKILL.md directly.", PATTERNS
        )
        self.assertTrue(hits)

    def test_prompt_prefix_fragment_aborts(self):
        hits = scrub.verify_no_leak(
            "Before starting, read the documentation.", PATTERNS
        )
        self.assertTrue(any(h["pattern"] == "prompt-prefix" for h in hits))

    def test_hits_carry_offset_and_snippet(self):
        text = "x" * 50 + " SKILL.md " + "y" * 50
        hits = scrub.verify_no_leak(text, PATTERNS)
        self.assertEqual(hits[0]["offset"], 51)
        self.assertIn("SKILL.md", hits[0]["snippet"])


if __name__ == "__main__":
    unittest.main()
