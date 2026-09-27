"""Pydantic schemas for Authentication and Users."""

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field("ANALYST", pattern="^(ADMIN|ANALYST|VIEWER)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
