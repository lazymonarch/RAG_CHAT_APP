from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.user import UserCreate, UserResponse, UserUpdate, AdminUserCreate, AdminCreateResponse, UserProfileResponse
from app.db.mongodb_models import User, UserRole
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings
from app.dependencies import get_current_user, require_admin, get_current_user_response
from app.users.profile_service import profile_service
from datetime import timedelta, datetime

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user (public endpoint for registration)."""
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user (always as USER role)
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        role=UserRole.USER  # Always create as regular user
    )
    
    await user.insert()
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.get("/", response_model=List[UserResponse])
async def list_users(current_user: User = Depends(require_admin)):
    """List all users (admin only)."""
    users = await User.find_all().to_list()
    return [
        UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user's information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: User = Depends(require_admin)):
    """Get user by ID (admin only)."""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, current_user: User = Depends(require_admin)):
    """Update user (admin only)."""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.hashed_password = get_password_hash(user_data.password)
    if user_data.role:
        user.role = user_data.role
    
    await user.save()
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(require_admin)):
    """Delete user (admin only)."""
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await user.delete()
    return {"message": "User deleted successfully"}


@router.get("/admin/count")
async def get_admin_count():
    """Get count of admin users (public endpoint)."""
    admin_count = await User.find(User.role == UserRole.ADMIN).count()
    return {"admin_count": admin_count}


@router.post("/admin/create", response_model=AdminCreateResponse)
async def create_admin(admin_data: AdminUserCreate):
    """Create admin user (max 2 admins allowed)."""
    # Check admin count
    admin_count = await User.find(User.role == UserRole.ADMIN).count()
    if admin_count >= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of admin users reached (2). Only 2 admin users are allowed."
        )
    
    # Check if user already exists
    existing_user = await User.find_one(User.email == admin_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create admin user (force admin role regardless of input)
    hashed_password = get_password_hash(admin_data.password)
    user = User(
        email=admin_data.email,
        hashed_password=hashed_password,
        role=UserRole.ADMIN  # Always create as admin
    )
    
    await user.insert()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return AdminCreateResponse(
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        ),
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me/profile", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put("/me/profile", response_model=UserResponse)
async def update_my_profile(user_data: UserUpdate, current_user: User = Depends(get_current_user)):
    """Update current user's profile."""
    # Update fields if provided
    if user_data.email:
        current_user.email = user_data.email
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)
    
    await current_user.save()
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's comprehensive profile with statistics."""
    try:
        return await profile_service.get_user_profile(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(user_data: UserUpdate, current_user: User = Depends(get_current_user)):
    """Update current user's profile."""
    try:
        # Update fields if provided
        if user_data.email:
            current_user.email = user_data.email
        if user_data.password:
            current_user.hashed_password = get_password_hash(user_data.password)
        if user_data.name:
            current_user.name = user_data.name
        
        current_user.updated_at = datetime.utcnow()
        await current_user.save()
        
        return await profile_service.get_user_profile(str(current_user.id))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/me/profile")
async def delete_my_profile(current_user: User = Depends(get_current_user)):
    """Delete current user's profile."""
    await current_user.delete()
    return {"message": "Profile deleted successfully"}
