"""
chain.py — LangGraph-backed agent entry point.

This module is the single orchestration layer called by routers/agent.py.
run_rag() retains its original public signature and return contract.

Changes from the intent-routing version:
  - The graph is now a ReAct loop (agent → tools → agent) rather than a
    classify → branch architecture. graph.py handles this entirely.
  - Result extraction (Option A): after graph.invoke() returns, run_rag()
    reads the final AIMessage from result["messages"] for the answer text,
    and parses "[Source: slug]" headers from any retrieve_kb ToolMessages
    for the sources list. No additional state keys are needed.

Fix — sources bleed across turns:
  graph.get_state() is called BEFORE graph.invoke() to snapshot the number
  of messages already in the checkpoint.  After invoke, only the slice
  result["messages"][prior_count:] (this turn's new messages) is passed to
  _extract_sources, so prior-turn retrieve_kb results never bleed through.

Public surface (unchanged):
  run_rag(question, db, thread_id?) -> dict  — called by routers/agent.py
  Return shape: {"answer": str, "sources": list[str]}
"""

import logging
import re

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError
from sqlalchemy.orm import Session

from agent.graph import AgentContext, get_rag_graph

logger = logging.getLogger(__name__)

_TECHNICAL_FALLBACK = (
    "I was unable to generate a response. Please try again or contact support."
)

# Regex to pull slugs from "[Source: some-article-slug]" lines produced by
# the retrieve_kb tool.  Non-greedy match keeps it tight.
_SOURCE_PATTERN = re.compile(r"^\[Source:\s*(.+?)\]$", re.MULTILINE)


def _extract_answer(messages: list) -> str:
    """Return the content of the last AIMessage, or the technical fallback."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and isinstance(msg.content, str):
            return msg.content
    return _TECHNICAL_FALLBACK


def _extract_sources(messages: list) -> list[str]:
    """
    Parse deduplicated article slugs from all retrieve_kb ToolMessages.

    retrieve_kb embeds slugs as "[Source: slug]" header lines in its return
    value, which LangGraph stores as ToolMessage.content.  Ordering mirrors
    retrieval order across all retrieve_kb calls in the turn.
    """
    seen: set[str] = set()
    sources: list[str] = []
    for msg in messages:
        if (
            isinstance(msg, ToolMessage)
            and getattr(msg, "name", None) == "retrieve_kb"
            and isinstance(msg.content, str)
        ):
            for slug in _SOURCE_PATTERN.findall(msg.content):
                if slug not in seen:
                    sources.append(slug)
                    seen.add(slug)
    return sources


def _snapshot_prior_message_count(graph, config: dict) -> int:
    """
    Return the number of messages already persisted in the thread checkpoint
    before this invocation begins.

    This boundary lets run_rag() slice result["messages"][prior_count:] to
    isolate only the messages produced in the *current* turn, preventing
    retrieve_kb ToolMessages from prior turns bleeding into this turn's sources.

    Returns 0 when:
      - config is empty (stateless mode — no checkpointer active)
      - the thread has no prior checkpoint (very first turn)
      - graph.get_state() raises for any reason
    """
    if not config:
        return 0
    try:
        prior_state = graph.get_state(config)
        return len(prior_state.values.get("messages", []))
    except Exception as exc:
        logger.debug("Could not snapshot prior message count: %s", exc)
        return 0


def run_rag(
    question: str,
    db: Session,
    thread_id: str | None = None,
    user_id: str = "",
    customer_id: str = "",
    user_email: str = "",
    user_role: str = "",
) -> dict:
    """
    Execute the ReAct agent via LangGraph and return a result dict.

    The SQLAlchemy Session is passed as runtime context (AgentContext), not
    embedded in graph state, keeping AgentState serialization-safe for the
    PostgreSQL checkpointer.

    When thread_id is provided, LangGraph reads the checkpoint for that
    thread (replaying prior messages) and writes the updated state back
    after the invocation, enabling multi-turn conversation memory.

    Args:
        question:    The user question (already stripped and validated).
        db:          An active SQLAlchemy session.
        thread_id:   Optional conversation identifier.  When provided,
                     the PostgresSaver checkpointer replays and persists
                     messages for that thread.  When None, the graph runs
                     statelessly.
        user_id:     UUID string of the authenticated user (from JWT).
        customer_id: UUID string of the user's customer/workspace (from JWT).
                     CRM tools read this directly — no need to ask the user.
        user_email:  Authenticated user's email (from JWT).
        user_role:   Authenticated user's role, e.g. "Member" (from JWT).

    Returns:
        {"answer": str, "sources": list[str]}

        - answer  — The last AIMessage content produced by the ReAct agent
                    in this turn, or a technical fallback if none was generated.
        - sources — Deduplicated article slugs from retrieve_kb ToolMessages
                    produced in this turn only.  Empty list when the agent
                    answered without calling retrieve_kb this turn.

    Raises:
        RuntimeError: Wraps any LLM/network-level error so the router can
                      surface a clean HTTP 502 without leaking internals.
    """
    graph = get_rag_graph(with_memory=bool(thread_id))

    config: dict = {"configurable": {"thread_id": thread_id}} if thread_id else {}
    # Hard circuit breaker: limit the ReAct loop to 5 internal steps to prevent
    # infinite LLM retries (and API credit drain) on systemic tool errors.
    config["recursion_limit"] = 5

    # Snapshot how many messages are already in the checkpoint BEFORE this
    # invocation so we can slice off only the new messages afterwards.
    prior_count = _snapshot_prior_message_count(graph, config)

    try:
        result = graph.invoke(
            {"question": question, "messages": []},
            config=config,
            context=AgentContext(
                db=db,
                user_id=user_id,
                customer_id=customer_id,
                user_email=user_email,
                user_role=user_role,
            ),
        )
    except GraphRecursionError:
        logger.warning("Graph recursion limit reached. Halting ReAct loop to protect API credits.")
        # We don't raise an error here. By catching it, we let the code below
        # extract whatever partial answer or tool messages were generated before
        # the loop was forcibly terminated.
        result = {}
        if thread_id:
            # Attempt to pull the current state from memory since invoke() aborted.
            try:
                result = graph.get_state(config).values
            except Exception:
                pass
    except Exception as exc:
        logger.error("LangGraph ReAct graph invocation failed: %s", exc)
        raise RuntimeError(f"LLM generation error: {exc}") from exc

    all_messages = result.get("messages", [])

    # Isolate only the messages added during this turn.
    # Falls back to the full list when prior_count is 0 (stateless or first turn).
    current_turn_messages = all_messages[prior_count:]

    return {
        # Prefer the last AIMessage from this turn; fall back to full history
        # as a safety net in the unlikely event this turn produced none.
        "answer": _extract_answer(current_turn_messages) or _extract_answer(all_messages),
        "sources": _extract_sources(current_turn_messages),
    }
