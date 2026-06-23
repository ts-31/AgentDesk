from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


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
