"""Effort pass-through: fail-closed verification, warning detection,
command construction, cell naming, and run-meta/report provenance."""
import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import run as run_mod
from harness import consumer

# Verbatim shape of `claude --help` on 2.1.206 (the discovered mechanism).
HELP_WITH_EFFORT = """\
  --disallowedTools, --disallowed-tools <tools...>
  --effort <level>                      Effort level for the current session
                                        (low, medium, high, xhigh, max)
  --exclude-dynamic-system-prompt-sections
"""

HELP_WITHOUT_EFFORT = """\
  --model <model>                       Model for the current session.
  --output-format <format>              Output format (only works with --print)
"""

# Verbatim warning observed live on 2.1.206: the CLI does NOT fail on a bad
# effort value; it warns and silently runs at the default effort.
CLI_WARNING = (
    "Warning: Unknown --effort value 'bogus' — ignoring it and using the "
    "default effort. Valid values: low, medium, high, xhigh, max."
)


class ParseEffortHelpTest(unittest.TestCase):
    def test_levels_and_snippet_extracted(self):
        levels, snippet = consumer.parse_effort_help(HELP_WITH_EFFORT)
        self.assertEqual(levels, ["low", "medium", "high", "xhigh", "max"])
        self.assertIn("--effort <level>", snippet)
        self.assertIn("(low, medium, high, xhigh, max)", snippet)

    def test_missing_flag_fails_closed(self):
        with self.assertRaises(consumer.ConsumerError):
            consumer.parse_effort_help(HELP_WITHOUT_EFFORT)

    def test_unparseable_level_list_fails_closed(self):
        with self.assertRaises(consumer.ConsumerError):
            consumer.parse_effort_help("  --effort <level>   Effort level\n")


class VerifyEffortSupportTest(unittest.TestCase):
    def test_advertised_level_accepted_with_evidence(self):
        evidence = consumer.verify_effort_support("low", HELP_WITH_EFFORT)
        self.assertEqual(
            evidence["advertised_levels"], ["low", "medium", "high", "xhigh", "max"]
        )
        self.assertIn("--effort", evidence["cli_help_evidence"])

    def test_max_level_accepted_end_to_end(self):
        # max is a first-class sweep endpoint: pre-flight accepts it with
        # evidence and the CLI command carries it through.
        evidence = consumer.verify_effort_support("max", HELP_WITH_EFFORT)
        self.assertIn("max", evidence["advertised_levels"])
        cmd = consumer.build_command("p", "claude-fable-5", effort="max")
        self.assertEqual(cmd[-2:], ["--effort", "max"])

    def test_unadvertised_level_fails_closed(self):
        with self.assertRaises(consumer.ConsumerError):
            consumer.verify_effort_support("ultrathink", HELP_WITH_EFFORT)

    def test_max_fails_closed_on_cli_without_it(self):
        help_no_max = HELP_WITH_EFFORT.replace(
            "(low, medium, high, xhigh, max)", "(low, medium, high, xhigh)"
        )
        with self.assertRaises(consumer.ConsumerError):
            consumer.verify_effort_support("max", help_no_max)

    def test_cli_without_effort_fails_closed(self):
        with self.assertRaises(consumer.ConsumerError):
            consumer.verify_effort_support("low", HELP_WITHOUT_EFFORT)


class EffortWarningTest(unittest.TestCase):
    def test_live_observed_warning_detected(self):
        self.assertEqual(consumer.effort_warning(CLI_WARNING), CLI_WARNING)

    def test_not_supported_and_env_warnings_detected(self):
        for line in (
            "Effort not supported on this model",
            "Not applied: CLAUDE_CODE_EFFORT_LEVEL=weird",
            "model x has invalid effort 'y'",
        ):
            self.assertIsNotNone(consumer.effort_warning(line), line)

    def test_benign_stderr_passes(self):
        for text in (None, "", "some unrelated warning\nanother line"):
            self.assertIsNone(consumer.effort_warning(text))


class BuildCommandTest(unittest.TestCase):
    def test_effort_flag_appended_when_set(self):
        cmd = consumer.build_command("p", "claude-fable-5", ("--x", "y"),
                                     effort="low")
        self.assertEqual(cmd[-2:], ["--effort", "low"])
        self.assertIn("--x", cmd)

    def test_no_effort_flag_by_default(self):
        cmd = consumer.build_command("p", "sonnet")
        self.assertNotIn("--effort", cmd)


class CellSlugTest(unittest.TestCase):
    def test_model_and_effort_in_run_id(self):
        self.assertEqual(run_mod.cell_slug("claude-fable-5", "low"),
                         "claude-fable-5-low")

    def test_default_effort_labelled(self):
        self.assertEqual(run_mod.cell_slug("sonnet", None), "sonnet-default")

    def test_unsafe_model_characters_sanitized(self):
        self.assertEqual(run_mod.cell_slug("org/model:v1", "xhigh"),
                         "org-model-v1-xhigh")


