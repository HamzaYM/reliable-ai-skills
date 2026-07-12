---
name: pre-merge-validation-gate
description: Use before declaring any change "done," before opening or updating a PR, after any UI-touching change, or whenever you're about to report test results. Defines what "done" actually means and how to report it without overstating what was checked.
---

# Pre-merge validation gate

"The build passed and the unit tests are green" is not the same claim as "this works." Treating them as equivalent is the single most common way agentic work ships a real bug that automated checks structurally cannot see: a UI regression that a type-checker and a passing test suite both miss because neither one looks at a rendered screen.

## Core rule: a UI-touching change is not done until it has been driven live

Build passing plus unit tests passing is necessary, never sufficient, for anything that changes what a user sees or interacts with. If there's no CI safety net on the branch you're targeting, treat your local gate as the only one that exists. Don't assume a downstream check will catch what you skipped.

## Scale the gate to the change

Not every change needs the full gate. Match the check to the blast radius:

| Change | Minimum required |
|---|---|
| Docs/config only | None of the below |
| Backend-only, no client-visible behavior change | Backend test suite |
| Backend change to an endpoint a client calls | Backend suite + integration/e2e suite |
| Anything in the UI layer | Full suite + a live, driven check of the changed screen |
| Shared/high-traffic UI chrome | All of the above + any byte-identical or snapshot fixtures that depend on it |
| New or changed user-facing strings | Land in every locale in the same commit, then run the test suite (a locale-parity check, if you have one, is the only thing that catches a string landing in one locale only) |

## Live verification, not just green CI

Driving the actual feature (clicking it, submitting it, refreshing it, observing the real output) is not optional for a UI change, even when an end-to-end suite exists and passes. End-to-end coverage tests what someone thought to write a test for; live verification catches what nobody thought to test yet. Concretely: bring up the real stack, exercise the specific thing you changed, and report what you actually observed (screenshot as evidence when you can produce one), not just "the suite passed."

## Gate paid or costly test suites behind an explicit switch

Any suite that spends real money (a live LLM call, a paid third-party API) should be opt-in, not run-by-default. Keep it deselected in your default test config and only enable it explicitly when asked. Don't "fix" that deselection just because it looks like a suite is being skipped: that's the intended behavior, and removing the opt-in gate is how you get a surprise bill.

## Baselines drift: measure, don't assume

Lint/type-check error counts, warning counts, and "known-flaky" baselines are a snapshot from whenever someone last measured them, not a permanent constant. State the bar as "zero *new* problems in the files you touched" rather than an absolute number, and re-measure the baseline yourself before citing it. Don't copy a number from an old doc or a stale comment.

## Byte-identical / snapshot fixtures: recapture is not a rubber stamp

If your project pins some UI surface to committed fixtures (golden screenshots, byte-identical content baselines), a failure right after your intentional change is expected, but recapturing over it is not automatic. Before committing a recaptured fixture: read the diff against the old fixture and confirm every changed hunk traces to your intended change. Anything you can't explain is a regression, not a fixture update. Investigate it; don't launder it into the new baseline. Recapture, then re-run in assert mode (no capture flag) at least twice to confirm the new fixture is actually deterministic before committing it.

## Reporting: unambiguous, not optimistic

Report the gate as a table: one row per check, with exit status and counts, new-vs-baseline where applicable. Then:

- List every applicable stage you did **not** run, and why ("environment wasn't up" is a finding: go start it, don't skip the step and stay silent about it).
- Never write "tests pass" if any applicable stage was skipped or any failure is unexplained.
- Quote failures verbatim and label each one as pre-existing (already failing before your change) or introduced by it.
- For anything verified live, state exactly what you exercised and what you observed.

## Environment write discipline during verification

If verifying a change requires writing to a shared environment (a staging database, a real third-party service), positively identify the write target before you write anything. A working credential proves nothing about which environment it's pointed at; check the actual resource identity (account ID, hostname, connection string marker), not an environment-name variable that might be misleading by design. Never report a verification write as a "no-op": if it created, published, or mutated anything, say so. Some records are legally or operationally material the instant they're created (a published policy version, a config version, anything append-only). There is no "test" scope that makes writing one of those safe; if a verification step seems to require it, stop and escalate rather than improvising a workaround.

## When not to use this

This is the "is it done" gate, not the review-quality gate. Pair it with an adversarial or tiered review for anything merge-bound (see the adversarial-review and tiered-review skills). It's also not a debugging guide: if the gate surfaces a failure, that's a handoff to a systematic debugging pass, not a reason to loosen the gate.

*Evidence: both source versions of this gate passed the pre-registered, order-blinded A/B of July 2, 2026 (one source: must-hits 1/3 cold to 3/3 loaded on one task and a 4/4 tie on the other; the second: 0/3 to 3/3 on a consent-scenario task and a 2/3 tie); this merged rewrite was later tested in the July 2026 effort lattice, where the full 17-skill library ran against every model and effort level (results/matrix/MATRIX.md; evidence note updated 2026-07-12).*
