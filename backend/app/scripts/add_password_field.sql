-- Add password_hash field to employees table
-- Run this migration against your database

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL;

COMMENT ON COLUMN employees.password_hash IS 'Bcrypt hashed password for local auth';
