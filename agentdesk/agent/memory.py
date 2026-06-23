"""
memory.py — PostgreSQL-backed LangGraph checkpointer singleton.

PostgresSaver (from langgraph-checkpoint-postgres) stores checkpoint data
in four tables inside the existing agentdesk_db PostgreSQL database.
Conversation history is keyed by thread_id and survives process restarts.

Lifecycle
---------
1. Call init_checkpointer(db_url) once during FastAPI startup (lifespan).
   This opens a psycopg ConnectionPool and calls checkpointer.setup(),
   which creates the four LangGraph tables if they do not already exist.
   setup() is idempotent — safe to call on every startup.

2. Call get_checkpointer() wherever the compiled graph is needed.
   Returns the single shared PostgresSaver for this process lifetime.

3. Call close_checkpointer() during FastAPI shutdown (lifespan teardown).
   This closes the connection pool gracefully.

Usage (from graph.py — unchanged):
    from agent.memory import get_checkpointer
    graph = builder.compile(checkpointer=get_checkpointer())

Why psycopg (Psycopg 3)?
    langgraph-checkpoint-postgres requires Psycopg 3 (psycopg package).
    The existing SQLAlchemy layer continues to use psycopg2-binary and is
    unaffected. Both drivers coexist without conflict.

Why ConnectionPool?
    A single raw psycopg connection is not safe for concurrent requests.
    ConnectionPool manages a pool of connections, handles recycling, and
    is the officially recommended approach for production workloads.
"""
from __future__ import annotations

import logging

import psycopg_pool
from langgraph.checkpoint.postgres import PostgresSaver

logger = logging.getLogger(__name__)

_pool: psycopg_pool.ConnectionPool | None = None
_checkpointer: PostgresSaver | None = None


def _to_psycopg_url(database_url: str) -> str:
    """
    Convert a SQLAlchemy-style database URL to a plain psycopg3 URL.

    SQLAlchemy uses dialect prefixes such as 'postgresql+psycopg2://' or
    'postgresql+psycopg://'.  Psycopg 3 only accepts 'postgresql://'.
    """
    return database_url.replace("postgresql+psycopg2://", "postgresql://") \
                       .replace("postgresql+psycopg://", "postgresql://")


def init_checkpointer(database_url: str) -> None:
    """
    Open a connection pool and initialise the PostgresSaver.

    Must be called exactly once during application startup before any
    graph invocation.  Calling it again is a no-op (guards against
    accidental double-init).

    Args:
        database_url: The DATABASE_URL from settings. Accepts both plain
                      'postgresql://' and SQLAlchemy dialect-prefixed forms.
    """
    global _pool, _checkpointer

    if _checkpointer is not None:
        logger.debug("Checkpointer already initialised — skipping.")
        return

    pg_url = _to_psycopg_url(database_url)

    logger.info("Opening psycopg ConnectionPool for LangGraph checkpointer...")
    _pool = psycopg_pool.ConnectionPool(
        conninfo=pg_url,
        min_size=1,
        max_size=5,
        kwargs={"autocommit": True, "row_factory": _dict_row_factory()},
        open=True,
    )

    _checkpointer = PostgresSaver(_pool)

    logger.info("Running PostgresSaver.setup() — creating checkpoint tables if needed...")
    _checkpointer.setup()

    logger.info("PostgresSaver checkpointer initialised.")


def get_checkpointer() -> PostgresSaver:
    """
    Return the process-scoped PostgresSaver.

    Raises:
        RuntimeError: If init_checkpointer() has not been called yet.
    """
    if _checkpointer is None:
        raise RuntimeError(
            "Checkpointer is not initialised. "
            "Ensure init_checkpointer() is called during application startup."
        )
    return _checkpointer


def close_checkpointer() -> None:
    """
    Close the connection pool gracefully.

    Should be called during application shutdown (lifespan teardown).
    Safe to call even if init_checkpointer() was never called.
    """
    global _pool, _checkpointer
    if _pool is not None:
        logger.info("Closing psycopg ConnectionPool...")
        _pool.close()
        _pool = None
        _checkpointer = None
        logger.info("PostgresSaver checkpointer closed.")


def _dict_row_factory():
    """Return psycopg's dict_row factory (imported lazily to avoid top-level errors)."""
    from psycopg.rows import dict_row
    return dict_row
