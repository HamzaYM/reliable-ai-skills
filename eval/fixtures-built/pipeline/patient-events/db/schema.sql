CREATE TABLE events (
    id bigserial PRIMARY KEY,
    user_id uuid NOT NULL,
    kind text NOT NULL,
    occurred_at timestamptz NOT NULL
);

CREATE TABLE user_data (
    user_id uuid PRIMARY KEY,
    profile jsonb NOT NULL
);

-- Hashed, PII-free record that consent was obtained.
CREATE TABLE consent_receipts (
    user_id uuid NOT NULL,
    consent_version_id integer NOT NULL REFERENCES consent_versions(id),
    captured_at timestamptz NOT NULL,
    receipt_hash text NOT NULL
);

-- Audit/history table: append-only. Rows are never updated or deleted; the
-- table serves as tamper evidence.
CREATE TABLE consent_audit (
    id bigserial PRIMARY KEY,
    user_id uuid NOT NULL,
    action text NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE consent_versions (
    id serial PRIMARY KEY,
    text text NOT NULL,
    published_at timestamptz NOT NULL DEFAULT now()
);
