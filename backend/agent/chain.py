"""
chain.py — LangChain LCEL (LangChain Expression Language) retrieval chain for the RAG pipeline.

This module is the single orchestration layer that replaced the ad-hoc
glue code previously spread across routers/agent.py.

Public surface:
  run_rag(question, db) -> dict  — called by routers/agent.py
  FALLBACK_ANSWER               — re-exported so the router can reference it

Internal chain structure (LCEL):
  PgVectorRetriever
    → create_stuff_documents_chain(ChatXAI, RAG_PROMPT)
    → create_retrieval_chain(retriever, document_chain)

create_retrieval_chain returns:
  {"input": str, "context": list[Document], "answer": str}

The "context" list is used here to extract deduplicated article_slug sources,
preserving the same source ordering logic that was in the original router.
"""

import logging
from typing import Any

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import PromptTemplate
from sqlalchemy.orm import Session

from agent.llm import get_llm
from agent.prompt import RAG_PROMPT
from config import settings
from search.retriever import PgVectorRetriever

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = (
    "I'm sorry, I couldn't find relevant information in the knowledge base "
    "to answer your question. You may need to submit a support ticket for "
    "further assistance."
)

# Per-document prompt: preserves the [Source: slug] header format that Grok
# previously received from _build_user_message() in the old generator.py.
_DOCUMENT_PROMPT = PromptTemplate.from_template(
    "[Source: {article_slug}]\n{page_content}"
)


def build_rag_chain(db: Session) -> Any:
    """
    Construct a per-request LCEL retrieval chain.

    The retriever is instantiated with the caller's DB session so that
    SQLAlchemy's connection-per-request lifecycle is respected — no
    session is held open beyond the request that created this chain.

    Args:
        db: An active SQLAlchemy session (injected by FastAPI Depends).

    Returns:
        A LangChain Runnable that accepts {"input": question_str} and
        returns {"input", "context", "answer"}.
    """
    retriever = PgVectorRetriever(
        db=db,
        top_k=5,
        threshold=settings.rag_similarity_threshold,
    )
    document_chain = create_stuff_documents_chain(
        llm=get_llm(),
        prompt=RAG_PROMPT,
        document_prompt=_DOCUMENT_PROMPT,
    )
    return create_retrieval_chain(retriever, document_chain)


def run_rag(question: str, db: Session) -> dict:
    """
    Execute the full RAG pipeline and return a result dict.

    This is the single entry-point called by routers/agent.py, keeping
    the router free of any chain or retrieval logic.

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
    chain = build_rag_chain(db)

    try:
        result = chain.invoke({"input": question})
    except Exception as exc:
        logger.error("LangChain chain invocation failed: %s", exc)
        raise RuntimeError(f"LLM generation error: {exc}") from exc

    docs = result.get("context", [])

    # No chunks passed the similarity threshold — return the standard fallback
    if not docs:
        logger.info(
            "No KB chunks above threshold %.2f for question: %r",
            settings.rag_similarity_threshold,
            question,
        )
        return {"answer": FALLBACK_ANSWER, "sources": []}

    # Deduplicate slugs while preserving retrieval order — same logic as the
    # original router (the walrus-operator trick is kept for consistency).
    seen: set[str] = set()
    sources = [
        d.metadata["article_slug"]
        for d in docs
        if not (d.metadata["article_slug"] in seen
                or seen.add(d.metadata["article_slug"]))  # type: ignore[func-returns-value]
    ]

    return {"answer": result["answer"], "sources": sources}
