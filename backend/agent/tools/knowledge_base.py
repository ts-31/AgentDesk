"""
knowledge_base.py — LangChain tool for searching the TeamFlow knowledge base.

Wraps the existing rewrite → PgVectorRetriever pipeline behind a single
@tool interface so the ReAct agent can call it on-demand, optionally
alongside CRM tools, without any upfront intent classification.

Rewriting is always applied (unconditionally) so that multi-turn follow-up
questions ("tell me more", "what about the API limits?") are resolved to
standalone queries before hitting pgvector.  For first-turn or already-
standalone queries the LLM reproduces the query verbatim — the rewrite step
is idempotent in that case.

The tool returns a plain str so its result fits naturally in a ToolMessage
content field and is directly readable by the LLM in the next ReAct step.
Sources are embedded as "[Source: slug]" headers so chain.py can parse them
without any additional state fields.
"""

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from agent.llm import get_llm
from agent.prompt import REWRITE_PROMPT
from config import settings
from search.retriever import PgVectorRetriever


@tool
def retrieve_kb(query: str, config: RunnableConfig) -> str:
    """Search the TeamFlow knowledge base for documentation, how-tos, feature
    explanations, API rate limits, subscription plans, billing policies, and
    support articles. Use this whenever the user asks about how the platform
    works, what a feature does, or what the policies are."""
    runtime = config["configurable"]["__pregel_runtime"]
    db = runtime.context.db

    # --- Query rewriting (always applied) -----------------------------------
    # Pull the current message history from the LangGraph runtime so that
    # follow-up questions are resolved to standalone search queries.
    # config["configurable"]["checkpoint_ns"] exists when memory is active;
    # we read messages from the state snapshot attached to the runtime.
    messages: list = []
    try:
        # LangGraph injects the current state snapshot into the runtime; the
        # "messages" key mirrors AgentState.messages at call time.
        messages = list(runtime.config.get("messages", []))
    except Exception:
        pass

    history_str = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in messages
        if hasattr(m, "content") and isinstance(m.content, str)
    )

    rewrite_prompt_msgs = REWRITE_PROMPT.format_messages(
        history=history_str or "(no prior conversation)",
        question=query,
    )
    rewrite_response = get_llm().invoke(rewrite_prompt_msgs)
    search_query = rewrite_response.content.strip() or query

    # --- Vector retrieval ---------------------------------------------------
    retriever = PgVectorRetriever(
        db=db,
        top_k=5,
        threshold=settings.rag_similarity_threshold,
    )
    docs = retriever.invoke(search_query)

    if not docs:
        return (
            "No relevant knowledge base articles were found for this query. "
            "The similarity threshold was not met by any article."
        )

    # Embed source slugs as parseable headers so chain.py can extract them.
    return "\n\n".join(
        f"[Source: {d.metadata['article_slug']}]\n{d.page_content}"
        for d in docs
    )
