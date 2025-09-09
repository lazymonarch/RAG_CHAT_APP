from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.db.mongodb_models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    # role defaults to USER and is not shown in API docs
    role: UserRole = Field(default=UserRole.USER, description="User role (defaults to 'user')")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: str
    role: UserRole
    created_at: datetime
    updated_at: datetime


class AdminUserCreate(UserBase):
    password: str
    # role defaults to ADMIN for admin creation
    role: UserRole = Field(default=UserRole.ADMIN, description="Admin role (defaults to 'admin')")


class AdminCreateResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
