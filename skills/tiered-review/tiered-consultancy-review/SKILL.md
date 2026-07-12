---
name: tiered-consultancy-review
description: Use when a deliverable needs to go from rough draft to genuinely finished without the requester babysitting every pass, a cover letter, a strategy memo, a customer-facing document, a recommendation, a decision review, or any artifact where tone, framing, and defensibility all matter as much as correctness. Mirrors how a consulting firm actually reviews work before a partner signs it.
---

# Tiered consultancy review

Most review setups are flat: one reviewer, one pass, done. That catches surface errors but misses the things a real firm catches before a partner-level deliverable goes out the door: weak framing, an unearned claim, a tone mismatch for the audience, a competitor argument nobody stress-tested. The fix is to run review as an actual **escalation ladder**, the way a consultancy staffs a real engagement: juniors first, then managers, then specialists, then partners, and only then does it reach the person who actually owns the decision.

## The ladder

Each tier has a distinct job. Don't collapse them into one giant "review this" pass, the value is in the separation.

1. **Analysts (parallel, blind to each other).** Two or three independent first passes, each reading the draft cold through a different frame (e.g., one for the core argument, one for factual/technical grounding, one for how a skeptical outsider would read it). Blind means they don't see each other's notes yet: that's what prevents one loud opinion from anchoring the rest.
2. **Managers (synthesis).** Merge the analyst passes into one coherent draft. Resolve overlaps, keep the sharpest version of each point, and drop redundant feedback. This is where "several good ideas" becomes "one good draft."
3. **Specialists (targeted passes).** One or two reviewers with a narrow, specific mandate, e.g., "is every factual claim actually true and not overstated," or "does this read naturally for the intended audience, not like a machine wrote it." Specialists catch what generalists miss because they aren't trying to catch everything at once.
4. **Partners (three angles, not one).** This is the tier that decides if it ships:
   - **Internal partner**: reads for whether it serves the requester's actual goal and asks for anything that strengthens their position.
   - **External partner**: reads as the actual audience would, with zero sympathy for how the sausage was made. Cuts throat-clearing, hedging, and anything that reads as unearned.
   - **Adversarial partner**: actively tries to find the argument's weakest point, the way a skeptic or competitor would attack it. This tier catches structural problems the earlier tiers were too close to see (e.g., a draft that led with the wrong achievement because the "obviously best" evidence actually undercut the core claim).
5. **Final polish.** One last pass for length, redundancy, and voice consistency after all the substantive edits have landed.

## Rules that make this actually work

- **Each tier can do one of three things with what it receives: fix it directly, confer with a peer at the same tier, or kick it back down with specific, actionable feedback.** A tier that can only pass things up is not adding review, it's adding latency.
- **Keep a review ledger.** One line per material change: what was flagged, at which tier, and what changed as a result. This is what lets you defend the final version later and lets the next review start from where this one left off instead of re-litigating settled points.
- **Escalate to the actual owner only for calls only they can make**: a factual claim only they can verify, a framing choice that depends on context the reviewers don't have, a tradeoff between two legitimate options. Don't escalate taste; the partner tiers exist to make taste calls.
- **Calibrate the depth of the ladder to the stakes.** A five-tier pass with three independent adversarial angles is for something that ships externally and is hard to walk back. An internal working doc gets one honest pass, not the full ladder. Running the whole pipeline on low-stakes material is how review theater happens.
- **The adversarial tier is not optional for anything customer- or decision-facing.** It is the one most likely to be skipped because it feels redundant after four other passes already said "looks good," and it is the one that catches structural problems the others structurally cannot, because everyone before it was working from inside the same frame.

## A parallel version for finished code or docs

The same escalation idea works as a **fixed-panel** variant rather than a strict ladder, useful when you want speed over depth: run several review lenses in parallel and blind (fidelity to spec, completeness against a checklist, clarity for a reader with zero context, honesty about alternatives considered, and a red-team pass), then route every material finding to an independent verifier whose only job is to try to refute it against the actual artifact (the live code, the actual source document). Report confirmed vs. refuted counts explicitly, fix every confirmed finding, and re-verify the fix against the real artifact rather than trusting the diff. This variant trades the sequential ladder's depth for running everything at once. Pick it when the artifact is well-defined and you want thorough coverage fast rather than a genuinely escalating argument.

## When not to use this

For a quick correctness check on a small diff, use a single adversarial pass instead (see the adversarial-review pattern). The full ladder is overkill and will just slow you down without adding real signal.
