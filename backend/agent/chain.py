"""
chain.py — LangChain retrieval logic for the RAG pipeline.

This module is the single orchestration layer that replaced the ad-hoc
glue code previously spread across routers/agent.py. It uses native Python
orchestration around langchain-core primitives instead of legacy LCEL "chains".

Public surface:
  run_rag(question, db) -> dict  — called by routers/agent.py
"""

import logging

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


def run_rag(question: str, db: Session) -> dict:
    """
    Execute the full RAG pipeline and return a result dict.

    This is the single entry-point called by routers/agent.py. It uses
    pure Python to coordinate the retriever and the language model.

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
    # 1. Retrieve relevant chunks
    retriever = PgVectorRetriever(
        db=db,
        top_k=5,
        threshold=settings.rag_similarity_threshold,
    )
    docs = retriever.invoke(question)

    # 2. Check threshold fallback
    if not docs:
        logger.info(
            "No KB chunks above threshold %.2f for question: %r",
            settings.rag_similarity_threshold,
            question,
        )
        return {"answer": FALLBACK_ANSWER, "sources": []}

    # 3. Format the context block preserving [Source: slug] headers
    context = "\n\n".join(
        f"[Source: {doc.metadata['article_slug']}]\n{doc.page_content}"
        for doc in docs
    )

    # 4. Generate the answer
    try:
        # Note: prompt expects {input} for the question and {context} for the documents
        prompt = RAG_PROMPT.invoke({"input": question, "context": context})
        response = get_llm().invoke(prompt)
    except Exception as exc:
        logger.error("LangChain LLM invocation failed: %s", exc)
        raise RuntimeError(f"LLM generation error: {exc}") from exc

    # 5. Extract and deduplicate sources while preserving retrieval order
    seen: set[str] = set()
    sources = [
        d.metadata["article_slug"]
        for d in docs
        if not (d.metadata["article_slug"] in seen
                or seen.add(d.metadata["article_slug"]))  # type: ignore[func-returns-value]
    ]

    return {"answer": response.content, "sources": sources}
