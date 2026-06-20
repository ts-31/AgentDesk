"""
subscriptions.py — LangChain tool for retrieving a customer's subscriptions.

Validates that the customer exists, then returns all associated
subscriptions as a list of plain dicts.
"""

from typing import Annotated
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from models import Customer, Subscription


@tool
def get_customer_subscriptions(
    customer_id: str,
    config: RunnableConfig,
) -> dict | str:
    """Retrieve all subscriptions for a given customer. Returns plan tier, billing cycle, status, and renewal info."""
    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid UUID format: '{customer_id}'."

    db = config["configurable"]["__pregel_runtime"].context.db
    customer = db.query(Customer).filter(Customer.customer_id == cid).first()

    if not customer:
        return f"Customer with ID {customer_id} not found."

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
