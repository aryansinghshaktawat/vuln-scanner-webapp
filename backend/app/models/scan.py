"""Scan record and execution status model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(36), primary_key=True, index=True)
    asset_id = Column(
        String(36),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    target = Column(String(255), nullable=False, index=True)
    profile = Column(String(50), default="quick", nullable=False)  # quick, full, custom
    status = Column(
        String(30), default="QUEUED", nullable=False, index=True
    )  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED, TIMEOUT
    progress_phase = Column(String(100), default="Queued", nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, default=0.0, nullable=False)

    risk_score = Column(Integer, default=0, nullable=False)
    raw_output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_by = Column(String(50), default="system", nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    asset = relationship("Asset", back_populates="scans")
    ports = relationship(
        "PortFinding", back_populates="scan", cascade="all, delete-orphan"
    )
    findings = relationship(
        "VulnerabilityFinding", back_populates="scan", cascade="all, delete-orphan"
    )
