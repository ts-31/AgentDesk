import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Open")
    priority = Column(String, nullable=False, default="Medium")
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="tickets")
    user = relationship("User", back_populates="tickets")
