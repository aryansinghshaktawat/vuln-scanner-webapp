"""Scan schedule ORM model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ScanSchedule(Base):
    __tablename__ = "scan_schedules"

    id = Column(String(36), primary_key=True, index=True)
    asset_id = Column(
        String(36),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    profile = Column(String(50), default="full", nullable=False)
    cadence = Column(String(50), default="Every 24 hours", nullable=False)
    interval_hours = Column(Integer, default=24, nullable=False)
    next_run = Column(DateTime(timezone=True), nullable=False)
    last_run = Column(DateTime(timezone=True), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    asset = relationship("Asset", back_populates="schedules")
