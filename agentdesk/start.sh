#!/usr/bin/env bash
# start.sh — Single command to start the AgentDesk backend.
# Usage: bash start.sh (from the backend/ directory)

set -e  # Exit immediately on any error

# ---------------------------------------------------------------------------
# 1. Start the database container
# ---------------------------------------------------------------------------
echo "[DOCKER] Ensuring PostgreSQL & pgAdmin containers are running..."
docker compose up -d

# ---------------------------------------------------------------------------
# 2. Wait for PostgreSQL to accept connections (max 30s)
# ---------------------------------------------------------------------------
echo "[DB] Waiting for PostgreSQL to be ready..."
MAX_WAIT=30
COUNT=0
until docker exec agentdesk_db pg_isready -U agentdesk -d agentdesk_db > /dev/null 2>&1; do
  COUNT=$((COUNT + 1))
  if [ "$COUNT" -ge "$MAX_WAIT" ]; then
    echo "[ERROR] PostgreSQL did not become ready within ${MAX_WAIT}s. Is Docker running?"
    exit 1
  fi
  sleep 1
done
echo "[DB] PostgreSQL is ready."

# ---------------------------------------------------------------------------
# 3. Auto-index knowledge base articles if not already indexed
# ---------------------------------------------------------------------------
echo "[KB] Checking knowledge base index..."

TABLE_EXISTS=$(docker exec agentdesk_db psql -U agentdesk -d agentdesk_db -t -c \
  "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'knowledge_chunks');" \
  2>/dev/null | tr -d '[:space:]')

if [ "$TABLE_EXISTS" = "t" ]; then
  CHUNK_COUNT=$(docker exec agentdesk_db psql -U agentdesk -d agentdesk_db -t -c \
    "SELECT COUNT(*) FROM knowledge_chunks;" \
    2>/dev/null | tr -d '[:space:]')
else
  CHUNK_COUNT=0
fi

if [ "$CHUNK_COUNT" -gt 0 ] 2>/dev/null; then
  echo "[KB] Already indexed (${CHUNK_COUNT} chunks). Skipping."
else
  echo "[KB] Knowledge base is empty. Running indexer..."
  python indexing/index.py
  echo "[KB] Indexing complete."
fi

# ---------------------------------------------------------------------------
# 4. Start the FastAPI server
#    lifespan.py handles: init_db, pgvector, auto-seed mock data
# ---------------------------------------------------------------------------
echo "[START] Starting FastAPI server on http://127.0.0.1:8000 ..."
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
