---
name: multi-model-adversarial-review
description: Use before merging any substantive change, or before finalizing a document, plan, or claim, when you want a genuine adversarial pass rather than the same model re-reading its own work. Applies to code diffs, PRs, architecture plans, and prose (specs, memos, claims). Not worth it for trivial one-line changes.
---

# Multi-model adversarial review

A single model reviewing its own work is not an adversarial review, even if you ask it to "be critical." One model's blind spots are usually its reviewer's blind spots too. The pattern that actually catches things: run **two models from different vendors or of different sizes**, then **reconcile** their findings instead of concatenating them.

## Why this works

Different models (or the same vendor's different model tiers) are trained differently enough that their errors are only partially correlated. Agreement between them is a real confidence signal. Disagreement is where the interesting findings live. But they are still both language models trained on overlapping data: agreement reduces *stochastic* misses, but it does not clear a *shared* blind spot. For anything safety- or correctness-critical, pair this with at least one non-LLM check (run it, compute it, grep for it).

## The pattern

1. **Identify the artifact.** A diff, a file, a plan, a claim. Decide whether you're reviewing code or prose: the framing changes what "finding" means.
2. **Run your primary reviewer's own pass first** (one or several review lenses; see below). Don't skip this: the second model adds diversity, it doesn't replace your own critique.
3. **In parallel, run a second model** (a different vendor's CLI, or a different tier of your own vendor) with read-only access to the same artifact. Give it a specific focus question, not just "review this." Never send secrets, regulated data, or embargoed material to a third-party model you don't already trust with that data.
4. **Synthesize.** The actual value is here, not in step 3. Never just paste the second opinion into your output; reconcile it against your own.

Run the two passes concurrently rather than serially; on a large artifact, split it into chunks and review each chunk separately, since most review wrappers warn about size but silently truncate rather than erroring.

### Multi-lens fan-out (when one reviewer isn't enough on its own)

For anything merge-bound or high-stakes, don't rely on a single reviewer even within one model family. Fan out several independent reviewers, each briefed on a distinct lens (e.g., correctness, security, product-intent fidelity, completeness) and, if your tooling allows model overrides, running on different model sizes so they don't share a blind spot. Two stages, not one: a genuine correctness/simplicity pass first, then the adversarial pass. A same-model, same-lens panel is not a real panel.

## Refute-verification: the load-bearing step

Every candidate finding must survive an attempt to refute it before it gets reported. In practice: route each finding to two or three independent reviewers whose job is specifically to try to knock it down. A finding survives only if it withstands that attempt. This single rule is what keeps a review from turning into a pile of plausible-sounding but wrong "findings." Fewer real findings beat a long list of maybes, and a wall of nitpicks with no real issue means "nothing substantive found," not "lots of problems."

Add one more pass after the fan-out: a **completeness critic** whose only job is "what did we not look at?"

## Synthesis contract

- **Tag every finding by source** (which lens, or which model raised it).
- **Agreement across independent reviewers = high confidence.** Surface these first.
- **Single-source findings get adjudicated, never rubber-stamped and never silently dropped.** State agree / disagree / uncertain with a one-line reason.
- **On factual disagreement about something material, run one rebuttal round.** Give the dissenting side the specific counter-evidence and ask it to withdraw (if genuinely refuted) or hold and sharpen its reasoning. Cap it at one round (two for genuinely high-stakes cases). A model that withdraws immediately just because it was told the other side disagrees is a known failure mode, the rebuttal prompt should explicitly say "withdraw only if the evidence refutes you," not "agree to be agreeable."
- **Matters of taste are the lead reviewer's call.** Tone, styling, severity, record the dissent in one line, decide, and move on. Don't escalate taste to a human.
- **Escalate to a human only when a finding is material and genuinely unresolvable** by the reviewers themselves, not merely because two models disagree.
- **Asymmetric veto for self-checks.** If a second opinion would, if true, mean an error in *your own* prior work or output, don't dismiss it on your own authority. That's precisely the case you're least equipped to judge fairly. Verify it with a non-LLM check or escalate, regardless of how confident you feel.
- Weigh the sampling asymmetry: if you ran several review lenses and the second model ran one pass, "the second model didn't flag it" is weak evidence either way.

## Fold-back

Fixes for confirmed findings should be test-first where feasible (write the failing test, then the minimal fix) and re-run the full validation gate before calling the finding closed. Standing practice worth adopting: after a PR opens, dispatch one more independent reviewer against the live diff and fold any real findings back the same way. Reviewers should return their verdicts to whoever is orchestrating the review, not post directly to external systems (PR comments, tickets). That keeps a human or lead model as the actual editor of what gets reported.

## Graceful degradation

If the second model or reviewing tool is unavailable (not installed, unauthenticated, timed out, empty output), proceed with the single-model review and say so explicitly in your report. Never block a review pass on tooling being down, and never silently downgrade to single-model without disclosing it.

## A related, prospective use of the same idea

The pattern above is retrospective: it critiques finished work. The same two-model idea also works prospectively: before a consequential, hard-to-reverse decision (an architecture choice, a migration, a release), ask a second model for its take on the options and risks before you commit. Same rule applies: it advises, you decide. Reserve it for genuinely high-stakes forks. Overusing it just adds latency and becomes a way to avoid deciding.
