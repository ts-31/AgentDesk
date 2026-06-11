import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False)
    plan_tier = Column(String, nullable=False)
    billing_cycle = Column(String, nullable=False) # Monthly, Annual
    status = Column(String, nullable=False, default="Active")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="subscriptions")
