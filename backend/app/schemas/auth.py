"""Authentication schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    nickname: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """User registration schema."""

    password: str = Field(..., min_length=8, max_length=72)  # bcrypt 限制最大72字节


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response schema."""

    id: int
    avatar: Optional[str] = None
    provider: str = "email"
    is_active: bool = True
    created_at: datetime
    locked_until: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token data schema."""

    user_id: Optional[int] = None
    email: Optional[str] = None
