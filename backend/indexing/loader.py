"""
loader.py — Reads Markdown files from the knowledge_base directory.

Extracts:
  - article_slug  : filename without the .md extension
  - article_title : text of the first # heading
  - tags          : comma-separated string from the **Tags:** line
  - content       : everything after the first --- separator (the body)
"""

import os
import re
from pathlib import Path
from typing import Optional

KB_DIR = Path(__file__).parent.parent / "knowledge_base"


def _extract_title(text: str) -> str:
    """Return the first # heading found in the text."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    return "Untitled"


def _extract_tags(text: str) -> Optional[str]:
    """Return the comma-separated tag string from the **Tags:** line."""
    match = re.search(r"\*\*Tags:\*\*\s*(.+)", text)
    if match:
        return match.group(1).strip()
    return None


def _extract_body(text: str) -> str:
    """Return content after the first horizontal rule (---), stripped of markdown."""
    parts = re.split(r"\n---\n", text, maxsplit=1)
    body = parts[1] if len(parts) > 1 else text

    # Remove markdown formatting for cleaner chunk text
    body = re.sub(r"#+\s+", "", body)           # headings
    body = re.sub(r"\*\*(.+?)\*\*", r"\1", body)  # bold
    body = re.sub(r"\*(.+?)\*", r"\1", body)       # italic
    body = re.sub(r"`(.+?)`", r"\1", body)         # inline code
    body = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", body)  # links
    body = re.sub(r"^\|.+\|$", "", body, flags=re.MULTILINE)  # table rows
    body = re.sub(r"^[-|]+$", "", body, flags=re.MULTILINE)   # table dividers
    body = re.sub(r"^\s*>\s*", "", body, flags=re.MULTILINE)   # blockquotes
    body = re.sub(r"\n{3,}", "\n\n", body)          # collapse excess blank lines
    return body.strip()


def load_articles() -> list[dict]:
    """
    Load all .md files from the knowledge_base directory.

    Returns a list of dicts with keys:
        article_slug, article_title, tags, content
    """
    articles = []
    for md_file in sorted(KB_DIR.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        articles.append({
            "article_slug": md_file.stem,
            "article_title": _extract_title(raw),
            "tags": _extract_tags(raw),
            "content": _extract_body(raw),
        })
    return articles
