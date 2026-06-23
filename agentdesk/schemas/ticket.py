from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class TicketBase(BaseModel):
    customer_id: UUID
    user_id: UUID
    category: str
    status: str
    priority: str
    created_at: datetime


class TicketCreate(BaseModel):
    customer_id: UUID
    user_id: UUID
    category: str
    status: Optional[str] = "Open"
    priority: Optional[str] = "Medium"


class TicketResponse(TicketBase):
    ticket_id: UUID
    model_config = ConfigDict(from_attributes=True)

