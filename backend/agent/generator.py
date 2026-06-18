"""
generator.py — Grok answer generation for the RAG pipeline.

Accepts the user question and pre-retrieved, pre-filtered KB chunks,
builds a grounded prompt, and returns the generated answer text.

Kept intentionally separate from the router so that a future
LangChain / LangGraph integration can call generate_answer() directly
without any changes to the API layer.

SDK: xai-sdk (official xAI Python SDK, gRPC-based)
  - Client / AsyncClient: xai_sdk.Client, xai_sdk.AsyncClient
  - Message helpers: xai_sdk.chat.system, xai_sdk.chat.user
  - Completion: chat.create(...) → chat.append(...) → chat.sample()
"""

import logging
from xai_sdk import Client
from xai_sdk.chat import system, user
from config import settings

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = (
    "I'm sorry, I couldn't find relevant information in the knowledge base "
    "to answer your question. You may need to submit a support ticket for "
    "further assistance."
)

_SYSTEM_PROMPT = """You are a helpful TeamFlow support assistant.
Answer the user's question using ONLY the knowledge base excerpts provided below.
Be concise and accurate. If the excerpts do not contain enough information, say so honestly.
Do not make up facts not present in the excerpts."""


def _build_user_message(question: str, chunks: list[dict]) -> str:
    """Assemble the context block + question into a single user message."""
    context_blocks = "\n\n".join(
        f"[Source: {c['article_slug']}]\n{c['chunk_text']}"
        for c in chunks
    )
    return f"Knowledge base excerpts:\n\n{context_blocks}\n\nQuestion: {question}"


def generate_answer(question: str, chunks: list[dict]) -> str:
    """
    Send question + retrieved chunks to Grok and return the generated answer.

    Args:
        question: The original user question (already stripped).
        chunks:   List of similarity-filtered dicts from semantic_search(),
                  each containing at minimum: article_slug, chunk_text.

    Returns:
        Answer string produced by Grok.

    Raises:
        RuntimeError: Wraps any xAI SDK or network-level error so the caller
                      can surface a clean HTTP 502 without leaking SDK internals.
    """
    client = Client(api_key=settings.xai_api_key)
    try:
        chat = client.chat.create(
            model=settings.xai_model,
            messages=[system(_SYSTEM_PROMPT)],
        )
        chat.append(user(_build_user_message(question, chunks)))
        response = chat.sample()
        return response.content
    except Exception as exc:
        logger.error("Grok generation failed: %s", exc)
        raise RuntimeError(f"LLM generation error: {exc}") from exc
