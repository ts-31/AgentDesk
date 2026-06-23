import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, default="Member")
    sso_enabled = Column(Boolean, default=False)
    # Stores a bcrypt hash of the user's password.
    # nullable=True for safe migration of existing rows; tighten after all rows are seeded.
    password_hash = Column(String, nullable=True)

    customer = relationship("Customer", back_populates="users")
    tickets = relationship("Ticket", back_populates="user")
