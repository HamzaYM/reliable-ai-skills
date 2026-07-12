"""Pre-registered run-validity rules: pinned output budget with
truncation-as-invalid, cross-model fallback detection, and the stop
reason / thinking usage / effective model provenance fields."""
import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import consumer

LIMIT = consumer.CONSUMER_MAX_OUTPUT_TOKENS


def cli_out(subtype="success", iterations=(100, 200), model_usage=None,
            extra=None):
    out = {
        "subtype": subtype,
        "result": "## Answers\nfine",
        "usage": {
            "output_tokens": sum(iterations),
            "iterations": [{"type": "message", "output_tokens": n}
                           for n in iterations],
        },
        "modelUsage": model_usage if model_usage is not None
        else {"claude-sonnet-5": {"outputTokens": sum(iterations)}},
    }
    out.update(extra or {})
    return out


class OutputBudgetTest(unittest.TestCase):
    def test_pinned_value_is_the_smoke_run_ceiling(self):
        # 64000 is the maxOutputTokens the CLI reported for the committed
        # smoke run; the pin must not drift silently.
        self.assertEqual(LIMIT, 64000)

    def test_env_pins_the_ceiling(self):
        env = consumer.consumer_env(LIMIT)
        self.assertEqual(env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"], str(LIMIT))

    def test_below_limit_passes(self):
        consumer.check_truncation(cli_out(iterations=(LIMIT - 1,)), LIMIT)

    def test_peak_message_at_limit_is_invalid(self):
        with self.assertRaises(consumer.ConsumerError):
            consumer.check_truncation(cli_out(iterations=(50, LIMIT)), LIMIT)

    def test_max_tokens_stop_reason_is_invalid(self):
        out = cli_out(extra={"stop_reason": "max_tokens"})
        with self.assertRaises(consumer.ConsumerError):
            consumer.check_truncation(out, LIMIT)

    def test_run_total_above_limit_is_not_truncation(self):
        # The ceiling is per message; a multi-turn run may exceed it in
        # total without any single message being truncated.
        out = cli_out(iterations=(LIMIT - 1, LIMIT - 1))
        consumer.check_truncation(out, LIMIT)

    def test_truncation_retried_once_then_fails(self):
        calls = []

        def fake_invoke(*args, **kwargs):
            calls.append(1)
            raise consumer.ConsumerError("consumer output truncated")

        with mock.patch.object(consumer, "_invoke", fake_invoke):
            with self.assertRaises(consumer.ConsumerError):
                consumer.run_claude("p", ".", "sonnet", 5,
                                    max_output_tokens=LIMIT)
        self.assertEqual(len(calls), 2)  # one retry, then excluded-as-invalid


class StopReasonAndThinkingTest(unittest.TestCase):
    def test_explicit_stop_reason_preferred(self):
        out = cli_out(extra={"stop_reason": "end_turn"})
        self.assertEqual(consumer.stop_reason(out), "end_turn")

    def test_subtype_fallback(self):
        self.assertEqual(consumer.stop_reason(cli_out()), "success")

    def test_no_signal_is_none(self):
        self.assertIsNone(consumer.stop_reason({}))

    def test_peak_from_iterations_only(self):
        self.assertEqual(
            consumer.peak_message_output_tokens(cli_out(iterations=(3, 9, 5))), 9
        )
        # No iterations: no per-message evidence, never guess from totals.
        self.assertIsNone(consumer.peak_message_output_tokens(
            {"usage": {"output_tokens": 999999}}
        ))

    def test_thinking_usage_extracted_when_present(self):
        out = cli_out()
        out["usage"]["thinking_tokens"] = 1234
        self.assertEqual(consumer.thinking_usage(out),
                         {"thinking_tokens": 1234})

    def test_thinking_usage_none_when_absent(self):
        self.assertIsNone(consumer.thinking_usage(cli_out()))


class ModelFallbackTest(unittest.TestCase):
    def test_alias_matches_full_id(self):
        self.assertTrue(consumer.model_matches("sonnet", "claude-sonnet-5"))
        self.assertTrue(consumer.model_matches("claude-fable-5",
                                               "claude-fable-5"))

    def test_cross_model_mismatch(self):
        self.assertFalse(consumer.model_matches("claude-fable-5",
                                                "claude-sonnet-5"))

    def test_primary_model_is_top_output_producer(self):
        out = cli_out(model_usage={
            "claude-haiku-4-5": {"outputTokens": 10},
            "claude-fable-5": {"outputTokens": 900},
        })
        self.assertEqual(consumer.primary_model(out), "claude-fable-5")

    def test_fallback_is_invalid(self):
        out = cli_out(model_usage={"claude-sonnet-5": {"outputTokens": 42}})
        with self.assertRaises(consumer.ConsumerError):
            consumer.check_model_fallback(out, "claude-fable-5")

    def test_requested_model_passes_and_is_returned(self):
        out = cli_out(model_usage={"claude-fable-5": {"outputTokens": 42}})
        self.assertEqual(
            consumer.check_model_fallback(out, "claude-fable-5"),
            "claude-fable-5",
        )

    def test_no_model_usage_is_unverifiable_not_invalid(self):
        out = cli_out(model_usage={})
        self.assertIsNone(consumer.check_model_fallback(out, "sonnet"))


class RunConsumerProvenanceTest(unittest.TestCase):
    def test_result_records_budget_and_model_provenance(self):
        out = cli_out(extra={"total_cost_usd": 0.1, "duration_ms": 5,
                             "num_turns": 1, "session_id": "s"})

        with mock.patch.object(consumer, "run_claude",
                               return_value=(out, 1)) as rc:
            result = consumer.run_consumer("p", ".", "sonnet", effort="max")
        self.assertEqual(rc.call_args.kwargs["max_output_tokens"], LIMIT)
        self.assertTrue(rc.call_args.kwargs["check_model"])
        self.assertEqual(result["stop_reason"], "success")
        self.assertEqual(result["max_output_tokens"], LIMIT)
        self.assertEqual(result["model_effective"], "claude-sonnet-5")
        self.assertEqual(result["models_effective"], ["claude-sonnet-5"])
        self.assertFalse(result["model_fallback"])
        self.assertEqual(result["effort_effective"], "max")
        self.assertIsNone(result["thinking_usage"])
        self.assertEqual(result["peak_message_output_tokens"], 200)

    def test_default_effort_recorded_as_default(self):
        with mock.patch.object(consumer, "run_claude",
                               return_value=(cli_out(), 1)):
            result = consumer.run_consumer("p", ".", "sonnet")
        self.assertEqual(result["effort_effective"], "default")


if __name__ == "__main__":
    unittest.main()
