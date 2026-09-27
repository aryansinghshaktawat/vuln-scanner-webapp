"""Authentication and user management endpoints."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.audit import AuditEvent
from app.schemas.user import UserCreate, UserResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate with username/password and return signed JWT."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    token = create_access_token(data={"sub": user.username, "role": user.role})

    # Audit log
    audit = AuditEvent(
        id=str(uuid.uuid4()),
        user_id=user.username,
        action="USER_LOGIN",
        resource_type="auth",
        resource_id=user.id,
        details="User successfully authenticated",
    )
    db.add(audit)
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role,
    )


@router.post("/register", response_model=UserResponse)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"])),
):
    """Admin-only endpoint to register a new platform user."""
    existing = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    user = User(
        id=str(uuid.uuid4()),
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve details for current authenticated session."""
    return current_user
