from typing import Optional, Union
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(
        select(User).where(User.username == token_data.username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    
    result = await db.execute(
        select(User).where(User.username == token_data.username)
    )
    user = result.scalar_one_or_none()
    
    if user and user.is_active:
        return user
    return None


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user (alias for superuser)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


class GuestSession:
    """Guest session for temporary access with usage tracking"""
    def __init__(self, guest_id: str, usage_count: int = 0, first_activity: datetime = None):
        self.guest_id = guest_id
        self.is_guest = True
        self.daily_limit = 10  # Daily evaluation limit for guests
        self.usage_count = usage_count
        self.remaining_uses = max(0, self.daily_limit - usage_count)
        self.created_at = first_activity or datetime.now(timezone.utc)
        self.session_duration = int((datetime.now(timezone.utc) - self.created_at).total_seconds() / 60)  # minutes
        self.evaluations_created = usage_count
        self.trigger_scenarios = self._check_trigger_scenarios()
        
    def __str__(self):
        return f"Guest({self.guest_id[:8]}...)"
    
    def _check_trigger_scenarios(self):
        """Check which login trigger scenarios are active"""
        scenarios = []
        
        # Scenario 1: Daily limit reached
        if self.remaining_uses <= 0:
            scenarios.append({
                "type": "limit_reached",
                "urgency": "high",
                "message": "您已达到今日免费评测次数上限"
            })
        
        # Scenario 2: Multiple evaluations without saving
        elif self.evaluations_created >= 2:
            scenarios.append({
                "type": "save_progress",
                "urgency": "medium",
                "message": "登录以保存您的评测历史"
            })
        
        # Scenario 3: Extended session time
        if self.session_duration >= 10:
            scenarios.append({
                "type": "extended_use",
                "urgency": "low",
                "message": "您已使用超过10分钟，注册账号享受更多功能"
            })
        
        return scenarios
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "guest_id": self.guest_id,
            "is_guest": True,
            "daily_limit": self.daily_limit,
            "usage_count": self.usage_count,
            "remaining_uses": self.remaining_uses,
            "created_at": self.created_at.isoformat(),
            "session_duration": self.session_duration,
            "trigger_scenarios": self.trigger_scenarios,
            "suggestions": {
                "show_login_prompt": len(self.trigger_scenarios) > 0,
                "primary_scenario": self.trigger_scenarios[0] if self.trigger_scenarios else None
            }
        }


async def get_current_user_or_guest(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Union[User, GuestSession]:
    """Get current authenticated user or create guest session"""
    
    # Debug logging
    print(f"[DEBUG] get_current_user_or_guest called!")
    print(f"[DEBUG] Request headers: {dict(request.headers)}")
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Request URL: {request.url}")
    
    # Try to get token from Authorization header
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix
        print(f"[DEBUG] Found Bearer token: {token[:20] if len(token) > 20 else token}...")
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username:
                token_data = TokenData(username=username)
                result = await db.execute(
                    select(User).where(User.username == token_data.username)
                )
                user = result.scalar_one_or_none()
                if user and user.is_active:
                    print(f"[DEBUG] Authenticated user: {user.username}")
                    return user
        except JWTError as e:
            print(f"[DEBUG] JWT decode error: {e}")
    
    # Create or get guest session
    guest_id = request.headers.get("x-guest-id") or request.headers.get("X-Guest-ID")
    if not guest_id:
        guest_id = str(uuid.uuid4())
    
    print(f"[DEBUG] Creating guest session: {guest_id}")
    return GuestSession(guest_id)


def is_guest_user(user: Union[User, GuestSession]) -> bool:
    """Check if the user is a guest"""
    return isinstance(user, GuestSession)