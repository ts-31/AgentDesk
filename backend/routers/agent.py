"""
agent.py — POST /agent/ask: RAG endpoint.

This router is intentionally thin:
  - HTTP request/response shaping
  - Whitespace validation (delegated to AskRequest validator)
  - Similarity threshold filtering
  - Dependency injection (DB session)

Retrieval is handled by search/retriever.py.
Generation is handled by agent/generator.py.
Neither module is aware of FastAPI or HTTP.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from config import settings
from search.retriever import semantic_search
from agent.generator import generate_answer, FALLBACK_ANSWER
from schemas.agent import AskRequest, AskResponse

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)):
    """
    RAG endpoint: retrieve KB chunks, filter by similarity threshold,
    generate a grounded answer with Grok, and return sources.

    Returns a fallback response (HTTP 200) when no chunks meet the threshold.
    Returns HTTP 502 if the Grok API call fails.
    """
    # 1. Retrieve top-5 candidates via pgvector cosine similarity
    raw_chunks = semantic_search(query=request.question, db=db, top_k=5)

    # 2. Filter to only chunks that meet the configured similarity threshold
    filtered_chunks = [
        c for c in raw_chunks
        if c["similarity_score"] >= settings.rag_similarity_threshold
    ]

    # 3. Fallback: no relevant chunks found in the knowledge base
    if not filtered_chunks:
        logger.info(
            "No KB chunks above threshold %.2f for question: %r",
            settings.rag_similarity_threshold,
            request.question,
        )
        return AskResponse(answer=FALLBACK_ANSWER, sources=[])

    # 4. Generate a grounded answer using the filtered context
    try:
        answer = generate_answer(question=request.question, chunks=filtered_chunks)
    except RuntimeError as exc:
        logger.error("Agent /ask generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Answer generation failed. Please try again later.",
        )

    # 5. Build sources list only from chunks that were sent to Grok,
    #    preserving order while deduplicating slugs.
    seen: set[str] = set()
    sources = [
        c["article_slug"] for c in filtered_chunks
        if not (c["article_slug"] in seen or seen.add(c["article_slug"]))  # type: ignore[func-returns-value]
    ]

    return AskResponse(answer=answer, sources=sources)
