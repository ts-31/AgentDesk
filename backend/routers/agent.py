"""
agent.py — POST /agent/ask: RAG endpoint.

This router is intentionally thin:
  - HTTP request/response shaping
  - Whitespace validation (delegated to AskRequest validator)
  - Dependency injection (DB session)

All retrieval, filtering, prompting, and generation logic lives in
agent/chain.py.  The router calls run_rag() and maps the result to
AskResponse — nothing more.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent.chain import run_rag
from database import get_db
from schemas.agent import AskRequest, AskResponse

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)):
    """
    RAG endpoint: retrieve KB chunks, generate a grounded answer with Grok,
    and return sources.

    Returns a fallback response (HTTP 200) when no chunks meet the similarity
    threshold.  Returns HTTP 502 if the LLM call fails.
    """
    try:
        result = run_rag(question=request.question, db=db)
    except RuntimeError as exc:
        logger.error("Agent /ask generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Answer generation failed. Please try again later.",
        )

    return AskResponse(answer=result["answer"], sources=result["sources"])
