from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from search.retriever import semantic_search
from schemas.knowledge_base import KnowledgeSearchResponse, KnowledgeSearchResult
from auth.dependencies import get_current_user

router = APIRouter(
    prefix="/knowledge-base",
    tags=["Knowledge Base"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge_base(
    q: str = Query(..., description="Natural language search query"),
    limit: int = Query(default=5, ge=1, le=20, description="Number of results to return (1-20)"),
    db: Session = Depends(get_db),
):
    """
    Perform semantic search against the TeamFlow knowledge base.

    Embeds the query using BGE-small and returns the top matching
    chunks ranked by cosine similarity.
    """
    # Validate query is not empty or whitespace-only
    if not q or not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Query parameter 'q' must not be empty or whitespace.",
        )

    raw_results = semantic_search(query=q.strip(), db=db, top_k=limit)

    return KnowledgeSearchResponse(
        query=q.strip(),
        results=[KnowledgeSearchResult(**r) for r in raw_results],
    )
