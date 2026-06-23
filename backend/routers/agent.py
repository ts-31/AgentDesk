"""
agent.py — POST /agent/ask: RAG endpoint (authentication-protected).

This router is intentionally thin:
  - HTTP request/response shaping
  - Whitespace validation (delegated to AskRequest validator)
  - Authentication via get_current_user dependency
  - Dependency injection (DB session)

All retrieval, filtering, prompting, and generation logic lives in
agent/chain.py.  The router calls run_rag() with the authenticated user's
identity fields (sourced from the validated JWT) so that CRM tools can use
customer_id directly without prompting the user.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent.chain import run_rag
from auth.dependencies import get_current_user
from database import get_db
from models import User
from schemas.agent import AskRequest, AskResponse

router = APIRouter(prefix="/agent", tags=["Agent"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    RAG endpoint: retrieve KB chunks, generate a grounded answer with Grok,
    and return sources.

    The authenticated user's customer_id is forwarded to run_rag() so the
    ReAct agent's CRM tools automatically scope all data lookups to the
    logged-in user's workspace — no need to ask for UUIDs.

    Returns a fallback response (HTTP 200) when no chunks meet the similarity
    threshold.  Returns HTTP 502 if the LLM call fails.
    """
    try:
        result = run_rag(
            question=request.question,
            db=db,
            thread_id=request.thread_id,
            user_id=str(current_user.user_id),
            customer_id=str(current_user.customer_id),
            user_email=current_user.email,
            user_role=current_user.role,
        )
    except RuntimeError as exc:
        logger.error("Agent /ask generation failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Answer generation failed. Please try again later.",
        )

    return AskResponse(answer=result["answer"], sources=result["sources"])
