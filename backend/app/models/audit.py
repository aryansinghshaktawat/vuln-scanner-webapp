"""Audit logging and Notification ORM models."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime
from app.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(50), default="system", nullable=False)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, index=True)
    event_type = Column(
        String(50), nullable=False
    )  # VULNERABILITY_CRITICAL, SCAN_FAILED, ASSET_NEW, etc.
    severity = Column(
        String(20), default="INFO", nullable=False
    )  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    target_id = Column(String(100), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
