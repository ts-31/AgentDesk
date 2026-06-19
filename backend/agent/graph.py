"""
graph.py — LangGraph RAG workflow for TeamFlow.

Defines a two-node StateGraph that reproduces the behaviour of the
original run_rag() using the official LangGraph Runtime[Context] API
for per-request dependency injection.

Graph topology:
  START ──▶ retrieve ──▶ generate ──▶ END

No checkpointer, no memory, no conditional edges.
The compiled graph is cached via @lru_cache for the process lifetime.

Runtime context vs. graph state
────────────────────────────────
RAGContext holds the SQLAlchemy Session because:
  - Sessions are not JSON-serializable — they cannot live in State.
  - Runtime context is never checkpointed or replayed by LangGraph.
  - This cleanly separates infrastructure concerns from graph data.
  - RunnableConfig.configurable is designed for configuration parameters
    (model name, temperature, flags), not stateful infrastructure objects.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import TypedDict

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from agent.llm import get_llm
from agent.prompt import RAG_PROMPT
from config import settings
from search.retriever import PgVectorRetriever

FALLBACK_ANSWER = (
    "I'm sorry, I couldn't find relevant information in the knowledge base "
    "to answer your question. You may need to submit a support ticket for "
    "further assistance."
)


# ---------------------------------------------------------------------------
# Runtime context schema  (injected per-invocation, never stored/serialized)
# ---------------------------------------------------------------------------

@dataclass
class RAGContext:
    """
    Typed runtime context for the RAG graph.

    Holds infrastructure dependencies that are scoped to a single
    graph invocation. LangGraph injects this via Runtime[RAGContext]
    into any node that declares it as a parameter.

    Attributes:
        db: Active SQLAlchemy Session, supplied by the FastAPI
            Depends(get_db) dependency and forwarded by run_rag().
    """
    db: object  # sqlalchemy.orm.Session — typed as object to avoid
                # importing Session into the graph layer


# ---------------------------------------------------------------------------
# Graph state schema  (dynamic, mutable, returned at END)
# ---------------------------------------------------------------------------

class RAGState(TypedDict):
    question: str             # set by caller in run_rag()
    docs:     list[Document]  # written by retrieve_node
    answer:   str             # written by generate_node
    sources:  list[str]       # written by generate_node


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def retrieve_node(state: RAGState, runtime: Runtime[RAGContext]) -> dict:
    """
    Node 1 — retrieve KB chunks and write them to state["docs"].

    The SQLAlchemy Session is accessed exclusively via
    runtime.context.db — it is never part of the graph state.
    """
    retriever = PgVectorRetriever(
        db=runtime.context.db,
        top_k=5,
        threshold=settings.rag_similarity_threshold,
    )
    docs = retriever.invoke(state["question"])
    return {"docs": docs}


def generate_node(state: RAGState) -> dict:
    """
    Node 2 — generate the answer from docs.

    Does not require runtime context because generation depends only
    on state data produced by retrieve_node.
    """
    docs = state["docs"]

    if not docs:
        return {"answer": FALLBACK_ANSWER, "sources": []}

    context = "\n\n".join(
        f"[Source: {d.metadata['article_slug']}]\n{d.page_content}"
        for d in docs
    )
    prompt   = RAG_PROMPT.invoke({"input": state["question"], "context": context})
    response = get_llm().invoke(prompt)

    seen: set[str] = set()
    sources = [
        d.metadata["article_slug"]
        for d in docs
        if not (d.metadata["article_slug"] in seen
                or seen.add(d.metadata["article_slug"]))  # type: ignore[func-returns-value]
    ]
    return {"answer": response.content, "sources": sources}


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_rag_graph():
    """
    Build, compile, and cache the RAG StateGraph.

    context_schema=RAGContext registers the typed runtime context so
    LangGraph knows to inject Runtime[RAGContext] into nodes that
    declare it as a parameter.
    """
    builder = StateGraph(RAGState, context_schema=RAGContext)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    return builder.compile()
