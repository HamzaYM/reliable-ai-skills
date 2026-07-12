---
name: llm-eval-harness-and-scoring-pipeline
description: "Use when building or changing a pipeline that scores, grades, or extracts structured output from an LLM in production: composite/aggregate scoring math, partial-failure handling when one sub-call fails, prompt versioning, an eval harness that makes real model calls, or comparing a candidate model/prompt against production without flipping it live."
---

# LLM eval harness and scoring pipeline

Any pipeline that turns LLM output into a number or a structured decision (a grade, a rank, a composite score) needs three things most first drafts skip: locked-down math that can't silently drift, an explicit policy for what happens when part of the pipeline fails, and a way to measure quality changes before they ship. This skill covers all three, plus the shadow-comparison technique for testing changes safely.

## Lock the aggregation math, and gate changes on it explicitly

Whatever formula turns multiple sub-scores into one number (a mean, a weighted composite, a rank with a tie-breaking rule) should be written down as an explicit, versioned contract: not just "whatever the code currently does." Once real scores exist that people compare over time, changing this math retroactively changes the meaning of every past score. Treat any change to it as requiring the same sign-off as a database migration: explicit, documented, and updated in one commit alongside whichever doc is the source of truth for it.

## Partial failure: degrade, never silently substitute

The most expensive bug class in a multi-call scoring pipeline is emitting a comparable-looking number that quietly lost an input. Concretely: if one sub-call in a multi-call scoring flow fails,

- **If the failed piece is not load-bearing for the final number** (a non-critical axis, an optional embellishment), renormalize over what succeeded and keep the result flagged as complete.
- **If the failed piece is load-bearing** (a required axis, or the piece that determines pass/fail), do not emit a number that looks comparable to a fully-scored case. Mark the result as degraded/incomplete, still show whatever partial signal you have (clearly labeled as partial), and queue the missing piece for retry.
- **If nothing scoreable survived, emit nothing.** Not a zero, not a placeholder value. A zero is a real, comparable data point; a missing score is not, and conflating them corrupts every downstream aggregate (rankings, cohort averages) that reads the number.

This matters because the alternative failure mode is silent and expensive: a partial result presented as complete has, in practice, produced real mis-rankings that only surfaced once someone noticed the underlying scores looked off.

## Version your prompts like schema migrations

Store prompts as versioned files (not inline strings), with an explicit version marker at the top of each one. Every scored/generated row should record which prompt version produced it, so that a prompt change is diffable after the fact: you can answer "which rows were scored under the old wording" without guessing. Keep old versions around rather than overwriting them; re-scoring needs to stay comparable across versions.

## Cost and concurrency controls belong next to the pipeline, not bolted on later

- **Concurrency limit on fan-out calls.** If a single unit of work triggers several parallel LLM calls, cap the fan-out with an explicit semaphore. If you start seeing rate-limit errors or timeouts under load, lower the concurrency limit first. Raising per-call timeouts just delays the same failure.
- **Retry only genuinely retryable errors** (rate limits, 5xx, timeouts) with exponential backoff; don't retry a definitive rejection (bad input, auth failure, content-policy block). That just wastes calls and, if the call carries sensitive data, can also reroute it somewhere it shouldn't go (see the cost-and-safety-guardrails skills for the full fallover-safety version of this rule).
- **Price every model you can call.** Any model string that can appear in a response needs a corresponding entry in your pricing table. An unpriced model call should never silently report as free: that blinds your cost dashboard exactly when a new/experimental model starts getting real traffic.
- **Make demo/seed data provably free.** If you seed a demo environment with synthetic scored data, run it through the real scoring code path with a deterministic stand-in for the LLM call, not a separate hand-authored shortcut. That way the seed data has the same shape and honesty as real output, costs nothing, and reruns byte-identically.

## Eval harness: real calls, opt-in, checked before every prompt change

An eval harness that makes real, costed LLM calls against a fixed set of test inputs should be deselected by default in your test runner (an explicit marker/flag), never run accidentally in a normal test pass. Run it deliberately after any prompt edit, before merging: assert on output shape and value ranges, not exact free-text content. Free text will legitimately vary between runs even with a stable prompt.

## Shadow comparison: how to test a model or prompt change safely

To answer "would a different model, prompt, or extraction strategy behave differently in production" without flipping anything live: run the candidate in parallel with the production path, on real traffic, but never let its output affect what the user sees or what state gets persisted. Concretely:

- The production path always wins and always determines behavior; the shadow path is purely observational.
- Log a structured comparison (exact-equality booleans, or a diff) between what production did and what the shadow candidate would have done, and aggregate those logs to make the go/no-go decision.
- Shadow calls should be excluded from cost caps and rate limits that apply to real traffic, and tagged distinctly in your cost ledger, since they're overhead, not user-facing work.
- Never resolve "would X behave differently" by actually flipping X on production to see what happens. That's an experiment on real users, not a test.

## When not to use this

If the question is "should this specific PR be reviewed before merge," that's the validation-gates or adversarial-review skill. This skill is about the scoring/eval pipeline's own architecture and invariants, not about reviewing a change to it.
