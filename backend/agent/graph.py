"""
graph.py — LangGraph hybrid workflow for TeamFlow.

Defines a StateGraph that routes between a RAG pipeline and CRM Tools.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Annotated, TypedDict, Literal

from pydantic import BaseModel, Field

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.runtime import Runtime

from agent.llm import get_llm
from agent.prompt import RAG_PROMPT, REWRITE_PROMPT, CLASSIFY_PROMPT, TOOL_SYSTEM_PROMPT
from agent.tools import ALL_TOOLS
from config import settings
from search.retriever import PgVectorRetriever

logger = logging.getLogger(__name__)

FALLBACK_ANSWER = (
    "I'm sorry, I couldn't find relevant information in the knowledge base "
    "to answer your question. You may need to submit a support ticket for "
    "further assistance."
)

@dataclass
class AgentContext:
    db: object  # sqlalchemy.orm.Session

class AgentState(TypedDict):
    question: str
    intent: str
    search_query: str
    docs: list[Document]
    answer: str
    sources: list[str]
    messages: Annotated[list[BaseMessage], add_messages]

class IntentOutput(BaseModel):
    intent: Literal["rag", "tools"] = Field(description="The routed intent")

# ---------------------------------------------------------------------------
# Routing & Classification
# ---------------------------------------------------------------------------

def classify_node(state: AgentState) -> dict:
    """Determine if the question requires RAG or tools."""
    prompt = CLASSIFY_PROMPT.format_messages(question=state["question"])
    llm_with_structured_output = get_llm().with_structured_output(IntentOutput)
    response = llm_with_structured_output.invoke(prompt)
    return {"intent": response.intent}

def route_intent(state: AgentState) -> str:
    return state["intent"]

# ---------------------------------------------------------------------------
# RAG Branch Nodes
# ---------------------------------------------------------------------------

def rewrite_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    if not messages:
        return {"search_query": state["question"]}

    history_str = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in messages
    )
    
    prompt = REWRITE_PROMPT.format_messages(
        history=history_str,
        question=state["question"]
    )
    response = get_llm().invoke(prompt)
    return {"search_query": response.content}

def retrieve_node(state: AgentState, runtime: Runtime[AgentContext]) -> dict:
    retriever = PgVectorRetriever(
        db=runtime.context.db,
        top_k=5,
        threshold=settings.rag_similarity_threshold,
    )
    docs = retriever.invoke(state.get("search_query", state["question"]))
    return {"docs": docs}

def generate_node(state: AgentState) -> dict:
    docs = state.get("docs", [])

    if not docs:
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
                or seen.add(d.metadata["article_slug"]))
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
# Tools Branch Nodes
# ---------------------------------------------------------------------------

def tool_agent_node(state: AgentState) -> dict:
    llm = get_llm().bind_tools(ALL_TOOLS)
    history: list[BaseMessage] = list(state.get("messages", []))
    
    messages = [
        {"role": "system", "content": TOOL_SYSTEM_PROMPT}
    ] + history + [HumanMessage(content=state["question"])]
    
    response = llm.invoke(messages)
    
    return {"messages": [HumanMessage(content=state["question"]), response]}

def tool_synthesize_node(state: AgentState) -> dict:
    """Final node after tools are executed to synthesize the response."""
    history: list[BaseMessage] = list(state.get("messages", []))
    
    llm = get_llm()
    messages = [{"role": "system", "content": TOOL_SYSTEM_PROMPT}] + history
    
    response = llm.invoke(messages)
    
    return {
        "answer": response.content,
        "sources": [],
        "messages": [response]
    }

# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

_graph_with_memory = None
_graph_stateless = None

def _build_graph() -> StateGraph:
    builder = StateGraph(AgentState, context_schema=AgentContext)
    
    # Nodes
    builder.add_node("classify", classify_node)
    
    # RAG branch
    builder.add_node("rewrite", rewrite_node)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    
    # Tools branch
    builder.add_node("tool_agent", tool_agent_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))
    builder.add_node("tool_synthesize", tool_synthesize_node)
    
    # Edges
    builder.add_edge(START, "classify")
    
    builder.add_conditional_edges(
        "classify",
        route_intent,
        {"rag": "rewrite", "tools": "tool_agent"}
    )
    
    # RAG path
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    
    # Tools path
    builder.add_conditional_edges(
        "tool_agent",
        tools_condition,
        {"tools": "tools", "__end__": "tool_synthesize"}
    )
    builder.add_edge("tools", "tool_synthesize")
    builder.add_edge("tool_synthesize", END)
    
    return builder

def get_rag_graph(with_memory: bool = True):
    global _graph_with_memory, _graph_stateless
    if with_memory:
        if _graph_with_memory is None:
            from agent.memory import get_checkpointer
            _graph_with_memory = _build_graph().compile(checkpointer=get_checkpointer())
            logger.info("Agent graph compiled with MemorySaver checkpointer.")
        return _graph_with_memory
    else:
        if _graph_stateless is None:
            _graph_stateless = _build_graph().compile()
            logger.info("Agent graph compiled without checkpointer (stateless).")
        return _graph_stateless
