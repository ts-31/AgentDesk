"""
chain.py — LangGraph-backed RAG entry point.

This module is the single orchestration layer called by routers/agent.py.
run_rag() retains its original public signature and return contract —
the only internal changes are:
  1. It accepts an optional thread_id parameter.
  2. It builds a RunnableConfig with configurable["thread_id"] when one
     is provided, enabling the MemorySaver checkpointer to replay and
     persist conversation state for that thread.
  3. When thread_id is None (the default), config={} is passed and the
     graph behaves identically to the original stateless implementation.

The SQLAlchemy Session is forwarded to the graph as typed runtime context
(context=AgentContext(db=db)) via the official LangGraph Runtime[Context]
API. It is never embedded in the graph state, keeping AgentState clean and
serialization-safe for the checkpointer.

Public surface:
  run_rag(question, db, thread_id?) -> dict  — called by routers/agent.py
"""

import logging

from sqlalchemy.orm import Session

from agent.graph import AgentContext, get_rag_graph

logger = logging.getLogger(__name__)


def run_rag(question: str, db: Session, thread_id: str | None = None) -> dict:
    """
    Execute the full RAG pipeline via LangGraph and return a result dict.

    Delegates to the compiled StateGraph returned by get_rag_graph().
    The SQLAlchemy Session is passed as runtime context, not state.

    When thread_id is provided, LangGraph reads the checkpoint for that
    thread (replaying prior messages) and writes the updated state back
    after each invocation, enabling multi-turn conversation memory.

    Args:
        question:  The user question (already stripped and validated).
        db:        An active SQLAlchemy session.
        thread_id: Optional conversation identifier.  When provided,
                   the MemorySaver checkpointer replays and persists
                   messages for that thread.  When None, the graph runs
                   statelessly — identical to the pre-memory behavior.

    Returns:
        {"answer": str, "sources": list[str]}

        - answer  — generated answer string, or FALLBACK_ANSWER if no
                    chunks exceeded the similarity threshold.
        - sources — deduplicated article_slug list in retrieval order.

    Raises:
        RuntimeError: Wraps any LLM/network-level error so the router can
                      surface a clean HTTP 502 without leaking internals.
    """
    graph = get_rag_graph(with_memory=bool(thread_id))

    # Only activate the checkpointer when a thread_id is explicitly supplied.
    config: dict = {"configurable": {"thread_id": thread_id}} if thread_id else {}

    try:
        result = graph.invoke(
            {"question": question},
            config=config,
            context=AgentContext(db=db),
        )
    except Exception as exc:
        logger.error("LangGraph RAG graph invocation failed: %s", exc)
        raise RuntimeError(f"LLM generation error: {exc}") from exc

    return {"answer": result["answer"], "sources": result["sources"]}
