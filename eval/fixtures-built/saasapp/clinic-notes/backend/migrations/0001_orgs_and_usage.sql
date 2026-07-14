CREATE TABLE organizations (
    id uuid PRIMARY KEY,
    name text NOT NULL,
    monthly_cap_usd numeric NOT NULL DEFAULT 250
);

CREATE TABLE llm_usage (
    id bigserial PRIMARY KEY,
    org_id uuid,
    model text NOT NULL,
    input_tokens integer NOT NULL,
    output_tokens integer NOT NULL,
    cost_usd numeric NOT NULL
);

CREATE TABLE cap_block_events (
    id bigserial PRIMARY KEY,
    org_id uuid,
    spend_usd numeric NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
