CREATE TABLE tenants (
    id uuid PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE clients (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    name text NOT NULL,
    contact_email text NOT NULL
);

CREATE TABLE appointments (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    client_id uuid NOT NULL REFERENCES clients(id),
    starts_at timestamptz NOT NULL,
    status text NOT NULL DEFAULT 'booked'
);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON clients
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON appointments
    USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- seed rows (obviously synthetic)
INSERT INTO tenants (id, name) VALUES
    ('00000000-0000-0000-0000-00000000000a', 'Tenant A'),
    ('00000000-0000-0000-0000-00000000000b', 'Tenant B');
INSERT INTO clients (id, tenant_id, name, contact_email) VALUES
    ('00000000-0000-0000-0000-0000000000a1',
     '00000000-0000-0000-0000-00000000000a',
     'Tenant A Client 1', 'client1@example.com'),
    ('00000000-0000-0000-0000-0000000000b1',
     '00000000-0000-0000-0000-00000000000b',
     'Tenant B Client 1', 'client2@example.com');
