"""
retriever.py — Vector similarity search against the knowledge_chunks table.

This module provides two interfaces:

1. semantic_search() — original function-based API.
   Still used by GET /knowledge-base/search.  Unchanged.

2. PgVectorRetriever — LangChain BaseRetriever wrapping semantic_search().
   Used by run_rag() in agent/chain.py.
   Similarity threshold filtering is applied here so the chain receives only
   documents that passed the threshold (an empty list triggers the fallback).
"""

from typing import Any, List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from indexing.embedder import embed_query


# ---------------------------------------------------------------------------
# Original function-based API — unchanged
# ---------------------------------------------------------------------------

def semantic_search(
    query: str,
    db: Session,
    top_k: int = 5,
) -> list[dict]:
    """
    Embed a natural language query and return the top_k most similar KB chunks.

    Args:
        query:  The raw natural language query string.
        db:     An active SQLAlchemy session.
        top_k:  Number of results to return (default 5).

    Returns:
        List of dicts with keys: article_title, article_slug,
        chunk_text, similarity_score.
    """
    query_vector = embed_query(query)

    # pgvector cosine distance operator: <=>
    # similarity = 1 - cosine_distance (valid because embeddings are L2-normalised)
    sql = text("""
        SELECT
            article_title,
            article_slug,
            chunk_text,
            1 - (embedding <=> CAST(:query_vec AS vector)) AS similarity_score
        FROM knowledge_chunks
        ORDER BY embedding <=> CAST(:query_vec AS vector)
        LIMIT :top_k
    """)

    rows = db.execute(sql, {
        "query_vec": str(query_vector),
        "top_k": top_k,
    }).fetchall()

    return [
        {
            "article_title": row.article_title,
            "article_slug": row.article_slug,
            "chunk_text": row.chunk_text,
            "similarity_score": round(float(row.similarity_score), 4),
        }
        for row in rows
    ]


# ---------------------------------------------------------------------------
# LangChain retriever — wraps semantic_search() as a BaseRetriever
# ---------------------------------------------------------------------------

class PgVectorRetriever(BaseRetriever):
    """
    LangChain-compatible retriever backed by the existing pgvector SQL pipeline.

    Instantiate per-request with the active SQLAlchemy session so that
    connection lifecycle is tied to the FastAPI request (via Depends(get_db)).

    Attributes:
        db:        Active SQLAlchemy Session.
        top_k:     Maximum raw candidates to fetch from pgvector (pre-filter).
        threshold: Minimum similarity_score to include in results.
                   Mirrors settings.rag_similarity_threshold.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    db: Any          # Session — typed as Any to satisfy Pydantic's model check
    top_k: int = 5
    threshold: float = 0.75

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """
        Retrieve and threshold-filter pgvector results, returning Documents.

        An empty list signals to chain.py that no chunks met the threshold,
        which triggers the standard fallback response — identical behaviour to
        the inline filter that was previously in routers/agent.py.
        """
        raw = semantic_search(query=query, db=self.db, top_k=self.top_k)
        filtered = [c for c in raw if c["similarity_score"] >= self.threshold]

        return [
            Document(
                page_content=c["chunk_text"],
                metadata={
                    "article_title":    c["article_title"],
                    "article_slug":     c["article_slug"],
                    "similarity_score": c["similarity_score"],
                },
            )
            for c in filtered
        ]
