---
name: ai-cost-tracking-and-guardrails
description: "Use when adding or changing any LLM call in a system that handles regulated or sensitive data (health records, financial data, other personal information) or that needs hard cost control: provider fallover between vendors, rate limiting, per-session or per-tenant cost caps, or making sure every call is tracked and priced."
---

# AI cost tracking and safety guardrails

Every LLM call in a production system costs real money and, in a lot of real systems, also carries sensitive or regulated data. Both problems get solved the same way: make the safe/tracked path the only path that's easy to write, and enforce it with an automated check rather than a code-review convention that erodes over time.

## Guardrail 1: every call is tracked, with an explicit opt-out

The failure mode to design against is a new LLM call that quietly bypasses your cost/usage tracking because it was written against the raw SDK client instead of your tracked wrapper. Enforce this with a static check (a script that greps for raw provider-client usage and diffs against an allowed baseline), wired into your test suite so it runs on every change, not just something a reviewer might remember to check. Two things make this actually hold up:

- **The check needs to catch direct instantiation, not just direct function calls.** A grep for "raw call" typically misses `new ProviderClient(...)`. Wrap the instance yourself immediately after constructing it.
- **The opt-out must be explicit and local.** If a script, test, or one-off tool genuinely can't build the tracking context, require an explicit `{ untracked: true }` (or equivalent) on the same line as the call, never a silent bypass. That keeps the opt-out visible to the same grep that catches accidental misses.
- **Tracking failures should fail loud, not swallow silently.** If writing a usage record fails, that should surface as an error on the request, not a silently-dropped tracking row. A silent swallow defeats the entire point of a cost cap, because the cap logic reads the same table that just failed to get written to.

## Guardrail 2: cross-provider fallover is a denylist, not a guess

If you fail over from a primary LLM provider to a secondary one on error, classify errors as **definitively non-retryable** (bad request, auth failure, not-found, a content-policy rejection) vs. **everything else** (rate limits, timeouts, 5xx, connection errors). Retry/fail over on the second category; never fail over a definitively-rejected payload to a different vendor. If the primary vendor rejected it outright, rerouting it to a second vendor can mean sending sensitive data somewhere it was never approved to go. Write this as an explicit denylist function with tests, not an inline `if` in the retry logic, because "everything else fails over" is the correct default and it's easy to accidentally invert it while refactoring.

## Guardrail 3: rate limiting fails closed, everywhere, by default

A rate limiter (or any safety-relevant gate) should fail **closed** in every environment unless a narrow, explicitly-named override is set for local development. Do not gate fail-open/fail-closed behavior on an "is this production" check: see the config-and-secrets-hygiene skill for why environment-name checks are unreliable in staging-like environments that deliberately mirror production defaults.

## Guardrail 4: cost-cap state must survive the transaction that triggered it

If a cost cap is checked inside a database transaction (e.g., under an advisory lock) and the cap is exceeded, the "we blocked this" record often needs to be written to the database *after* that transaction has already rolled back, because the very error that trips the cap is what's causing the rollback. Writing the "blocked" record on the same connection, inside the same transaction, means it gets thrown away by the rollback that triggered it. Persist it on a separate connection/transaction, in the caller's exception handler, after the original transaction has fully unwound. Test this specifically (start a session, force the cap, verify the block record survived). It's the kind of bug that looks fine until the first real production cap trip.

## Guardrail 5: no session/call without a resolved tenant or cost-attribution context

If cost caps and tracking are keyed on a tenant/organization/account ID, any code path that can start a billable session must refuse to proceed without that ID resolved. Never fall through to an untracked, uncapped path just because the ID lookup came back null. A missing tenant ID should block session creation with a clear error, not silently downgrade to "untracked call, no cap enforced."

## Guardrail 6: price every model that can appear in a response

Any model identifier that can show up in your usage records needs a matching row in your pricing table, including less common presets and foundation-model IDs from a secondary cloud provider. An unpriced model should never silently report as free-of-cost: that blinds your spend dashboard exactly when a new or experimental model starts taking real traffic.

## Handling sensitive or regulated data specifically

If the system processes health data, financial data, or other regulated personal information:

- **Fail closed on anything that gates handling of that data.** A missing required secret (a salt, a signing key) should make the dependent route fail hard, never silently fall back to an unsalted or unguarded path.
- **Keep sensitive data out of logs and audit metadata by allowlist, not denylist.** Maintain an explicit allowlist of metadata keys that are safe to log; drop anything not on the list rather than trying to enumerate everything unsafe. A denylist of "known-bad" keys reliably misses a new field the next engineer adds; an allowlist fails safe by default. Long or free-text content that must be referenced in a log should be hashed/truncated, never logged verbatim.
- **Never claim data residency or handling guarantees your infrastructure doesn't actually provide.** If you're not certain every code path for a given data category stays within a specific region or provider, say so explicitly rather than asserting compliance. This is very often a live open question for counsel or compliance, not an engineering fact you can assert unilaterally.
- **New AI action that touches sensitive data → it needs a place in the audit-metadata allowlist and a place in the cost/fallover guardrails above, in the same change**, not as a follow-up.

## When not to use this

For the actual consent/retention/regulatory-lifecycle side of handling personal data (not the AI-call-specific guardrails), see the consent-and-regulated-data-reference skill.
