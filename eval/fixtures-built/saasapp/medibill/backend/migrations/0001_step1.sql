CREATE TABLE invoice (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL,
    amount_cents integer NOT NULL,
    currency text NOT NULL,
    status text NOT NULL
);
