"""
memory.py — In-memory LangGraph checkpointer singleton.

MemorySaver stores all checkpoint data in a plain Python dict that lives
for the lifetime of the process.  It is intentionally NOT backed by
PostgreSQL — that is a future step.

Conversation history is keyed by thread_id (a free-form string supplied
by the API caller).  Threads expire when the process restarts.

Usage:
    from agent.memory import get_checkpointer
    graph = builder.compile(checkpointer=get_checkpointer())
"""
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver


@lru_cache(maxsize=1)
def get_checkpointer() -> MemorySaver:
    """Return the single shared MemorySaver for this process lifetime."""
    return MemorySaver()
