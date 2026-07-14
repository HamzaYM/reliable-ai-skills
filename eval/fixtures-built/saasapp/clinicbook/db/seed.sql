-- Obviously synthetic seed data. No dates of birth, government ids, or
-- record numbers. Contact addresses are under example.com.
INSERT INTO tenants (id, name) VALUES (1, 'Clinic Alpha'), (2, 'Clinic Beta');
INSERT INTO patients (id, tenant_id, display_name, contact_email) VALUES
    (1, 1, 'Patient A-001', 'a001@example.com'),
    (2, 1, 'Patient A-002', 'a002@example.com'),
    (3, 2, 'Patient B-014', 'b014@example.com'),
    (4, 2, 'Patient B-015', 'b015@example.com');
