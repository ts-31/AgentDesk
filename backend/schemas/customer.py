from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class CustomerBase(BaseModel):
    company_name: str
    plan_type: str


class CustomerResponse(CustomerBase):
    customer_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
