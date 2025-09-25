-- Initialize MrDoors database
-- PostgreSQL doesn't support IF NOT EXISTS for CREATE DATABASE
-- The database is already created by POSTGRES_DB environment variable

-- Create user if not exists (PostgreSQL syntax)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'mrdoors_user') THEN

      CREATE ROLE mrdoors_user LOGIN PASSWORD 'mrdoors_password';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mrdoors TO mrdoors_user;