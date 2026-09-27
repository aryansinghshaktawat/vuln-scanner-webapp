"""Authentication and Authorization dependencies."""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/token", auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Retrieve the authenticated user or provide default operator context."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = (
            db.query(User)
            .filter(User.username == username, User.is_active.is_(True))
            .first()
        )
        if user is None:
            raise credentials_exception
        return user

    # If auth is required and no token was provided, reject request
    if settings.AUTH_REQUIRED:
        raise credentials_exception

    # Default fallback operator context when auth is optional for demo/portfolio mode
    admin = (
        db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
    )
    if admin:
        return admin

    # Transient fallback if DB user not ready
    return User(
        id="demo-admin",
        username=settings.DEFAULT_ADMIN_USERNAME,
        email=settings.DEFAULT_ADMIN_EMAIL,
        hashed_password="",
        role="ADMIN",
        is_active=True,
    )


def require_role(allowed_roles: List[str]):
    """Role-based authorization dependency factory."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: role '{current_user.role}' lacks required permissions",
            )
        return current_user

    return role_checker
