"""
invoices.py — LangChain tool for retrieving the authenticated customer's invoices.

Post-auth: customer_id is sourced directly from AgentContext (JWT payload).
The tool no longer accepts customer_id as a parameter.
"""

from typing import Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg


@tool
def get_customer_invoices(config: Annotated[RunnableConfig, InjectedToolArg]) -> dict | str:
    """Retrieve all invoices for the authenticated customer. Returns a list of invoice records including amount, status, and due date."""
    ctx = config["configurable"]["__pregel_runtime"].context
    db = ctx.db
    customer_id = ctx.customer_id

    if not customer_id:
        return "No authenticated customer context available."

    from uuid import UUID
    from models import Customer, Invoice

    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid customer_id in auth context: '{customer_id}'."

    customer = db.query(Customer).filter(Customer.customer_id == cid).first()
    if not customer:
        return "Customer record not found."

    invoices = db.query(Invoice).filter(Invoice.customer_id == cid).all()

    return {
        "customer_id": customer_id,
        "invoices": [
            {
                "invoice_id": str(inv.invoice_id),
                "amount": str(inv.amount),
                "status": inv.status,
                "due_date": inv.due_date.isoformat() if inv.due_date else None,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
                "billing_period_start": inv.billing_period_start.isoformat() if inv.billing_period_start else None,
                "billing_period_end": inv.billing_period_end.isoformat() if inv.billing_period_end else None,
            }
            for inv in invoices
        ],
    }
