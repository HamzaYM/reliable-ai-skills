---
name: consent-and-regulated-data-reference
description: Use when a change touches user consent, data retention or erasure, breach notification, or any messaging/communication opt-in that's subject to privacy or marketing-communication law (health data, financial data, or general personal-data regulation). Establishes fail-closed defaults and the never-cross lines that keep a system defensible.
---

# Consent and regulated-data reference

Systems that handle regulated personal data (health records, financial data, or personal data generally under a privacy regime) share a small set of hard rules regardless of jurisdiction or industry specifics. Get these wrong and the failure is not a bug ticket, it's a legal or compliance incident. The unifying principle: **fail closed everywhere, and never let a "test" or "verification" action create a legally material record.**

## Fail closed, structurally

- No consent record → no processing, no send, no session. Don't let a missing consent check degrade to "allow, and log a warning."
- A missing secret required for a compliance-sensitive path (a hashing salt, a signing key) should make that path fail hard (an error), never silently fall back to an unsalted or unguarded equivalent. This is one of the few places where "fail loud and ugly" is strictly better than "fail soft and available."
- If your consent/communication model has more than one generation (an old model being phased out, a new authoritative one), the gate logic should read from the current authoritative model only. A legacy model kept around for backward-compatible reads should never be treated as satisfying a current-model check.

## Never mix communication scopes

If your system distinguishes necessary/operational communication (e.g., service-related messages a user needs to receive) from optional/commercial communication (marketing, upsell, review requests), keep those two consent scopes **completely separate**, in both directions:

- An opt-in for necessary communication never authorizes commercial communication.
- An opt-out from commercial communication must never also silently revoke necessary/operational consent.
- Any new message type needs its scope declared in exactly one place, so "which scope does this belong to" is never re-derived ad hoc at each call site.
- Commercial-category sends should sit behind their own explicit kill switch, off by default, and that switch must gate every stage of the flow (rendering the opt-in UI, capturing the opt-in, and the actual send). A gap at any one stage defeats the whole switch.
- A hard, global opt-out signal (e.g., a "stop all messages" reply) should override every per-service or per-relationship opt-in: global always wins.
- Delivery failures (bounces, spam complaints) are a deliverability signal, not a consent signal. Don't let your bounce-handling code accidentally mutate consent state.

## Age and minors: gate deliberately, everywhere self-consent matters

If your product allows self-directed sign-up or data submission and your jurisdiction has an age-of-consent rule, every entry point that can create a session or consent record on someone's own say-so needs the same age gate. A new unauthenticated entry point added later needs the identical check, not a "we'll add it eventually."

## Retention and erasure: automate it, and never touch the audit trail

- Automated retention/erasure sweeps (a scheduled job that purges expired data, processes a deletion request) need to actually run on a real schedule in your deployed environment. Verify the scheduling mechanism is live, not just that the code exists. A retention job that only exists on an unmerged branch is not compliance, it's a draft.
- An append-only audit trail (anything designed as tamper-evidence) should never be purged, updated, or reordered, ever, including as part of a retention sweep. If a genuine legal need to purge audit history arises, that's a decision for whoever owns legal/compliance risk, never a routine engineering action.
- Distinguish between data that must cascade-delete with a user's record (their raw data) and a durable, PII-free proof-of-consent record that should survive deletion specifically to prove consent was once properly obtained. Conflating the two means you either fail to actually erase someone's data, or you lose your own evidence that consent was handled correctly.

## Audit metadata: allowlist, not denylist

Any logging or audit path that records metadata about an action should filter what it stores through an **explicit allowlist** of safe keys, dropping anything not on the list. Never try to enumerate everything unsafe and block that instead, because a denylist reliably misses the next new field someone adds. Long or free-text content that needs to be referenced in an audit record should be hashed or truncated, never stored verbatim. Adding a new logged action means adding its specific new metadata keys to the allowlist as part of that same change, not as an afterthought.

## Publishing anything legally material is a real write, never a "check"

If a change publishes a new version of a legally material document (a consent-text version, a policy version, anything that other records will reference going forward), that publish action is real and irreversible-in-effect the moment it happens: subsequent records point at it. This means:

- **It is never an acceptable "verification" or "no-op check."** There is no test-environment exception for this specifically, because in a lot of real systems test/staging environments share the same tables as production for exactly this kind of record.
- Any minimum-content or validation guard on a publish action (a minimum length, a required review step) exists specifically to block low-effort accidental publishes. Never weaken it to unblock a test.
- If a genuine test of the publish mechanism is required, use an isolated, disposable copy of the data store, never a shared environment.

## Breach notification: build it to actually fire

A breach-notification path should always record that a breach was reported (an audit entry), independent of whether the notification email actually got sent. Don't let a missing notification-destination configuration silently mean "nothing happened." If the destination isn't configured, that should surface clearly (at minimum a loud warning, ideally a hard failure at the point notification is attempted), not a silently-skipped send.

## Legal/regulatory status is often a live open question, not a fact you can assert

Whether a specific data-handling posture (e.g., "all sensitive data stays within a specific region," or "this consent language is sufficient") is actually compliant is very often something that's still pending a formal legal or compliance sign-off, even after the engineering work is done. Present open regulatory questions as open, explicitly, and point at wherever your organization tracks real status (a ticket, a legal review doc) rather than asserting compliance yourself. Never let engineering confidence in the implementation substitute for an actual compliance sign-off.

## When not to use this

For the AI-call-specific version of handling sensitive data (cost tracking, provider fallover safety), see the ai-cost-tracking-and-guardrails skill. The two are complementary but distinct.
