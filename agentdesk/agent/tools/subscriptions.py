"""
subscriptions.py — LangChain tool for retrieving the authenticated customer's subscriptions.

Post-auth: customer_id is sourced directly from AgentContext (JWT payload).
The tool no longer accepts customer_id as a parameter.
"""

from typing import Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg


@tool
def get_customer_subscriptions(config: Annotated[RunnableConfig, InjectedToolArg]) -> dict | str:
    """Retrieve all subscriptions for the authenticated customer. Returns plan tier, billing cycle, status, and renewal info."""
    ctx = config["configurable"]["__pregel_runtime"].context
    db = ctx.db
    customer_id = ctx.customer_id

    if not customer_id:
        return "No authenticated customer context available."

    from uuid import UUID
    from models import Customer, Subscription

    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid customer_id in auth context: '{customer_id}'."

    customer = db.query(Customer).filter(Customer.customer_id == cid).first()
    if not customer:
        return "Customer record not found."

    subs = db.query(Subscription).filter(Subscription.customer_id == cid).all()

    return {
        "customer_id": customer_id,
        "subscriptions": [
            {
                "subscription_id": str(sub.subscription_id),
                "plan_tier": sub.plan_tier,
                "billing_cycle": sub.billing_cycle,
                "status": sub.status,
                "start_date": sub.start_date.isoformat() if sub.start_date else None,
                "end_date": sub.end_date.isoformat() if sub.end_date else None,
                "canceled_at": sub.canceled_at.isoformat() if sub.canceled_at else None,
                "auto_renew": sub.auto_renew,
            }
            for sub in subs
        ],
    }
