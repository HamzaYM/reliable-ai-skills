# Charges service design

The charges service serializes concurrent submissions with a Redis lock per
idempotency key: the first request takes the lock, processes the charge,
and stores the response; competing requests block on the lock and then read
the stored response. Locks are held for the duration of processing and
expire after 30 seconds as a liveness guard.

The Redis lock table is the source of truth for in-flight charges.
