"""
tickets.py — LangChain tools for reading and creating support tickets.

Two tools:
  - get_customer_tickets: Retrieves all tickets for a customer.
  - create_ticket: Creates a new ticket after validating customer and user.
"""

from typing import Annotated
from uuid import UUID

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from models import Customer, Ticket, User


@tool
def get_customer_tickets(
    customer_id: str,
    config: RunnableConfig,
) -> dict | str:
    """Retrieve all support tickets for a given customer. Returns ticket details including category, status, and priority."""
    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid UUID format: '{customer_id}'."

    db = config["configurable"]["__pregel_runtime"].context.db
    customer = db.query(Customer).filter(Customer.customer_id == cid).first()

    if not customer:
        return f"Customer with ID {customer_id} not found."

    tickets = db.query(Ticket).filter(Ticket.customer_id == cid).all()

    return {
        "customer_id": customer_id,
        "tickets": [
            {
                "ticket_id": str(t.ticket_id),
                "user_id": str(t.user_id),
                "category": t.category,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tickets
        ],
    }


@tool
def create_ticket(
    customer_id: str,
    user_id: str,
    category: str,
    priority: str,
    config: RunnableConfig,
) -> dict | str:
    """Create a new support ticket for a customer. Validates that both the customer and user exist. Priority should be one of: Low, Medium, High, Urgent."""
    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid UUID format for customer_id: '{customer_id}'."

    try:
        uid = UUID(user_id)
    except ValueError:
        return f"Invalid UUID format for user_id: '{user_id}'."

    db = config["configurable"]["__pregel_runtime"].context.db

    customer = db.query(Customer).filter(Customer.customer_id == cid).first()
    if not customer:
        return f"Customer with ID {customer_id} not found."

    user = db.query(User).filter(User.user_id == uid).first()
    if not user:
        return f"User with ID {user_id} not found."

    ticket = Ticket(
        customer_id=cid,
        user_id=uid,
        category=category,
        status="Open",
        priority=priority,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "ticket_id": str(ticket.ticket_id),
        "customer_id": str(ticket.customer_id),
        "user_id": str(ticket.user_id),
        "category": ticket.category,
        "status": ticket.status,
        "priority": ticket.priority,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }
