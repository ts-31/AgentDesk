from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from models import Ticket, Customer, User
from schemas import TicketBase, TicketCreate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", response_model=List[TicketResponse])
def get_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Ticket).offset(skip).limit(limit).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket. Validates that customer and user exist."""
    # Validate customer exists
    customer = db.query(Customer).filter(Customer.customer_id == ticket_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Validate user exists
    user = db.query(User).filter(User.user_id == ticket_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ticket = Ticket(**ticket_data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

