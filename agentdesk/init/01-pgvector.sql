-- Enable pgvector extension for the agentdesk database.
-- This script runs automatically when the container is first created
-- via the docker-entrypoint-initdb.d mechanism.
CREATE EXTENSION IF NOT EXISTS vector;
