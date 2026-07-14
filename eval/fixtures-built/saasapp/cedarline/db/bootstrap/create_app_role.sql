-- One-time bootstrap: dedicated application role. Not part of automatic
-- database initialization; run by hand on first setup.
CREATE ROLE cedar_app LOGIN PASSWORD 'apppw';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cedar_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cedar_app;
