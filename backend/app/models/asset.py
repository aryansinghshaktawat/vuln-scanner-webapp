"""Asset inventory model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    target = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    environment = Column(
        String(50), default="production", nullable=False
    )  # production, staging, development, internal
    owner = Column(String(100), default="Security Operations", nullable=False)
    criticality = Column(
        String(20), default="high", nullable=False
    )  # critical, high, medium, low
    tags = Column(
        String(255), default="", nullable=False
    )  # Comma-delimited: e.g. web,dmz,public-facing

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_scanned_at = Column(DateTime(timezone=True), nullable=True)
    scan_status = Column(
        String(30), default="UNCHECKED", nullable=False
    )  # UNCHECKED, QUEUED, RUNNING, COMPLETED, FAILED
    current_risk_score = Column(Integer, default=0, nullable=False)

    # Relationships
    scans = relationship(
        "Scan",
        back_populates="asset",
        cascade="all, delete-orphan",
        order_by="desc(Scan.created_at)",
    )
    findings = relationship(
        "VulnerabilityFinding", back_populates="asset", cascade="all, delete-orphan"
    )
    schedules = relationship(
        "ScanSchedule", back_populates="asset", cascade="all, delete-orphan"
    )
