"""
prompt.py — LangChain prompt template for the RAG pipeline.

The system prompt text is identical to the original _SYSTEM_PROMPT in
generator.py. The {context} placeholder is populated by
create_stuff_documents_chain using a per-document template that preserves
the original [Source: slug] header format. {input} receives the raw user
question from the chain invocation.
"""

from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "You are a helpful TeamFlow support assistant.\n"
    "Answer the user's question using ONLY the knowledge base excerpts provided below.\n"
    "Be concise and accurate. If the excerpts do not contain enough information, say so honestly.\n"
    "Do not make up facts not present in the excerpts."
)

# {context} — formatted document block injected by create_stuff_documents_chain
# {input}   — raw user question passed via chain.invoke({"input": question})
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Knowledge base excerpts:\n\n{context}\n\nQuestion: {input}"),
])

REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Given the following conversation history and the latest user question, rephrase the question to be a standalone search query that can be understood without context.\n\nConversation History:\n{history}\n\nIf the latest question is already standalone, return it as is. Do NOT answer the question. ONLY return the rewritten query."),
    ("human", "{question}"),
])

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a routing agent for TeamFlow. Determine if the user's request requires the 'rag' knowledge base (general platform knowledge, how-tos, documentation) or 'tools' (CRM customer operations, viewing tickets, invoices, subscriptions).\n\nIf the user asks about specific customer data, choose 'tools'. If they ask how a feature works or need support documentation, choose 'rag'."),
    ("human", "{question}"),
])

TOOL_SYSTEM_PROMPT = (
    "You are a customer ops agent with access to CRM tools. Use the provided tools to fulfill the user's request.\n"
    "Answer the user based on the tool outputs. Be concise, accurate, and helpful."
)
