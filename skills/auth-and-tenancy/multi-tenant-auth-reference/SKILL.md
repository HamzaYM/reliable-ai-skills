---
name: multi-tenant-auth-reference
description: "Use when debugging or changing auth, tokens, sessions, invites, or tenant isolation in a multi-tenant application: unexpected 401s/403s, cross-tenant data leaking or disappearing, role checks that seem too wide or too narrow, or row-level security that appears to be silently doing nothing."
---

# Multi-tenant auth and tenancy reference

Auth bugs in a multi-tenant system are expensive to debug by guessing, because the failure modes look identical from the outside (a 401, a blank page, a row that "should" be there) but have completely different root causes. The fix is to maintain a ground-truth reference for your own system's token/role model instead of re-deriving it from scratch every time, and to never guess which token or role kind is in play.

## Document every token/credential kind as a table, not prose

If your system mints more than one kind of credential (a full user session, a scoped short-lived token, a share link, an account-level token distinct from a session token), keep one table: what claims discriminate it, what mints it, what verifies it, and its TTL. The single highest-cost mistake in this space is guessing which kind of token a code path expects instead of looking it up. Treat two wrong guesses in one session as a sign the reference is missing or stale, not a sign to guess harder.

If tokens are stored client-side across multiple keys (a global session token, a per-resource token, an account-level token that must never get swapped into the global slot), document the full key set and both directions of any swap that can happen. The classic bug here is exactly that: an unrelated code path swaps the global slot back to the wrong credential mid-flow, and everything downstream 401s in a way that looks unrelated to the actual cause.

## Build a symptom → cause → fix decision table

Keep a running table of "if you see X, it means Y, do Z" for your own system's actual auth errors, e.g.:

| Symptom | Likely cause | Fix |
|---|---|---|
| 401 "wrong token kind" | A route expects one credential type and received another | Check the discriminator table above; don't retry with a different token blindly |
| 401 after a previously-working flow | A credential got clobbered by a parallel bootstrap/session-refresh path | Check the storage-key swap directions, not just the immediate call site |
| 403 on a role that should have access | A role guard is narrower (or a permission model is more granular) than the role name suggests | Check whether access is actually gated by a capability/permission, not the role string; see below |
| Cross-tenant read returns zero rows instead of an error | Isolation is enforced by a session-scoped context variable that wasn't set on this code path | Confirm the isolation context is pinned before the query runs, not after |

This table is worth more than any individual fix, because most "new" auth bugs in a mature system are re-encounters of an already-diagnosed failure mode.

## Prefer capability checks over role-string checks

`role === "admin"` (or any literal role-string comparison) is a trap the moment your permission model has more nuance than the role name suggests: for example, an "admin" role that shouldn't automatically get every admin capability, or a narrower role that legitimately needs one specific elevated permission. Gate behavior on an explicit capability/permission check (`requireCapability("doTheSensitiveThing")`), not on the role label. When you widen a role guard to "just make the 403 go away," you are very likely re-opening a boundary that was deliberately drawn. Treat any urge to widen a role guard as a signal to go find out why it was narrow, not a green light.

## Row-level isolation has a silent-bypass failure mode: know it

If tenant isolation is enforced by a database-level policy (row-level security or equivalent) keyed on a session-scoped variable, there is usually a role or connection mode that silently bypasses it entirely: for example, a superuser or elevated-privilege connection role skips row-level security unconditionally, with no error and no warning at query time. This is the single most dangerous failure mode in this category because it doesn't fail loud: the query just returns everything, and nothing tells you the policy didn't run. Concretely:

- The application's runtime connection must use a least-privilege role that cannot bypass the isolation mechanism. Never the same role that owns the schema or runs migrations.
- Add a boot-time or startup check that asserts the connected role does not have bypass privileges, and treat any warning from it as a stop-the-line issue, not a log line to ignore.
- Defense in depth: also filter by tenant ID in application code, even though the database policy should already be doing it. Isolation should not depend on exactly one mechanism working.

## Invite / redemption flows: enumerate every path explicitly

If your system has more than one way to redeem an invite (a user-account invite vs. a scoped single-use invite tied to a specific resource), they usually need genuinely different handling: different token shapes, different consumption semantics. Document both paths side by side and treat "what happens when someone re-invites an existing user, or a role mismatch shows up on redemption" as a product decision, not an engineering one. Escalate it rather than picking a direction that changes user-facing semantics unilaterally.

## Maintain provenance, not just facts

Auth references go stale fast: file:line citations rot the moment the branch moves. Date-stamp what you verified and how (a specific grep, a specific test name), so the next reader can re-verify in seconds instead of re-deriving the whole model from scratch.
