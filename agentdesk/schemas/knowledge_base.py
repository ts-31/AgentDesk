from pydantic import BaseModel


class KnowledgeSearchResult(BaseModel):
    article_title: str
    article_slug: str
    chunk_text: str
    similarity_score: float


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResult]
