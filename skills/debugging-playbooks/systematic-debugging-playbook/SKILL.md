---
name: systematic-debugging-playbook
description: Use when debugging any bug, regression, or failing test, before proposing a fix, and especially before editing a file you know is a frequent source of regressions. Establishes ground truth before hypothesizing, and defines the discipline for multi-round fix loops after a review pass finds problems.
---

# Systematic debugging playbook

The most expensive debugging mistake is skipping straight to a hypothesis and a fix. In any codebase with real history, most "new" bugs are re-encounters of something already root-caused, and most fixes that get re-reviewed introduce a second bug in the process of fixing the first. This playbook is the discipline against both.

## Step 0: look up ground truth before forming a hypothesis

Before writing any code:

1. **Search prior art first.** Grep commit history for the symptom (`git log --all -i --grep="<keyword>"`), check any existing investigation/post-mortem archive your project keeps, and check file history for the specific file involved (`git log --follow -- <path>`). A surprising number of "new" bugs already have a full root-cause writeup sitting in history.
2. **If a prior investigation doc exists, check whether it was later corrected or resolved.** A doc that opens with a "RESOLVED" or correction banner should have that banner treated as overriding the body. Verify the recorded fix is actually still present in current code before concluding a fixed issue "recurred": it's easy to mistake "I'm looking at the pre-fix version" for "this regressed."
3. **Don't trust a finding's classification blindly, including your own project's tracker.** A finding marked resolved, retracted, or not-reproducible should be re-verified via the real path that would trigger it, not assumed correct because a doc says so. Post-mortems have real examples of a "confirmed" finding turning out to be an artifact of how it was tested (a guessed URL producing an expected 404, not an actual broken link).
4. **If the symptom touches auth/permissions**, resolve it against your actual token/role model (see the multi-tenant-auth-reference skill) before guessing which credential or role is involved. Guessing here is exactly the kind of thing that burns hours for no reason, because the answer is almost always already in the code.

## The core loop: reproduce, then write the failing test, then fix

**Reproduce at the lowest layer that actually shows the bug.** Pure logic belongs in a unit test with a minimal mock, not a full end-to-end run. A user-facing flow bug needs an end-to-end reproduction; a runtime-only issue (something that only shows up under production-like load or logging) may need a read-only look at real logs before you can even reproduce it locally. That's a legitimate outcome, not a failure to reproduce.

Then:
1. Write the failing regression test **before** the fix, and make sure it actually reproduces the real failure shape. A test using an unrealistic stand-in (e.g., a simplified stub that doesn't match real-world framing/encoding) can pass while the real bug remains, which is worse than no test because it looks like coverage.
2. Fix the root cause, not the symptom. If the same logic exists in more than one entry point (a streaming and non-streaming version of the same operation, for instance), the fix has to land in both: "twin" code paths are a common place for a fix to land in one and not the other.
3. Write a commit message that states symptom → root cause → fix → how you verified it. This is what makes the "search prior art" step above actually work for the next person (including future-you). A vague commit message breaks the whole mechanism.

## Danger zones: track your own hot files

Keep a short, explicit list of files with unusually high fix-churn in your own project (measurable with `git log --format= --name-only | sort | uniq -c | sort -rn`). Treat any edit to one of these as needing extra care and, if one exists, a guard test run before and after the change. These files have earned their reputation, and a "quick fix" to one of them is disproportionately likely to be the next entry in this list.

## Multi-round fix loops: the regression rule

When a review pass (see the adversarial-review or tiered-review skills) surfaces multiple findings and you fix them in rounds, the proven failure mode is **the fixer introduces the next round's bug**. Concrete rules that prevent this:

1. **Every fix in round N ships with its own regression test in round N**, not a follow-up.
2. **Before declaring round N done, re-run every test added in rounds 1 through N**, not just the new one. A fix late in the loop can silently break an earlier round's guard.
3. **Treat each round's diff as the next round's review target.** A reviewer's job in round N+1 is to diff round N's changes specifically, not just re-check the original findings.
4. **One commit per round, with the round labeled in the message**, so that if a regression does slip through, it bisects cleanly to the round that caused it.

Calibrate how many rounds and how much review-fleet weight you throw at this to the actual stakes: a shipped, customer-facing change warrants the full loop; an internal working doc doesn't.

## Never "flip it to see what happens" in a shared environment

If the question is "would a different model, flag, or config behave differently," resist the urge to just flip it on a shared/production-like environment to observe. Use a shadow/observation mechanism instead (see the llm-eval-harness-and-scoring-pipeline skill) that runs the candidate in parallel without it ever affecting real behavior or real users.

## Writing up a nontrivial investigation

If you spend real effort investigating something, write it down in a consistent, searchable format: what triggered the investigation, your conclusion (labeled clearly as confirmed root cause vs. best hypothesis), and the evidence trail (log lines, file:line references, session/request identifiers). If you found nothing and changed nothing, say so explicitly at the top: "read-only, no changes" is a valid and useful outcome to record. If a later finding invalidates an old writeup, prepend a dated correction banner; never silently edit or delete the original. The original's evidence trail still has value even when its conclusion turns out to be wrong.

## When not to use this

If you're specifically trying to avoid re-attempting something that was already tried and abandoned (not "already fixed," but "already tried this exact approach and it didn't work"), see the failure-archaeology skill. It's a distinct, complementary discipline.

*Evidence: both source versions of this playbook passed the pre-registered, order-blinded A/B of July 2, 2026 (one source: must-hits 1/3 cold to 3/3 loaded and 2/3 to 3/3; the second: 0/3 to 2/3 and a 2/3 tie); this merged rewrite was later tested in the July 2026 effort lattice, where the full 17-skill library ran against every model and effort level (results/matrix/MATRIX.md; evidence note updated 2026-07-12).*
