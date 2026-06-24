"""
graph.py — LangGraph ReAct agent for AgentDesk.

Replaces the former intent-routing architecture (classify → rag | tools)
with a single ReAct (Reason + Act) loop that can reason about whether to:
  - answer directly (no tool calls)
  - call one or more CRM tools
  - call retrieve_kb (rewrite + pgvector retrieval)
  - combine CRM tools and retrieve_kb in any order

Graph structure:
  START → agent ──[tool_calls]──► tools ──► agent (loop)
                └──[no tool_calls]──► END

State:
  AgentState now carries only `question` (original text, for chain.py
  fallback) and `messages` (the full message history, updated by
  add_messages after every node).  `answer`, `intent`, `search_query`,
  `docs`, and `sources` are removed from state; `chain.py` extracts the
  final answer and sources from the message list after graph.invoke() returns
  (Option A agreed design).

Preserved:
  - PgVectorRetriever / pgvector SQL    → unchanged in search/retriever.py
  - PostgreSQL checkpoint memory        → unchanged in agent/memory.py
  - AgentContext runtime context        → unchanged dataclass
  - get_rag_graph() public function     → same signature, same cache pattern
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agent.llm import get_llm
from agent.prompt import REACT_SYSTEM_PROMPT
from agent.tools import ALL_TOOLS

logger = logging.getLogger(__name__)

# Minimal technical fallback — only surfaced when the graph produces zero
# AIMessages (should not happen in normal operation; LLM naturally expresses
# "I couldn't find" responses via the tool outputs).
_TECHNICAL_FALLBACK = (
    "I was unable to generate a response. Please try again or contact support."
)


# ---------------------------------------------------------------------------
# Runtime context — unchanged
# ---------------------------------------------------------------------------

@dataclass
class AgentContext:
    db: object       # sqlalchemy.orm.Session
    # Identity fields sourced from the validated JWT — populated by routers/agent.py.
    # All are strings (not UUIDs) to stay serialization-safe.
    user_id: str = ""       # UUID string of the authenticated user
    customer_id: str = ""   # UUID string of the user's customer/workspace
    user_email: str = ""    # Used for audit trails and ticket attribution
    user_role: str = ""     # Member | Admin | Guest (reserved for future gating)


# ---------------------------------------------------------------------------
# State — simplified for ReAct
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    # Original user question — retained so chain.py has a fallback reference.
    question: str
    # Full message history — the only data conduit for the ReAct loop.
    # add_messages ensures each append is a proper list union (no overwrites).
    messages: Annotated[list[BaseMessage], add_messages]


# ---------------------------------------------------------------------------
# ReAct agent node
# ---------------------------------------------------------------------------

def react_agent_node(state: AgentState) -> dict:
    """
    Core ReAct reasoning step.

    Binds ALL_TOOLS to the LLM and invokes it with the current message
    history prefixed by the system prompt.  The LLM either:
      a) Returns an AIMessage with one or more tool_calls  → LangGraph routes
         to the ToolNode for execution, then loops back here.
      b) Returns a plain AIMessage with no tool_calls → tools_condition routes
         to END.

    The HumanMessage for the first turn is injected here if `messages` is
    empty (i.e. stateless mode or very first message of a thread).
    """
    llm = get_llm().bind_tools(ALL_TOOLS)

    history: list[BaseMessage] = list(state.get("messages", []))

    # On the very first invocation within a thread the question may not yet
    # be in the message list (chain.py passes it via state["question"]).
    # Prepend it so the LLM always sees a HumanMessage.
    if not history or not isinstance(history[-1], HumanMessage):
        history = history + [HumanMessage(content=state["question"])]

    messages_to_send = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT},
        *history,
    ]

    response = llm.invoke(messages_to_send)

    # If we injected the HumanMessage above, include it in the returned
    # messages so the checkpointer persists it in the thread's state.
    new_messages: list[BaseMessage] = []
    if not state.get("messages"):
        new_messages.append(HumanMessage(content=state["question"]))
    new_messages.append(response)

    return {"messages": new_messages}


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------

_graph_with_memory = None
_graph_stateless = None


def _build_graph() -> StateGraph:
    builder = StateGraph(AgentState, context_schema=AgentContext)

    # Nodes
    builder.add_node("agent", react_agent_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    # Edges
    builder.add_edge(START, "agent")

    # tools_condition routes to "tools" when the last AIMessage has tool_calls,
    # otherwise routes to END.  The implicit mapping is:
    #   {"tools": "tools", "__end__": END}
    builder.add_conditional_edges("agent", tools_condition)

    # After tool execution, loop back to the agent for the next reasoning step.
    builder.add_edge("tools", "agent")

    return builder


def get_rag_graph(with_memory: bool = True):
    """
    Return the compiled ReAct graph, with or without the PostgreSQL checkpointer.

    Caches both variants as module-level singletons to avoid recompilation.
    The function signature is identical to the previous version so all call
    sites (chain.py, tests) remain unchanged.
    """
    global _graph_with_memory, _graph_stateless
    if with_memory:
        if _graph_with_memory is None:
            from agent.memory import get_checkpointer
            _graph_with_memory = _build_graph().compile(
                checkpointer=get_checkpointer()
            )
            logger.info("ReAct agent graph compiled with PostgresSaver checkpointer.")
        return _graph_with_memory
    else:
        if _graph_stateless is None:
            _graph_stateless = _build_graph().compile()
            logger.info("ReAct agent graph compiled without checkpointer (stateless).")
        return _graph_stateless
