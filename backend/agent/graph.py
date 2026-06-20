"""
graph.py — LangGraph RAG workflow for TeamFlow.

Defines a two-node StateGraph that reproduces the behaviour of the
original run_rag() using the official LangGraph Runtime[Context] API
for per-request dependency injection.

Graph topology:
  START ──▶ retrieve ──▶ generate ──▶ END

Checkpointer (PostgresSaver):
  The graph is compiled with the process-scoped PostgresSaver from
  agent/memory.py.  When chain.py passes a non-empty configurable
  {"thread_id": ...}, LangGraph reads the stored checkpoint from
  PostgreSQL, replays it, and persists the updated state after each
  invocation.  Conversation history survives application restarts.
  When thread_id is absent (config={}), the checkpointer is bypassed
  entirely and the graph behaves identically to the stateless version.

Runtime context vs. graph state
────────────────────────────────
RAGContext holds the SQLAlchemy Session because:
  - Sessions are not JSON-serializable — they cannot live in State.
  - Runtime context is never checkpointed or replayed by LangGraph.
  - This cleanly separates infrastructure concerns from graph data.
  - RunnableConfig.configurable is designed for configuration parameters
    (model name, temperature, flags), not stateful infrastructure objects.

Conversation history vs. RAG state
────────────────────────────────────
RAGState.messages accumulates [HumanMessage, AIMessage] pairs across
turns via the add_messages reducer.  Keys question/docs/answer/sources
are overwritten fresh on every invoke — they are never accumulated.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Annotated, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.runtime import Runtime

from agent.llm import get_llm
from agent.prompt import RAG_PROMPT
from config import settings
from search.retriever import PgVectorRetriever

logger = logging.getLogger(__name__)

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
    # add_messages reducer: appends incoming messages instead of replacing.
    # Replayed by the checkpointer across turns when thread_id is provided.
    messages: Annotated[list[BaseMessage], add_messages]


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
    Node 2 — generate the answer from docs, optionally using chat history.

    When thread_id is provided (checkpointer active), state["messages"]
    contains prior [HumanMessage, AIMessage] pairs from earlier turns.
    These are prepended to the RAG prompt so the LLM has conversation
    context.  On the stateless path (no thread_id), messages is empty
    and the behaviour is identical to the original implementation.

    After generation, this turn's HumanMessage + AIMessage are appended
    to messages via the add_messages reducer so the checkpointer persists
    them for future turns.
    """
    docs = state["docs"]

    if not docs:
        # Even on fallback, record the turn so history is coherent.
        return {
            "answer": FALLBACK_ANSWER,
            "sources": [],
            "messages": [
                HumanMessage(content=state["question"]),
                AIMessage(content=FALLBACK_ANSWER),
            ],
        }

    context = "\n\n".join(
        f"[Source: {d.metadata['article_slug']}]\n{d.page_content}"
        for d in docs
    )

    # Build prompt: prior conversation history + RAG prompt messages
    history: list[BaseMessage] = list(state.get("messages", []))
    rag_messages = RAG_PROMPT.format_messages(
        input=state["question"], context=context
    )
    prompt_messages = history + rag_messages

    response = get_llm().invoke(prompt_messages)

    seen: set[str] = set()
    sources = [
        d.metadata["article_slug"]
        for d in docs
        if not (d.metadata["article_slug"] in seen
                or seen.add(d.metadata["article_slug"]))  # type: ignore[func-returns-value]
    ]

    return {
        "answer": response.content,
        "sources": sources,
        "messages": [
            HumanMessage(content=state["question"]),
            AIMessage(content=response.content),
        ],
    }


# ---------------------------------------------------------------------------
# Graph factory  (module-level singleton, not @lru_cache)
# ---------------------------------------------------------------------------

# @lru_cache cannot be used here: LangGraph requires the same compiled graph
# object that holds the MemorySaver reference to be reused across calls.
# A module-level sentinel achieves the identical singleton guarantee.
_graph_with_memory = None
_graph_stateless = None


def _build_graph() -> StateGraph:
    builder = StateGraph(RAGState, context_schema=RAGContext)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    return builder


def get_rag_graph(with_memory: bool = True):
    """
    Build, compile, and cache the RAG StateGraph.

    When with_memory=True, it compiles with the MemorySaver checkpointer.
    When with_memory=False, it compiles without a checkpointer to allow stateless execution.
    """
    global _graph_with_memory, _graph_stateless
    if with_memory:
        if _graph_with_memory is None:
            from agent.memory import get_checkpointer  # local import avoids circularity
            _graph_with_memory = _build_graph().compile(checkpointer=get_checkpointer())
            logger.info("RAG graph compiled with MemorySaver checkpointer.")
        return _graph_with_memory
    else:
        if _graph_stateless is None:
            _graph_stateless = _build_graph().compile()
            logger.info("RAG graph compiled without checkpointer (stateless).")
        return _graph_stateless

