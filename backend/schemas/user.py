from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserBase(BaseModel):
    customer_id: UUID
    email: str
    role: str
    sso_enabled: bool


class UserResponse(UserBase):
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)
