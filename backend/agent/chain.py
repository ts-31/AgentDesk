"""
chain.py — LangGraph-backed RAG entry point.

This module is the single orchestration layer called by routers/agent.py.
run_rag() retains its original public signature and return contract —
the only internal change is that it delegates to the compiled StateGraph
in agent/graph.py instead of coordinating retrieval and generation directly.

The SQLAlchemy Session is forwarded to the graph as typed runtime context
(context=RAGContext(db=db)) via the official LangGraph Runtime[Context]
API. It is never embedded in the graph state, keeping RAGState clean and
serialization-safe for any future checkpointer.

Public surface:
  run_rag(question, db) -> dict  — called by routers/agent.py
"""

import logging

from sqlalchemy.orm import Session

from agent.graph import RAGContext, get_rag_graph

logger = logging.getLogger(__name__)


def run_rag(question: str, db: Session) -> dict:
    """
    Execute the full RAG pipeline via LangGraph and return a result dict.

    Delegates to the compiled StateGraph returned by get_rag_graph().
    The SQLAlchemy Session is passed as runtime context, not state.

    Args:
        question: The user question (already stripped and validated).
        db:       An active SQLAlchemy session.

    Returns:
        {"answer": str, "sources": list[str]}

        - answer  — generated answer string, or FALLBACK_ANSWER if no
                    chunks exceeded the similarity threshold.
        - sources — deduplicated article_slug list in retrieval order.

    Raises:
        RuntimeError: Wraps any LLM/network-level error so the router can
                      surface a clean HTTP 502 without leaking internals.
    """
    graph = get_rag_graph()
    try:
        result = graph.invoke(
            {"question": question},
            context=RAGContext(db=db),
        )
    except Exception as exc:
        logger.error("LangGraph RAG graph invocation failed: %s", exc)
        raise RuntimeError(f"LLM generation error: {exc}") from exc

    return {"answer": result["answer"], "sources": result["sources"]}
