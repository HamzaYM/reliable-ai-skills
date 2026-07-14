# ADR-0014: move sessions from Postgres to Redis

Status: Proposed

## Context

Session reads dominate Postgres load at peak. Redis offers sub-millisecond
reads and a simpler hot path. See ADR-0009 for the session storage
decision this supersedes.

## Decision

Redis becomes the SOLE store for all session data. The existing Postgres
session tables are dropped after migration. There is no separate archive
or cold-storage tier.

## Capacity

~2,000,000 active sessions at ~4KB each is about 8GB, so a single 16GB
node has comfortable headroom.

Because Redis will comfortably hold everything, no eviction policy is
required.

## Durability

We enable RDB snapshots every 5 minutes; losing at most ~5 minutes of
sessions on failover is acceptable.

## Consequences

Postgres session load disappears; the session hot path moves entirely to
Redis.