class EffortInvariantModelTest(unittest.TestCase):
    def test_haiku_class_is_invariant(self):
        for model in ("haiku", "claude-haiku-4-5-20251001", "Claude-Haiku"):
            self.assertTrue(consumer.effort_invariant_model(model), model)

    def test_effortful_models_are_not(self):
        for model in ("sonnet", "opus", "claude-fable-5", "claude-sonnet-5"):
            self.assertFalse(consumer.effort_invariant_model(model), model)


class EnumerateEffortSupportTest(unittest.TestCase):
    def test_effortful_model_gets_the_advertised_levels(self):
        record = consumer.enumerate_effort_support(
            "claude-fable-5", HELP_WITH_EFFORT
        )
        self.assertEqual(record["supported_levels"],
                         ["low", "medium", "high", "xhigh", "max"])
        self.assertEqual(record["cli_advertised_levels"],
                         record["supported_levels"])
        self.assertFalse(record["effort_invariant"])
        self.assertIn("--effort", record["cli_help_evidence"])
        self.assertIn("fail closed", record["probe"])
        self.assertIn("authoritative", record["detected_default"]["note"])
        self.assertIn("env_CLAUDE_CODE_EFFORT_LEVEL", record["detected_default"])

    def test_invariant_model_supports_no_levels(self):
        record = consumer.enumerate_effort_support("haiku", HELP_WITH_EFFORT)
        self.assertTrue(record["effort_invariant"])
        self.assertEqual(record["supported_levels"], [])
        # The CLI still advertises the global list; the model just cannot
        # verifiably take any of it.
        self.assertEqual(record["cli_advertised_levels"],
                         ["low", "medium", "high", "xhigh", "max"])
        self.assertIn("unavailable by design", record["probe"])
        self.assertIn("none", record["detected_default"]["note"])

    def test_cli_without_effort_enumerates_empty_without_raising(self):
        record = consumer.enumerate_effort_support(
            "claude-fable-5", HELP_WITHOUT_EFFORT
        )
        self.assertEqual(record["cli_advertised_levels"], [])
        self.assertEqual(record["supported_levels"], [])


class EffortLabelTest(unittest.TestCase):
    def test_explicit_level_records_as_itself(self):
        self.assertEqual(run_mod.effort_label("claude-fable-5", "max"), "max")

    def test_default_for_effortful_models(self):
        self.assertEqual(run_mod.effort_label("sonnet", None), "default")

    def test_none_for_invariant_models(self):
        self.assertEqual(run_mod.effort_label("haiku", None), "none")
        self.assertEqual(
            run_mod.effort_label("claude-haiku-4-5-20251001", None), "none"
        )

    def test_cell_slug_carries_the_none_label(self):
        self.assertEqual(run_mod.cell_slug("haiku", None), "haiku-none")


class UnavailableByDesignTest(unittest.TestCase):
    def test_invariant_model_with_effort_is_unavailable(self):
        reason = run_mod.unavailable_by_design("haiku", "medium")
        self.assertIsNotNone(reason)
        self.assertIn("unavailable by design", reason)
        self.assertIn("without any warning", reason)

    def test_effortful_combinations_are_available(self):
        self.assertIsNone(run_mod.unavailable_by_design("sonnet", "max"))
        self.assertIsNone(run_mod.unavailable_by_design("haiku", None))

    def test_record_written_for_audit(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(run_mod, "RESULTS_DIR", Path(tmp)):
                path = run_mod.record_unavailable_cell(
                    "haiku", "medium",
                    run_mod.unavailable_by_design("haiku", "medium"),
                )
            self.assertEqual(path.name, "haiku-medium.json")
            data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "unavailable-by-design")
        self.assertEqual(data["model"], "haiku")
        self.assertEqual(data["effort"], "medium")
        self.assertIn("unavailable by design", data["reason"])
        self.assertIn("recorded_at", data)


class AmbientEffortSourcesTest(unittest.TestCase):
    def test_env_var_recorded(self):
        with mock.patch.dict("os.environ",
                             {"CLAUDE_CODE_EFFORT_LEVEL": "high"}):
            sources = consumer.ambient_effort_sources()
        self.assertEqual(sources["env_CLAUDE_CODE_EFFORT_LEVEL"], "high")
        self.assertIn("user_settings_effortLevel", sources)

    def test_absent_env_var_recorded_as_none(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            sources = consumer.ambient_effort_sources()
        self.assertIsNone(sources["env_CLAUDE_CODE_EFFORT_LEVEL"])


if __name__ == "__main__":
    unittest.main()
