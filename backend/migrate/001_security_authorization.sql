-- Security/authorization migration for an existing PostgreSQL MPLADS database.
-- Run this once against the existing database before starting the upgraded API.
--
-- If the database is brand new, Base.metadata.create_all() creates these objects
-- automatically; this file is for existing installations.

ALTER TYPE userrole RENAME VALUE 'state_official' TO 'state';
ALTER TYPE userrole RENAME VALUE 'district_official' TO 'district';
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ministry';

ALTER TABLE users ADD COLUMN IF NOT EXISTS constituency_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS district_id VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS state_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS ix_users_constituency_id ON users (constituency_id);
CREATE INDEX IF NOT EXISTS ix_users_district_id ON users (district_id);
CREATE INDEX IF NOT EXISTS ix_users_state_id ON users (state_id);

ALTER TABLE works ADD COLUMN IF NOT EXISTS state_id VARCHAR(100);
ALTER TABLE works ADD COLUMN IF NOT EXISTS district_id VARCHAR(100);
ALTER TABLE works ADD COLUMN IF NOT EXISTS constituency_id VARCHAR(100);

CREATE INDEX IF NOT EXISTS ix_works_state_id ON works (state_id);
CREATE INDEX IF NOT EXISTS ix_works_district_id ON works (district_id);
CREATE INDEX IF NOT EXISTS ix_works_constituency_id ON works (constituency_id);

ALTER TABLE grievances ADD COLUMN IF NOT EXISTS submitted_by_user_id VARCHAR(100);
CREATE INDEX IF NOT EXISTS ix_grievances_submitted_by_user_id
    ON grievances (submitted_by_user_id);

CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100),
    username VARCHAR(255),
    role VARCHAR(50),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    ip_address VARCHAR(64),
    user_agent TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'SUCCESS',
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS ix_audit_logs_resource_id ON audit_logs (resource_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp);

CREATE TABLE IF NOT EXISTS report_signatures (
    id VARCHAR(36) PRIMARY KEY,
    report_id VARCHAR(100) UNIQUE NOT NULL,
    report_hash VARCHAR(64) NOT NULL,
    signature TEXT NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    signed_by VARCHAR(100) NOT NULL,
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_report_signatures_report_id
    ON report_signatures (report_id);
