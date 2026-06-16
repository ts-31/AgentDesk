"""
chunker.py — Splits article body text into retrieval-friendly chunks.

Strategy:
  1. Split on ## section headings first (natural document boundaries).
  2. If any section exceeds MAX_WORDS, further split by paragraph with
     a rolling OVERLAP_WORDS word overlap to preserve context at boundaries.
"""

import re

MAX_WORDS = 200      # Maximum words per chunk
OVERLAP_WORDS = 30   # Words of overlap when splitting large sections


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text on blank lines, returning non-empty paragraph strings."""
    return [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]


def _words(text: str) -> list[str]:
    return text.split()


def _chunk_large_section(text: str) -> list[str]:
    """
    Break a section that exceeds MAX_WORDS into overlapping chunks.
    Works at paragraph granularity to avoid cutting mid-sentence.
    """
    paragraphs = _split_into_paragraphs(text)
    chunks = []
    current_words: list[str] = []

    for para in paragraphs:
        para_words = _words(para)

        if len(current_words) + len(para_words) > MAX_WORDS and current_words:
            chunks.append(" ".join(current_words))
            # Carry the last OVERLAP_WORDS words into the next chunk
            current_words = current_words[-OVERLAP_WORDS:]

        current_words.extend(para_words)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


def chunk_article(article: dict) -> list[dict]:
    """
    Split a loaded article into chunks.

    Args:
        article: dict with keys article_slug, article_title, tags, content

    Returns:
        List of chunk dicts with keys:
            article_slug, article_title, tags, chunk_index, chunk_text
    """
    content = article["content"]

    # Split on section headings (lines that were originally ## headings,
    # now plain text after stripping in loader). We re-split on double
    # newlines followed by a capitalised short line as a heuristic, or
    # simply treat each top-level paragraph block as a section.
    #
    # Simpler & more reliable: split on lines that look like section titles
    # (short, no period at end, not a list item).
    section_pattern = re.compile(r"\n(?=[A-Z][^\n]{3,60}\n)")
    raw_sections = section_pattern.split(content)
    sections = [s.strip() for s in raw_sections if s.strip()]

    # Fallback: if we got only one block, treat whole content as one section
    if len(sections) <= 1:
        sections = [content.strip()]

    chunks = []
    chunk_index = 0

    for section in sections:
        if len(_words(section)) <= MAX_WORDS:
            chunks.append(section)
        else:
            chunks.extend(_chunk_large_section(section))

    result = []
    for i, chunk_text in enumerate(chunks):
        if not chunk_text.strip():
            continue
        result.append({
            "article_slug": article["article_slug"],
            "article_title": article["article_title"],
            "tags": article["tags"],
            "chunk_index": i,
            "chunk_text": chunk_text.strip(),
        })

    return result
