---
name: architecture-contracts-as-law
description: "Use when changing anything that crosses a system boundary: database schema, wire/API shapes, cross-module imports, the one place a third-party SDK is allowed to be called from, or when tempted to build infrastructure \"ahead of need.\" Establishes a single merge-blocking source of truth for system invariants, kept current in the same commit as the code that changes it."
---

# Architecture contracts as law

Large systems accumulate implicit invariants ("this module never imports that one," "only this file talks to the LLM SDK") that everyone half-remembers and nobody has written down. The fix is a single, explicit contract document that is treated as merge-blocking law, updated in the same commit as any change to what it governs: not a wiki page that quietly goes stale.

## The contract document is a source of truth, not documentation

Whatever you call it (a CONTRACTS file, an architecture decision record, an invariants doc), it needs one property to actually work: **drift between it and the code is treated as a bug**, not as "the doc needs updating eventually." Concretely:

- Any change to schema, API/wire shape, route surface, or a documented invariant updates the contract document **in the same commit**, and the change is called out explicitly in the summary of that commit/PR.
- If the contract is ambiguous or looks wrong for what you're trying to do, that's a stop-and-surface moment. Don't silently improvise an interpretation and move on.
- Locked algorithms or formulas (see the llm-eval-harness-and-scoring-pipeline skill for a concrete example) live here, with an explicit note on who has to sign off before they can change.

## Enforce a module dependency direction, and name the exceptions

If your system has a layered or DAG-shaped dependency structure (module A may depend on B but never the reverse), write the intended direction down explicitly, and separately maintain a short list of the **real, current exceptions**. In any system old enough to matter, reality has drifted from the original diagram at least a little. An exception list that's honest about existing deviations is far more useful than a diagram that's aspirationally clean but wrong. New code should follow the documented direction; an existing exception is not a license to add a new one elsewhere without the same scrutiny the original one presumably got.

Verify programmatically, don't just trust the doc:

```bash
# generalized pattern, adapt the paths/import syntax to your language
grep -rn "^from your_module\." path/to/leaf_module | grep -v "expected internal imports"
```

## Isolate third-party SDK / vendor boundaries to one module

If your system calls an external LLM provider, payment processor, or any other vendor SDK, funnel every call through a single module that owns that boundary. Domain code gets a thin accessor function, never the raw SDK client. This buys you two things: a swappable provider (changing the default model or backing vendor is a one-line change in one place) and an enforceable invariant you can literally grep for:

```bash
grep -rn "from provider_sdk_name" your_codebase --include="*.py" | grep -v path/to/the/one/allowed/module
```

Keep an explicit, current list of the rare legitimate exceptions (e.g., a batch-API client that needs its own SDK instance, or a module that only imports the SDK's error types for exception handling). Anything not on that list is a violation.

## Version anything whose meaning changes over time

Prompts, scoring rubrics, rule configurations: anything read at runtime whose *content* changing changes behavior should be versioned as explicit files or records, not edited in place. Every row/record produced using one of these should record which version produced it, so you can answer "what changed, and which past results does it affect" without guessing. New versions get added as new files; old versions stay around for as long as anything produced under them needs to remain comparable.

## Keep an explicit deferred-work ledger with pickup triggers

For deliberately-postponed infrastructure (a queueing system you don't need yet, an auth provider swap, a caching layer), don't just leave a "TODO: maybe someday" comment. Keep one ledger with, per deferred item: what's deferred, what the interim shortcut is, and the **explicit, concrete trigger** that means it's time to build it now ("when scoring consistently takes longer than N minutes," "when a second external identity provider is needed"). This does two things: it stops people from building speculative infrastructure early ("check the ledger: has the trigger actually fired?"), and it stops the deferred item from being silently forgotten once the trigger does fire.

## Freeze identifiers that other systems depend on for comparability

If an ID (a category, a rubric dimension, a taxonomy key) is used anywhere that compares values across time or across records, treat renaming or removing it as almost never acceptable once real data exists under it. A rename breaks every historical comparison silently. Add new identifiers for new concepts; don't repurpose old ones. Where a decision like this has already been made, document it as settled rather than leaving it to be re-litigated by whoever encounters the temptation next.

## Physical infrastructure names can be permanent even after logical renames

If you rename a logical reference to a piece of infrastructure (a Terraform resource address, a code-level identifier) but the actual deployed resource has a physical name baked in at creation (an IAM role name, a fixed identifier some other system already depends on), renaming the physical name usually means destroy-and-recreate, not a clean rename. Decide explicitly whether that's worth doing as its own planned operation. Don't let it get bundled unintentionally into an unrelated change just because the logical name looks inconsistent.

## Don't cite a number: read the source

Any place your documentation states a count that can drift (a count of error codes, capability flags, dependency-free modules) is guaranteed to go stale, and multiple docs disagreeing about the same count is worse than no doc at all. It hands the reader three wrong answers instead of one honest "go read the code." Where you need to communicate something like this, either point at the single source of truth to compute the number, or drop the number entirely and describe the property instead of the count.

## When not to use this

For the specific technique of keeping a symptom-driven token/permission reference for auth systems, see the multi-tenant-auth-reference skill. For which *document* wins when several pieces of documentation disagree with each other, see the docs-of-record-and-arbitration skill.
