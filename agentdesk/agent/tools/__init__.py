"""
agent/tools — LangChain tools for customer data operations and KB retrieval.

All tools are designed to be mounted into a LangGraph ToolNode and receive
the SQLAlchemy session via Runtime[AgentContext] + InjectedToolArg.

CRM tools (get_customer, get_customer_invoices, get_customer_subscriptions,
get_customer_tickets, create_ticket) handle live customer data.

retrieve_kb wraps the existing rewrite → PgVectorRetriever pipeline so the
ReAct agent can search documentation without a separate RAG branch.

Usage:
    from agent.tools import ALL_TOOLS
    from langgraph.prebuilt import ToolNode

    builder.add_node("tools", ToolNode(ALL_TOOLS))
"""

from .customer import get_customer
from .invoices import get_customer_invoices
from .knowledge_base import retrieve_kb
from .subscriptions import get_customer_subscriptions
from .tickets import get_customer_tickets, create_ticket

ALL_TOOLS = [
    # CRM tools — listed first so they appear first in the LLM tool schema
    get_customer,
    get_customer_invoices,
    get_customer_subscriptions,
    get_customer_tickets,
    create_ticket,
    # Knowledge base tool — wraps rewrite + pgvector retrieval
    retrieve_kb,
]
