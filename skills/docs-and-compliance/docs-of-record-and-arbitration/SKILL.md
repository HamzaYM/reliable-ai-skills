---
name: docs-of-record-and-arbitration
description: Use when project documentation disagrees with itself, disagrees with the code, or you're not sure which of several overlapping docs is actually current, and when producing a business or team-facing deliverable (a showcase, a report, screenshots) that needs to be factually solid before it ships.
---

# Docs of record and arbitration

Mature projects accumulate overlapping documentation: several versions of the same spec, a "why we built it this way" doc that's now describing a stack nobody uses anymore, a README that was accurate on the day it was written and hasn't been touched since. The failure mode is building from whichever doc you happened to open first. The fix is an explicit arbitration order, applied consistently.

## Classify every doc as authoritative or historical, explicitly

Keep one short table: which documents currently govern which decisions, and which are retained only as history and should never be built from. A doc that's superseded should say so in its own header if possible ("superseded by vN, kept for history"), but don't rely on that alone. Maintain the classification independent of whether the old doc admits it's stale.

## Arbitration order when documents disagree

A reasonable default order; adapt it to your own project's actual sources of truth:

1. **A settled-decisions ledger**, if you keep one (a running log of "we decided X, here's why, here's where it's implemented"). This beats every other document, because it records an actual decision made with full context, not a snapshot of intent.
2. **The contract/invariants document** (see architecture-contracts-as-law), for anything about schema, API shape, or system invariants.
3. **The current product/behavior spec**, for what the system is supposed to do, as of now.
4. **Everything else**: older specs, README sections, "why we chose this stack" docs. Useful for historical context, never for settling a current disagreement.

Concretely: if a doc contradicts a settled decision, or contradicts code that already correctly implements that decision, **the doc is wrong.** Fix the doc and cite the decision when you do. If code contradicts the contract document, that's a bug, full stop, regardless of which one you assume is "obviously" right. And if resolving the discrepancy would itself create a new product decision that isn't already settled, that's an escalation, not something to resolve by picking whichever reading is more convenient.

## Docs can be wrong even when they look official

Even a formally-versioned spec has, in real projects, been caught inventing behavior that never shipped and never matched an already-settled decision. The lesson isn't "specs are untrustworthy," it's "verify against the actual settled decision and the actual code before treating any single document, however official-looking, as ground truth." A living review corpus (open findings, triage notes) can itself go stale the moment a finding gets fixed: a "still open" claim from a finding-tracking doc is worth a quick check against current code before you act on it.

## How docs of record get properly updated

- Contract-relevant changes land in the same commit as the code change that necessitates them, never as a promised follow-up.
- When a document needs a substantial rewrite rather than an amendment, prefer cutting a new version that explicitly supersedes the old one over silently rewriting history in place. Within a given version, small amendments get folded in as dated addenda rather than spawning a new version for every tweak.
- Screenshot-based or visually-captured documentation (a team guide, a walkthrough) should treat every image as a **regenerable slot** tied to a specific route/state, not a hand-made asset. If a slot's capture fails because the underlying UI moved, that's a signal to fix the capture definition, not to hand-edit or fake the image.

## Producing a new business/team deliverable: confirm scope before building

Before generating any nontrivial document, screenshot showcase, or report, confirm three things if they aren't already pinned by the request: the actual output format, the intended audience (their technical depth changes the right level of detail enormously), and where it's meant to live. Building the wrong format for the audience is expensive to redo and is a very avoidable mistake. One clarifying question up front is cheaper than a full rebuild.

Calibrate review effort to the deliverable's stakes: an internal-only draft needs one honest verification pass (facts, links, do the screenshots match what they claim to show); a customer-facing or high-stakes deliverable earns the full tiered or adversarial review (see those skills). Running a heavy review pipeline on a low-stakes internal doc is not "being careful," it's wasted effort that could go somewhere more useful.

## Fact-check before you polish

For any deliverable built substantially from claims about a real system (a feature showcase, a technical write-up), write the underlying fact sheet first, every claim paired with the concrete evidence backing it (a specific file, a specific measured number, a specific verified behavior), before writing the polished prose. Let the prose only ever say what the fact sheet actually supports. This ordering matters: polishing prose first and fact-checking after tends to preserve whatever the first draft assumed, even when it's wrong.

## Screenshot-heavy documents need their own integrity check

If a deliverable includes before/after image pairs or a set of captured screenshots:
- Verify every referenced image file actually exists, and every captured file is actually referenced somewhere (an automatable check, not a manual scan).
- For every before/after pair specifically, open both images and confirm they show the same surface in a comparable state. This is the single most common way this kind of document ships something quietly wrong (an "after" that's actually an unrelated screen), and no automated tool catches it reliably.
- Caption honesty: if a shown surface has placeholder or non-final content, the caption needs to say so. Don't let a polished screenshot imply something is finished when it isn't.

## Follow the owner's attribution policy in anything user-visible

The same rule as in git-change-control-for-agents applies here with a wider blast radius: a changelog entry, a report footer, or embedded document metadata should carry attribution according to the repository or organization owner's stated policy, not according to whatever your export tooling defaults to. Where the owner's convention is no attribution artifacts, strip them; where no policy is stated, ask rather than silently strip. Check the actual output, not just the source you wrote, since export tooling (document generators, static-site builders) sometimes injects its own metadata you didn't type. The point is deliberate policy-obedience: attribution is the owner's call, never the tool's.

## When not to use this

For the specific discipline of handling regulated data (consent records, retention) inside these documents or systems, see the consent-and-regulated-data-reference skill.
