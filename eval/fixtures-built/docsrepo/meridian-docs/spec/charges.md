# Charges endpoint spec (v3, current)

POST /v2/charges

Idempotency: pass an Idempotency-Key header. Keys expire 72 hours after
first use. When a request arrives with an already-expired key, the endpoint
replays the previously stored response.

Fields: amount_cents, currency, tenant_id, capture (bool).
