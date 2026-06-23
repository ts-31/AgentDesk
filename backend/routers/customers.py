from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import Customer, User, Subscription, Invoice, Ticket
from schemas import (
    CustomerBase,
    CustomerResponse,
    UserResponse,
    SubscriptionResponse,
    InvoiceResponse,
    TicketResponse,
)
from auth.dependencies import get_current_user

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(get_current_user)]
)


def _get_customer_or_404(customer_id: UUID, db: Session) -> Customer:
    """Shared lookup — raises 404 if the customer doesn't exist."""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("", response_model=List[CustomerResponse])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    return _get_customer_or_404(customer_id, db)


@router.get("/{customer_id}/users", response_model=List[UserResponse])
def get_customer_users(customer_id: UUID, db: Session = Depends(get_db)):
    """List all users belonging to a customer."""
    _get_customer_or_404(customer_id, db)
    return db.query(User).filter(User.customer_id == customer_id).all()


@router.get("/{customer_id}/subscription", response_model=List[SubscriptionResponse])
def get_customer_subscription(customer_id: UUID, db: Session = Depends(get_db)):
    """Get the subscription(s) for a customer."""
    _get_customer_or_404(customer_id, db)
    return db.query(Subscription).filter(Subscription.customer_id == customer_id).all()


@router.get("/{customer_id}/invoices", response_model=List[InvoiceResponse])
def get_customer_invoices(customer_id: UUID, db: Session = Depends(get_db)):
    """List all invoices for a customer."""
    _get_customer_or_404(customer_id, db)
    return db.query(Invoice).filter(Invoice.customer_id == customer_id).all()


@router.get("/{customer_id}/tickets", response_model=List[TicketResponse])
def get_customer_tickets(customer_id: UUID, db: Session = Depends(get_db)):
    """List all support tickets for a customer."""
    _get_customer_or_404(customer_id, db)
    return db.query(Ticket).filter(Ticket.customer_id == customer_id).all()
