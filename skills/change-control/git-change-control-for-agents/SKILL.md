---
name: git-change-control-for-agents
description: "Use when doing any git work: cutting a branch, opening a PR, merging parallel work, or resuming work in a repo you didn't just leave. Covers state verification before acting, the dead-base PR trap, migration-number collisions, working-tree discipline, and how to handle a product decision that surfaces mid-task."
---

# Git change control for agents

Agentic git work fails in specific, recurring ways that human muscle-memory usually avoids by accident: trusting a branch's state instead of checking it, building a PR on a base that's secretly already dead, and treating "clean up the working tree" as safe when it isn't. This skill is the checklist against all of them.

## Step 0: determine current state every time, never trust what you inherit

Never assume the checkout you're starting from reflects the true remote state, and never act on remembered sequencing from an earlier session. At the start of any branch/PR work:

```bash
git fetch origin
git status --short --branch
git log --oneline -1 origin/main
git log --branches --not --remotes --oneline   # local-only, unpushed work
gh pr list --state open --json number,title,headRefName,baseRefName
git worktree list
```

Decision gates:
- **On the main/trunk branch** → never work here directly; branch first.
- **Your current branch is already merged into the trunk** (its tip is an ancestor of the trunk's tip, and isn't the trunk tip itself) → don't commit more here; cut a fresh branch from the trunk instead.
- **Local trunk is behind the remote trunk** → never branch from local trunk; branch from the fetched remote tip.
- **Unrecognized dirty or untracked files** → don't stash or discard them; they may not be yours. Ask before touching anything you didn't create.

## The dead-base PR trap

Stacking a PR on another feature branch as its base, instead of the trunk, creates a real hazard: if that base branch later gets merged via a *different* PR (or an earlier snapshot of it does), your stacked PR silently orphans into repeated merge conflicts. The base still technically exists, which proves nothing about whether it's still the right target. Rules:

1. **Base every PR on the trunk.** For coordinated parallel work, merge individual branches locally into one integration branch first, then open a single PR from that integration branch to the trunk.
2. **Before opening a PR, confirm your branch actually contains the current trunk tip.** A stale branch needs a rebase/merge first, not a PR.
3. **If you must target a non-trunk base, verify it's actually still alive** (not merged, not closed) before you do: "the branch exists on the remote" is not sufficient evidence.

## Migration-number and other serialization collisions

If your schema-migration tool numbers files sequentially, two branches independently adding a migration can collide (duplicate numbers, multiple heads). Before and after merging any two branches that both touch migrations, check for exactly one head using your migration tool's own "list heads" command. Never assume it merged cleanly just because git didn't report a conflict (numbered migration files often don't textually conflict at all, which is exactly what makes this collision easy to miss). Fix by renumbering the later migration and re-chaining it, or by adding an explicit no-op "merge" migration if either colliding migration might already be applied somewhere you can't rewrite.

## Working-tree discipline

- **Never stash, pull, or switch branches mid-fix.** Work only on the current branch, and stage only the files your actual change touched.
- **Stage by explicit path, never a blanket "add everything."** A repo used as a workspace for more than just tracked product code (scratch notes, screenshots, generated artifacts) will sweep unrelated files into your commit if you add everything blindly.
- **Never run a destructive git cleanup command** (removing untracked files/directories) without first checking whether anything untracked is actually load-bearing. Some untracked directories are deliberately kept out of git because they're a live work queue or contain material that shouldn't be committed without asking. Treat any untracked directory you don't recognize as "ask before touching," not "safe to clean."
- **When a mistake lands on the trunk directly**, recover in preserve-first order: pin the mistaken commits on a new branch first, *then* figure out whether to reset (only if strictly local/unpushed, and prefer a non-destructive reset mode that aborts rather than discards if there's anything else going on in the tree). Never reset-first on a shared or already-dirty checkout.

## Parallel-work collision rules

When more than one agent or contributor is working simultaneously:
- **Any single serialized resource (a migration chain, for example) needs one coordinator**, not independent parallel writers. Race a schema change against a scratch/disposable copy of the database before merging, never against the first real shared instance.
- **High-churn shared files (a shared translations/localization dictionary, a shared types file) need one clear owner per work session**, with everyone else handing that owner their diffs rather than editing the shared file directly.
- **Before opening a PR from a long-running branch, confirm your diff is actually scoped to what you meant to change** (`git log origin/main..HEAD -- <file>` should be non-empty only for files you actually intended to touch). A stale base can make your diff quietly include changes you didn't make.

## Product decisions surfacing mid-task

If a task reveals a decision that changes user-facing behavior or semantics and isn't already settled by existing documentation, don't decide it yourself and don't guess to keep moving. Log it somewhere durable (a queued-decisions doc, a ticket) with the concrete options and your own recommendation. Park the affected work and continue on independent parts of the task. Note clearly, wherever you report progress, which parts were parked and why.

## Hard gates before anything merges

- **Never self-merge; get an actual review** (see the adversarial-review and tiered-review skills for how to make that review substantive).
- **Follow the repo owner's attribution policy for anything user-visible** (commit trailers, PR bodies, changelogs), and never let tooling set that policy for you. Where the owner's stated convention is no attribution artifacts, strip them and check before pushing (`git log <base>..HEAD --format=%B | grep -i <attribution-marker>` should return nothing); where there is no stated policy, ask rather than silently strip. Attribution is the repo owner's call, not the default your commit or export tooling happens to inject.
- **If merging to your trunk is itself a deploy trigger**, don't merge a schema or seed change you aren't prepared to see applied to the shared environment minutes later.

## When not to use this

Executing a large multi-PR backlog as coordinated batches is the campaign-execution skill. It builds on this one but adds wave planning and checkpoint discipline for work that spans many sessions.

*Evidence: both source versions of this skill passed the pre-registered, order-blinded A/B of July 2, 2026 (one source: must-hits 2/3 cold to 3/3 loaded plus a 3/3 tie; the second: 1/3 to 3/3 on both of its tasks); this merged rewrite was later tested in the July 2026 effort lattice, where the full 17-skill library ran against every model and effort level (results/matrix/MATRIX.md; evidence note updated 2026-07-12).*
