# ADR-0009: server-side session storage

Status: Accepted (2025-11-03)

## Context

Sessions are stored server-side in Postgres. The product creates on the
order of 2,000,000 sessions per day.

## Decision

- Server-side sessions are retained 30 days for audit.
- Hard requirement: in-progress bookings must never lose server-side
  session state.

## Consequences

Session storage is a durability-sensitive system; any change to it must
preserve the zero-loss requirement for in-progress bookings.
