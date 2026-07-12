---
name: failure-archaeology
description: "Use when you're about to propose something that smells like it might have already been tried and abandoned: a hosting/platform migration, a framework or library swap, a \"quick fix\" to code that looks deliberately unusual, or when a revert commit turns up in git history. Prevents re-litigating settled decisions and re-fighting battles someone already lost on purpose."
---

# Failure archaeology

Every mature codebase has a set of approaches that were tried, didn't work, and were deliberately reverted or abandoned. Without a record of them, every new contributor (human or agent) is doomed to rediscover the same dead end at the same cost. This skill is about building and using that record.

## Why this is worth maintaining as its own artifact

A revert commit in history is a strong signal, but revert commits often don't explain *why* in the commit body itself: the reasoning lived in a conversation, a ticket, or someone's head, and is gone unless it's captured somewhere durable. The fix is a standing "settled battles" reference: one entry per abandoned approach, each with what was tried, why it failed or was reverted, and what the actual settled alternative is.

## What belongs in an entry

For each settled battle:
- **What was tried**: concretely, not vaguely ("switched the ORM's hosting adapter to X").
- **Why it failed or was reverted**: the actual technical reason if known (a specific limitation, an incompatibility), or "reverted, reason not recorded; re-derive before retrying" if the reasoning is genuinely lost. Don't invent a plausible-sounding reason after the fact; an honestly-unknown reason is more useful than a fabricated one, because it tells the next reader to actually investigate rather than trust a guess.
- **The settled alternative**: what the codebase actually does today instead, and where to find it.
- **A commit hash or reference** so the claim is independently checkable, and a note that hashes/details should be re-verified before being cited, since branches move.

## Categories worth keeping a battle log for

- **Hosting/platform migrations that were tried and reverted.** These are expensive to re-litigate because the original evaluation (cold starts, bundling incompatibilities, operational opacity) took real time to discover and is easy to forget once the codebase has moved on.
- **Framework-specific footguns that don't fail until build/deploy time.** Some config syntax (e.g., certain regex features in a framework's routing-matcher config) parses fine as a string but fails to compile at build time in a way that's easy to reintroduce if the constraint isn't written down anywhere near the code.
- **Product/UX decisions that were reverted specifically because they weren't the engineer's call to make**: a copy or behavior change that got reverted with a note like "this is a product decision, not a refactor target," independent of whether the change itself was good. The lesson here isn't about the specific change; it's that anything in this category needs the actual decision-owner's sign-off before it lands, even when it looks obviously correct.
- **A feature that shipped, got reverted, and came back reshaped.** Document the reshaped, currently-live version as the settled outcome, not the original attempt, so nobody re-proposes the original shape without knowing it already failed once.
- **Schema/migration naming footguns**: for example, a mismatch between a model's logical name and its actual mapped table/column name has, in practice, broken a migration chain more than once in the same codebase. Write down the exact rule for looking up the real physical name before hand-writing any migration SQL.
- **Infrastructure teething problems that were each fixed individually but look like a pile of unrelated hacks** if you don't know the underlying root cause connecting them (e.g., several container-networking symptoms that were all actually one binding/interface issue, fixed piecemeal over several commits). Document the root cause once, with pointers to where each individual fix lives, so nobody "cleans up" a fix whose purpose isn't obvious from the code alone.

## How to use the archive

- **Before proposing a change, check whether it matches a settled battle.** If it does, read the entry, and if you still think it's worth reattempting, that's a decision for whoever owns the system, not something to silently re-attempt. The fact that it was tried before is itself information they need.
- **Before deleting "weird" code, check if it's the fix for a settled battle.** Code that looks unnecessarily defensive or oddly specific is disproportionately likely to be exactly that. Read any comment near it, and check the archive, before assuming it's dead weight.
- **Treat a revert commit you find in history as a prompt to go looking**, not as a fact you already understand. If the archive doesn't have an entry for it yet, that's a gap worth filling once you understand it.

## Keeping the archive honest

An archive entry is only useful if it's trustworthy. Re-verify a cited hash or file reference before relying on it (`git show <hash> --stat` costs nothing and confirms the entry hasn't drifted). If digging through history turns up other settled battles not yet documented, add them. A quick sweep of `git log --oneline -i --grep="revert"` across a mature repo reliably turns up more of these than anyone remembers.

## When not to use this

This is about *already-attempted-and-abandoned* approaches specifically. For "here's a bug we already root-caused, here's the fix," that's the settled-battles table inside the systematic-debugging-playbook skill: related discipline, different artifact.
