from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash
)
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, Token

class LoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter()


@router.post("/register", response_model=UserSchema)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Register new user"""
    # Check if user exists
    result = await db.execute(
        select(User).where(
            (User.username == user_in.username) | 
            (User.email == user_in.email)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)
) -> Any:
    """OAuth2 compatible token login"""
    # Get credentials from form
    login_username = form_data.username
    login_password = form_data.password
    
    # Get user
    result = await db.execute(
        select(User).where(User.username == login_username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires,
        is_superuser=user.is_superuser,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }