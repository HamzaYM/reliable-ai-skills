CREATE TABLE patients (
    id uuid PRIMARY KEY,
    display_name text NOT NULL,
    contact_email text NOT NULL,
    contact_sms text NOT NULL
);

CREATE TABLE consent (
    patient_id uuid PRIMARY KEY REFERENCES patients(id),
    notifications_enabled boolean NOT NULL DEFAULT true,
    marketing_enabled boolean NOT NULL DEFAULT false
);
