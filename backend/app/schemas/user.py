from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1, max_length=100)
    age_group: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    join_date: datetime
    is_premium: bool
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
