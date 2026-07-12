---
name: multi-agent-batch-campaigns
description: Use when executing a large backlog of review findings or a multi-part feature as coordinated batches across parallel agents or sessions, planning waves, avoiding file-contention collisions, and resuming a campaign that a previous session left mid-way through.
---

# Multi-agent batch campaigns

A single large backlog (dozens of review findings, a multi-part feature) executed by parallel agents over multiple sessions fails in specific, avoidable ways: agents redo already-finished work because a status doc rotted, two batches collide on the same file, and a session that dies mid-campaign takes unrecoverable context with it. This skill is the execution model that avoids all three.

## Step 0: re-establish ground truth. Status docs rot, git doesn't

Never trust a backlog's own status annotations at face value. Before planning or resuming anything:

- Check the actual current tip of your integration branch, not what a tracking doc says it is.
- Read the tail of any checkpoint/progress file for the real "what's done, what's next," and never redo an entry already marked done.
- Check for open PRs: a finding already owned by an open PR isn't yours to pick up.
- Check for unpushed, local-only branches: these are invisible to any remote-based check and are one disk failure from gone.
- For each individual finding you're about to work, re-read the actual current code at the cited location before trusting the backlog's description of it. Backlogs go stale the moment anything gets fixed, refactored, or moved, and citations (line numbers especially) rot fast.

A campaign that trusts a stale status doc instead of live state will, with some regularity, spend real effort redoing work that's already shipped.

## Planning a campaign

1. **Re-baseline every candidate item against the current integration tip.** Drop anything already fixed (with a one-line reason), and dedupe near-identical items across different sources into one canonical owner.
2. **Flag anything that would change user-facing behavior and isn't already a settled decision.** Escalate these as a batch, don't block the rest of the campaign on an answer, and don't guess.
3. **Group remaining work by area and primary file**, so each batch owns a disjoint slice of the codebase. This is what makes true parallelism possible without collisions.
4. **Sequence in waves**: test-only and genuinely file-disjoint work first (fully parallelizable), then area-local application code, then heavy-overlap areas last and sequenced rather than parallelized.
5. **Use one integration branch.** Batches branch off the integration branch's tip (not the trunk directly), get folded back in as they're reviewed and green, and only the single integration branch ever goes to the actual trunk as one PR. This keeps "many small changes landing continuously" from becoming "the trunk is red half the time."

## Maintain an explicit file-contention map

For any file that multiple planned batches might touch, write down in one place which batch owns it, and route every other batch's related changes through that one owner rather than letting them collide. High-contention files in most systems are predictable in advance (a routing hub, a shared type/contract file, a heavily-used service file), and calling them out explicitly before work starts avoids a lot of merge pain later.

## Parallel execution mechanics

- **One workspace/worktree per agent or batch**, as a sibling checkout, not a shared working directory. This is what actually enables true parallelism without agents clobbering each other's uncommitted state.
- **A backend batch that runs its own test suite needs its own isolated test resource** (a separate test database, a separate scratch environment) so parallel test runs don't collide with each other.
- **Every fix stays test-first** (see the systematic-debugging-playbook skill), and gets reviewed before folding into the integration branch (see the adversarial-review skill). A campaign is not an excuse to skip either discipline just because there's a lot of work to get through.

## Checkpoint-to-file discipline: mandatory for anything long-running

Long autonomous sessions die (hit a length limit, get interrupted, crash) more often than anyone plans for, and an in-progress session's context does not survive that. The only thing that reliably survives is what got written to a file. For any campaign expected to span more than one sitting:

- Maintain a single progress file with unambiguous resume instructions at the top ("if resuming: read this file, find the next unfinished item, do not redo finished ones").
- Append an entry after every meaningful event (a unit fixed, a batch gated, a PR opened, a review returned, a fold-back merged), with enough detail (branch, commit, what passed) that a fresh session could resume from just this file with zero other context.
- If a past entry turns out to be wrong, append a correction; never edit history in place. The point of the file is to be a trustworthy trail, and silently rewriting it defeats that.
- Keep individual work small enough to checkpoint frequently; detail belongs in the file, not in a single giant in-memory transcript that might not survive to the next session.

## Guardrails for autonomous/looped execution specifically

- Whoever owns the trunk merges the final integration PR. An autonomous loop should never merge anything into the trunk itself.
- Every fix stays test-first and gets reviewed; a long autonomous run is not a reason to relax either discipline.
- A new product/behavior decision surfacing mid-loop gets batched and flagged, never decided by the loop itself.
- Folding a reviewed batch branch into the integration branch with a local merge is not the same action as merging a PR to the trunk. The first is the required mechanism for a multi-batch campaign; only the second is the one action reserved for the trunk's owner.

## When not to use this

For a single bugfix or small feature, plain git-change-control-for-agents is enough. The wave-planning and checkpoint machinery here is specifically for backlogs and campaigns large enough to span multiple sessions or genuinely parallel agents.

*Evidence: the source version of this skill passed the pre-registered, order-blinded A/B of July 2, 2026 (must-hits 2/4 cold to 3/4 loaded on one task and 2/3 to 3/3 on the other); this rewrite was later tested in the July 2026 effort lattice, where the full 17-skill library ran against every model and effort level (results/matrix/MATRIX.md; evidence note updated 2026-07-12).*
