"""
customer.py — LangChain tool for looking up a customer by UUID.

Uses the SQLAlchemy session from Runtime[RAGContext] (injected via
InjectedToolArg) to query the Customer model directly.  Returns a
plain dict — never a SQLAlchemy instance or HTTP exception.
"""

from typing import Annotated
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from models import Customer


@tool
def get_customer(
    customer_id: str,
    config: RunnableConfig,
) -> dict | str:
    """Look up a customer by their UUID. Returns company name, plan type, and creation date."""
    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid UUID format: '{customer_id}'."

    db = config["configurable"]["__pregel_runtime"].context.db
    customer = db.query(Customer).filter(Customer.customer_id == cid).first()

    if not customer:
        return f"Customer with ID {customer_id} not found."

    return {
        "customer_id": str(customer.customer_id),
        "company_name": customer.company_name,
        "plan_type": customer.plan_type,
        "created_at": customer.created_at.isoformat(),
    }
