from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class CustomerBase(BaseModel):
    company_name: str
    plan_type: str

class CustomerResponse(CustomerBase):
    customer_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    customer_id: UUID
    email: str
    role: str
    sso_enabled: bool

class UserResponse(UserBase):
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)

class SubscriptionBase(BaseModel):
    customer_id: UUID
    plan_tier: str
    billing_cycle: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    auto_renew: bool

class SubscriptionResponse(SubscriptionBase):
    subscription_id: UUID
    model_config = ConfigDict(from_attributes=True)

class InvoiceBase(BaseModel):
    customer_id: UUID
    amount: Decimal
    status: str
    created_at: datetime
    due_date: datetime
    paid_at: Optional[datetime] = None
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None

class InvoiceResponse(InvoiceBase):
    invoice_id: UUID
    model_config = ConfigDict(from_attributes=True)

class TicketBase(BaseModel):
    customer_id: UUID
    user_id: UUID
    category: str
    status: str
    priority: str
    created_at: datetime

class TicketResponse(TicketBase):
    ticket_id: UUID
    model_config = ConfigDict(from_attributes=True)
