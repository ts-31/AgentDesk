"""
llm.py — LangChain LLM singleton for the RAG pipeline.

Uses the official langchain-xai integration (ChatXAI) rather than
ChatOpenAI with a custom base_url — ChatXAI has native support for
xAI-specific response fields that ChatOpenAI may silently drop.

The @lru_cache(maxsize=1) pattern keeps a single ChatXAI instance for
the lifetime of the process, consistent with the embedding model singleton
in indexing/embedder.py.
"""

from functools import lru_cache

from langchain_xai import ChatXAI

from config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatXAI:
    """Return the cached ChatXAI LLM instance configured for Grok."""
    return ChatXAI(
        model=settings.xai_model,
        xai_api_key=settings.xai_api_key,
    )
