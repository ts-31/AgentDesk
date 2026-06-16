"""
retriever.py — Vector similarity search against the knowledge_chunks table.

This module is intentionally isolated from the router so that a future
LangChain integration can call semantic_search() directly without any
changes to the API layer.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from indexing.embedder import embed_query


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
