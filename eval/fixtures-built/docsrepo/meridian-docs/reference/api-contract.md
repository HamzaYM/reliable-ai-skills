# API contract: POST /v2/charges

Request headers:
- Idempotency-Key: string, required for retried requests.

Request body: amount_cents (int), currency (string), tenant_id (string),
capture (bool, default true).

Response body: charge_id (string), status (string), amount_cents (int),
currency (string).

(No expiry duration or post-expiry behavior is specified here.)
