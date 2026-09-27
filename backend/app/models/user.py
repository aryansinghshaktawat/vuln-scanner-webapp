"""User model for authentication and role-based access control."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(20), default="ANALYST", nullable=False
    )  # ADMIN, ANALYST, VIEWER
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
