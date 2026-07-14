CREATE TABLE tenants (id uuid PRIMARY KEY, subdomain text, name text);
CREATE TABLE desks (id uuid PRIMARY KEY, tenant_id uuid, label text);
CREATE TABLE bookings (
    id uuid PRIMARY KEY,
    tenant_id uuid,
    desk_id uuid,
    day date,
    hour integer,
    created_at timestamptz DEFAULT now()
);
