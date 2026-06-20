"""
invoices.py — LangChain tool for retrieving a customer's invoices.

Validates that the customer exists, then returns all associated
invoices as a list of plain dicts.
"""

from typing import Annotated
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from models import Customer, Invoice


@tool
def get_customer_invoices(
    customer_id: str,
    config: RunnableConfig,
) -> dict | str:
    """Retrieve all invoices for a given customer. Returns a list of invoice records including amount, status, and due date."""
    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid UUID format: '{customer_id}'."

    db = config["configurable"]["__pregel_runtime"].context.db
    customer = db.query(Customer).filter(Customer.customer_id == cid).first()

    if not customer:
        return f"Customer with ID {customer_id} not found."

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
