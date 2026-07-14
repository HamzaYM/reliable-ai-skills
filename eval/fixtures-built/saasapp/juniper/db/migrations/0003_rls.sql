ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON appointments
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
