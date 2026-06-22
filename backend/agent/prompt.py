"""
prompt.py — LangChain prompt templates for the TeamFlow agent.

Templates:
  RAG_PROMPT      — Used inside retrieve_kb to format KB excerpts for the LLM.
                    {context} receives the [Source: slug]\\nchunk_text blocks.
                    {input} receives the user's question.

  REWRITE_PROMPT  — Used inside retrieve_kb to rewrite a conversational
                    question into a standalone search query.
                    {history} receives the formatted conversation history.
                    {question} receives the latest user question.

  REACT_SYSTEM_PROMPT — System prompt for the top-level ReAct agent node.
                    Gives the LLM its tool menu and reasoning rules, replacing
                    the removed CLASSIFY_PROMPT and TOOL_SYSTEM_PROMPT.
"""

from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "You are a helpful TeamFlow support assistant.\n"
    "Answer the user's question using ONLY the knowledge base excerpts provided below.\n"
    "Be concise and accurate. If the excerpts do not contain enough information, say so honestly.\n"
    "Do not make up facts not present in the excerpts."
)

# {context} — formatted document block produced by retrieve_kb
# {input}   — raw user question
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Knowledge base excerpts:\n\n{context}\n\nQuestion: {input}"),
])

# {history} — formatted prior conversation (or "(no prior conversation)")
# {question} — latest user question to rewrite into a standalone query
REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "Given the following conversation history and the latest user question, "
        "rephrase the question to be a standalone search query that can be understood "
        "without context.\n\n"
        "Conversation History:\n{history}\n\n"
        "If the latest question is already standalone, return it as is. "
        "Do NOT answer the question. ONLY return the rewritten query."
    )),
    ("human", "{question}"),
])

# System prompt for the ReAct agent node.
# Replaces both CLASSIFY_PROMPT (removed) and TOOL_SYSTEM_PROMPT (removed).
# The agent uses this to reason about which tools to call and in what order.
REACT_SYSTEM_PROMPT = (
    "You are TeamFlow's intelligent support agent. "
    "You have access to the following tools:\n\n"
    "  • retrieve_kb            — Search the knowledge base for documentation, "
    "feature explanations, API rate limits, subscription plans, and policies.\n"
    "  • get_customer           — Look up a customer record by UUID.\n"
    "  • get_customer_invoices  — Retrieve invoices for a customer.\n"
    "  • get_customer_subscriptions — Retrieve subscription details for a customer.\n"
    "  • get_customer_tickets   — Retrieve support tickets for a customer.\n"
    "  • create_ticket          — Create a new support ticket.\n\n"
    "Reasoning rules:\n"
    "1. For questions about platform features, documentation, or policies — "
    "call retrieve_kb.\n"
    "2. For questions about specific customer data (invoices, tickets, subscriptions, "
    "account details) — call the appropriate CRM tool.\n"
    "3. For questions that mix both (e.g. 'What plan is Acme on, and what are the "
    "API rate limits?') — call CRM tools AND retrieve_kb, then synthesize a unified answer.\n"
    "4. For purely conversational questions with no tool need — answer directly.\n"
    "5. Never fabricate data. If a tool returns no results, say so honestly.\n"
    "Be concise, accurate, and helpful."
)

