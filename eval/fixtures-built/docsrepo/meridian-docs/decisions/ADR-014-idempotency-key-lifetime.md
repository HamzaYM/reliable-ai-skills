# ADR-014: idempotency key lifetime

Date: 2026-02-12
Status: Accepted

## Decision

Idempotency keys expire 24 hours after first use.

## Rationale

A 24h window covers client retry storms and overnight batch replays while
keeping the key table small enough for the hot path. Longer windows showed
no additional dedupe benefit in the replay analysis.

Implementation: src/idempotency.py.
