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
    last_login: Optional[datetime] = None
    storage_used: int = 0
    storage_limit: int = 100 * 1024 * 1024
    is_active: bool = True


class UserProfileResponse(BaseModel):
    """Comprehensive user profile with statistics."""
    id: str
    name: Optional[str] = None
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None
    document_count: int = 0
    chat_count: int = 0
    message_count: int = 0
    storage_used: int = 0
    storage_limit: int = 100 * 1024 * 1024
    storage_percentage: float = 0.0


class AdminUserCreate(UserBase):
    password: str
    # role defaults to ADMIN for admin creation
    role: UserRole = Field(default=UserRole.ADMIN, description="Admin role (defaults to 'admin')")


class AdminCreateResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
