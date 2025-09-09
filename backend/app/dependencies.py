from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import verify_token
from app.db.mongodb_models import User
from app.schemas.user import UserResponse
from typing import Optional

# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_response(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user as UserResponse schema."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for access."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_user_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require user or admin role for access."""
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User or admin access required"
        )
    return current_user
