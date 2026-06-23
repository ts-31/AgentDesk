"""
index.py — Standalone indexing script.

Run from the backend/ directory with the DB container running:
    python indexing/index.py

Workflow:
  1. Load all .md articles from knowledge_base/
  2. Chunk each article
  3. Generate embeddings for all chunks
  4. Wipe existing rows for each article_slug (idempotent)
  5. Insert new KnowledgeChunk rows into PostgreSQL

Idempotency: re-running this script is safe — it replaces all rows for
each article before re-inserting, so no duplicates accumulate.
"""

import sys
import os

# Allow running as `python indexing/index.py` from the backend/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, init_db, enable_pgvector
from models.knowledge_chunk import KnowledgeChunk
from indexing.loader import load_articles
from indexing.chunker import chunk_article
from indexing.embedder import embed_texts


def run_indexing():
    print("\n=== TeamFlow Knowledge Base Indexer ===\n")

    # Ensure pgvector extension and table exist
    enable_pgvector()
    init_db()

    articles = load_articles()
    if not articles:
        print("No articles found in knowledge_base/. Exiting.")
        return

    print(f"Found {len(articles)} article(s).\n")

    # Load the model once before opening the DB session
    all_chunks: list[dict] = []
    for article in articles:
        chunks = chunk_article(article)
        all_chunks.extend(chunks)
        print(f"  {article['article_slug']}: {len(chunks)} chunk(s)")

    print(f"\nTotal chunks to index: {len(all_chunks)}")
    print("\nGenerating embeddings (this may take a moment on first run)...")

    texts = [c["chunk_text"] for c in all_chunks]
    embeddings = embed_texts(texts)

    print("Embeddings generated. Writing to database...\n")

    db = SessionLocal()
    try:
        # Group chunks by slug and upsert article-by-article
        slugs_seen: set[str] = set()
        for chunk_data, embedding in zip(all_chunks, embeddings):
            slug = chunk_data["article_slug"]

            # Delete existing rows for this slug on first encounter
            if slug not in slugs_seen:
                deleted = db.query(KnowledgeChunk).filter(
                    KnowledgeChunk.article_slug == slug
                ).delete()
                if deleted:
                    print(f"  [{slug}] Replaced {deleted} existing chunk(s).")
                slugs_seen.add(slug)

            chunk = KnowledgeChunk(
                article_slug=chunk_data["article_slug"],
                article_title=chunk_data["article_title"],
                tags=chunk_data["tags"],
                chunk_index=chunk_data["chunk_index"],
                chunk_text=chunk_data["chunk_text"],
                embedding=embedding,
            )
            db.add(chunk)

        db.commit()
        print(f"\n[OK] Done. {len(all_chunks)} chunk(s) indexed across {len(articles)} article(s).")

        # Print a quick summary from the DB to confirm
        print("\n--- Stored chunk counts ---")
        for slug in sorted(slugs_seen):
            count = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.article_slug == slug
            ).count()
            print(f"  {slug}: {count} chunk(s)")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error during indexing: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_indexing()
