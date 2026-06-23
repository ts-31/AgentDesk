from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal


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
