-- Database initialization script for PostgreSQL
-- This script runs when the PostgreSQL container is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- Text search improvements
CREATE EXTENSION IF NOT EXISTS "btree_gin";  -- GIN indexing for B-tree types

-- Create development and test databases if they don't exist
SELECT 'CREATE DATABASE app_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'app_dev')\gexec

SELECT 'CREATE DATABASE app_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'app_test')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE app_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE app_dev TO postgres;
GRANT ALL PRIVILEGES ON DATABASE app_test TO postgres;

-- Output success message
\echo 'Database initialization complete!'
\echo 'Available databases: app_db (default), app_dev, app_test'
