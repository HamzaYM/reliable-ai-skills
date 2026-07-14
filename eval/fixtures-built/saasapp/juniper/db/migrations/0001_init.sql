-- Roles: juniper_owner owns the schema and runs migrations (ordinary LOGIN
-- role: not a superuser, no BYPASSRLS). juniper_app is the lower-privilege
-- runtime role.
CREATE ROLE juniper_owner LOGIN PASSWORD 'ownerpw';
CREATE ROLE juniper_app LOGIN PASSWORD 'apppw';

CREATE TABLE tenants (
    id uuid PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE appointments (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    patient_name text NOT NULL,
    starts_at timestamptz NOT NULL
);

GRANT SELECT, INSERT ON tenants, appointments TO juniper_app;

-- seed rows (obviously fictional placeholders)
INSERT INTO tenants (id, name) VALUES
    ('00000000-0000-0000-0000-00000000000a', 'Clinic A'),
    ('00000000-0000-0000-0000-00000000000b', 'Clinic B');
INSERT INTO appointments (id, tenant_id, patient_name, starts_at) VALUES
    ('00000000-0000-0000-0000-0000000000a1',
     '00000000-0000-0000-0000-00000000000a', 'Pat Example-1',
     '2026-07-10T09:00:00Z'),
    ('00000000-0000-0000-0000-0000000000b1',
     '00000000-0000-0000-0000-00000000000b', 'Sam Test-2',
     '2026-07-10T10:00:00Z');
