"""
customer.py — LangChain tool for looking up the authenticated customer.

Post-auth: customer_id is sourced directly from AgentContext (JWT payload).
The tool no longer accepts customer_id as a parameter, so the LLM will
never need to ask the user for it.
"""

from typing import Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg


@tool
def get_customer(config: Annotated[RunnableConfig, InjectedToolArg]) -> dict | str:
    """Look up the authenticated customer's account. Returns company name, plan type, and creation date."""
    ctx = config["configurable"]["__pregel_runtime"].context
    db = ctx.db
    customer_id = ctx.customer_id

    if not customer_id:
        return "No authenticated customer context available."

    from uuid import UUID
    from models import Customer

    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid customer_id in auth context: '{customer_id}'."

    customer = db.query(Customer).filter(Customer.customer_id == cid).first()

    if not customer:
        return "Customer record not found."

    return {
        "customer_id": str(customer.customer_id),
        "company_name": customer.company_name,
        "plan_type": customer.plan_type,
        "created_at": customer.created_at.isoformat(),
    }
