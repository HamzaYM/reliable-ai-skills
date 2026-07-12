---
name: config-and-secrets-hygiene
description: "Use when adding or changing configuration, environment variables, or feature flags: deciding which config layer something belongs in, adding a new per-tenant flag, debugging why a config value or flag \"does nothing,\" or reviewing whether a boot-time secret guard is safe to weaken."
---

# Config and secrets hygiene

Configuration bugs are rarely about the value being wrong. They're about the value landing in a layer nobody reads, a precedence rule nobody remembered, or a flag whose null/missing state does the opposite of what its name implies. This skill is a checklist for avoiding all three.

## Pick the right layer, on purpose

Most non-trivial systems end up with several config layers (server-side environment variables, client-side/build-time variables, and a runtime database-backed settings table for things end users or admins can tune). Choose deliberately:

- **Server-side env var**: per-deploy, infrastructure-shaped, or secret.
- **Client-side/build-time var**: the client needs it and it is *not* a secret. Anything that ends up in a client bundle ships to every browser that loads the app, full stop.
- **Runtime, tenant/admin-tunable setting**: an admin should be able to change it without a deploy. This is the highest-overhead option (needs validation, an admin surface, auditing); don't reach for it by default.

## Precedence traps that waste hours

- **A misspelled env var may be silently ignored** rather than erroring, if your config loader is configured to ignore unknown keys. If a new variable "does nothing," check the spelling against the exact field name before assuming a deeper bug.
- **Process-level environment variables usually beat a checked-in `.env` file**, which usually beats a local-only override file. Know your own stack's order, and check the override file closest to "wins" first when a value seems wrong. A stale local override file is one of the most common causes of "it works for everyone except me."
- **A local override pointing at a dead port/host is a classic silent trap.** If a client is healthy per every log but every request fails at the network layer, check for a stale local override before assuming a code bug.

## Boot-time guards exist to be obeyed, not relaxed

If your app refuses to boot on a placeholder/weak secret, or refuses to start without a required credential, treat that as working as intended, not as an obstacle. Fix the actual input (generate a real secret, set the real credential); never widen the list of "acceptable" values or delete the validator to unblock yourself locally. The entire point of the guard is to make it structurally impossible to accidentally run production, or anything production-adjacent, on a placeholder secret.

## Runtime feature flags: verify a consumer actually exists

A flag that renders correctly in an admin UI is not proof that anything reads it. Before relying on a runtime-tunable setting, or citing it in a fix, grep for its actual consumer in the codebase outside the settings-registration code itself. It is common, in a system that's grown organically, for a meaningful fraction of registered settings to have zero runtime consumer: the value is stored, displayed, editable, and completely inert. If you're asked to "make X configurable," check whether the field already exists unconsumed before adding a new one; the real work is usually wiring an existing dead field to its intended consumer, not creating a new one.

## Per-tenant flags: the null/missing semantics is a product decision, not a coin flip

When a new tenant-level flag can be null, missing, or malformed, decide its default deliberately based on blast radius:

- **Low-risk, convenience-only behavior** (an authoring nicety, a UI preference) → grandfather existing tenants in as "on" by default; new capability should not require every existing tenant to opt in manually.
- **Anything that can trigger outbound messaging, spend money, or take an automated action on a user's behalf** → invert the default: null/missing/malformed means **off**. The asymmetry matters because grandfathering a convenience feature on is low-cost if wrong, while grandfathering an automated outbound action on can mean silently enrolling every existing tenant into behavior they never opted into.

Never copy-paste one resolver's null-handling into a new flag in the other category without re-deciding this explicitly.

## Rollout flags: check the exact literal, and check both halves

If a rollout flag is read as a strict string literal (`=== "true"`, not any truthy value), and it's gated by an env-level master switch AND a per-tenant/per-record value, a flag flip that "does nothing" is almost always one of:

1. The literal doesn't match (`"1"` vs `"true"`, case, whitespace).
2. The other half of the pair is off (the master gate can override the per-tenant value in either direction; know which way).
3. The variable was set in the wrong deployment target, so the specific component that reads it never got it.
4. The change hasn't actually been redeployed yet.

Check in that order before assuming the flag's logic is broken.

## Adding a new flag: a repeatable recipe

1. A pure, testable resolver function, not an inline check scattered across call sites.
2. Default OFF / no-op everywhere, until step 4 explicitly turns it on somewhere.
3. If it's per-tenant, combine the tenant value with an env-level master (AND them together) and choose grandfather-on vs. invert-off per the blast-radius rule above.
4. Wire it into deploy config with a paragraph-length description and a genuinely no-op default, so adding the wiring itself ships as a no-op.
5. Document it in your env-var reference with a ticket/issue reference for why it exists.
6. Write down a rollback affordance before you ship the "on" state: know exactly what flips it back off.

## Live hygiene: things to check, not just things to fix

Keep a short automatable check (a script, or a documented set of greps) for the traps that recur in practice: a real secret sitting in a gitignored-but-present local env file, a client-side variable that would leak a secret if anything ever reads it, a stale local override pointing at a dead host/port, and any registered-but-unconsumed flags. Run it before trusting your own assumptions about current config state. These things drift the moment anyone edits a local file, and stale assumptions here waste real debugging time.
