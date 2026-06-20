"""
agent/tools — LangChain tools for customer data operations.

All tools are designed to be mounted into a LangGraph ToolNode and receive
the SQLAlchemy session via Runtime[RAGContext] + InjectedToolArg.

Usage:
    from agent.tools import ALL_TOOLS
    from langgraph.prebuilt import ToolNode

    builder.add_node("tools", ToolNode(ALL_TOOLS))
"""

from .customer import get_customer
from .invoices import get_customer_invoices
from .subscriptions import get_customer_subscriptions
from .tickets import get_customer_tickets, create_ticket

ALL_TOOLS = [
    get_customer,
    get_customer_invoices,
    get_customer_subscriptions,
    get_customer_tickets,
    create_ticket,
]
