"""
embedder.py — Loads BAAI/bge-small-en-v1.5 locally and generates embeddings.

The model is ~33 MB and runs on CPU with no external API calls.
On first use it is downloaded to the HuggingFace cache (~/.cache/huggingface/).
Subsequent runs use the cached weights.
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Module-level singleton — loaded once per process
_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    """Load (or return the cached) embedding model."""
    global _model
    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        print("Model loaded.")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of strings.

    Args:
        texts: List of chunk text strings.

    Returns:
        List of 384-dim float vectors (one per input text).
    """
    model = load_model()
    # BGE models benefit from a query/passage prefix for asymmetric retrieval.
    # For indexing (passage side), we use the passage prefix.
    prefixed = [f"passage: {t}" for t in texts]
    embeddings = model.encode(prefixed, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()
