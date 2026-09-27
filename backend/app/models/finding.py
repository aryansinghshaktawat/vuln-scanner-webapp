"""Port discovery and vulnerability finding ORM models."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PortFinding(Base):
    __tablename__ = "port_findings"

    id = Column(String(36), primary_key=True, index=True)
    scan_id = Column(
        String(36),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id = Column(
        String(36),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), default="tcp", nullable=False)
    state = Column(String(20), default="open", nullable=False)
    service = Column(String(100), default="unknown", nullable=False)
    version = Column(String(255), default="", nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    scan = relationship("Scan", back_populates="ports")


class VulnerabilityFinding(Base):
    __tablename__ = "vulnerability_findings"

    id = Column(String(36), primary_key=True, index=True)
    scan_id = Column(
        String(36),
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id = Column(
        String(36),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    cve_id = Column(String(30), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    affected_host = Column(String(255), nullable=False)
    affected_port = Column(Integer, nullable=True)
    service = Column(String(100), nullable=True)
    service_version = Column(String(255), nullable=True)

    severity = Column(
        String(20), default="MEDIUM", nullable=False, index=True
    )  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    cvss_score = Column(Float, nullable=True)
    is_known_exploit = Column(
        String(10), default="UNKNOWN", nullable=False
    )  # YES, NO, UNKNOWN (from CISA KEV)
    evidence = Column(Text, nullable=True)
    detection_source = Column(String(100), default="nmap-nse-vuln", nullable=False)

    first_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_seen = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(
        String(30), default="OPEN", nullable=False, index=True
    )  # OPEN, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, FALSE_POSITIVE

    remediation_owner = Column(String(100), nullable=True)
    remediation_notes = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="findings")
    asset = relationship("Asset", back_populates="findings")
