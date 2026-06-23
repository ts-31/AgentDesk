"""
tickets.py — LangChain tools for reading and creating support tickets.

Post-auth changes:
  - get_customer_tickets: customer_id sourced from AgentContext — no parameter.
  - create_ticket: customer_id and user_id both sourced from AgentContext.
    The LLM only needs to supply `category` and `priority` (ticket content),
    never identity data.
"""

from typing import Annotated
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg


@tool
def get_customer_tickets(config: Annotated[RunnableConfig, InjectedToolArg]) -> dict | str:
    """Retrieve all support tickets for the authenticated customer. Returns ticket details including category, status, and priority."""
    ctx = config["configurable"]["__pregel_runtime"].context
    db = ctx.db
    customer_id = ctx.customer_id

    if not customer_id:
        return "No authenticated customer context available."

    from uuid import UUID
    from models import Customer, Ticket

    try:
        cid = UUID(customer_id)
    except ValueError:
        return f"Invalid customer_id in auth context: '{customer_id}'."

    customer = db.query(Customer).filter(Customer.customer_id == cid).first()
    if not customer:
        return "Customer record not found."

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
    category: str,
    priority: str,
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> dict | str:
    """Create a new support ticket for the authenticated user. Provide the category and priority only — customer and user identity are resolved automatically. Priority must be one of: Low, Medium, High, Urgent."""
    ctx = config["configurable"]["__pregel_runtime"].context
    customer_id = ctx.customer_id
    user_id = ctx.user_id

    if not customer_id or not user_id:
        return "No authenticated user context available."

    from uuid import UUID
    from sqlalchemy.exc import SQLAlchemyError
    from database import SessionLocal
    from models import Customer, User, Ticket

    try:
        cid = UUID(customer_id)
        uid = UUID(user_id)
    except ValueError as exc:
        return f"Invalid identity in auth context: {exc}"

    # Use a fresh, independent session for the write so that any commit or
    # rollback here cannot corrupt the shared read-only request session used
    # by the other CRM tools.
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.customer_id == cid).first()
        if not customer:
            return "Customer record not found."

        user = db.query(User).filter(User.user_id == uid).first()
        if not user:
            return "User record not found."

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
    except SQLAlchemyError as exc:
        db.rollback()
        return f"Failed to create ticket due to a database error: {exc}"
    finally:
        db.close()

