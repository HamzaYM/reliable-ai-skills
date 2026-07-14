# Architecture

## Payment integration

Every call to the payment provider goes through app/billing/gateway.py; the
only exception is app/billing/errors.py, which imports the provider error
classes.

## Invoice API

The Invoice API response contains exactly the fields: id, tenant_id,
amount_cents, currency, status.

## Webhooks

The integration handles 4 webhook event types: payment_succeeded,
payment_failed, refund_created, dispute_opened.
