"""Pydantic schemas for Vulnerability Findings and Remediation Lifecycle."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FindingBase(BaseModel):
    cve_id: str
    title: str
    description: Optional[str] = None
    affected_host: str
    affected_port: Optional[int] = None
    service: Optional[str] = None
    service_version: Optional[str] = None
    severity: str = Field("MEDIUM", pattern="^(CRITICAL|HIGH|MEDIUM|LOW|INFO)$")
    cvss_score: Optional[float] = None
    is_known_exploit: str = "UNKNOWN"
    evidence: Optional[str] = None
    detection_source: str = "nmap-nse-vuln"


class FindingResponse(FindingBase):
    id: str
    scan_id: str
    asset_id: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    status: str
    remediation_owner: Optional[str] = None
    remediation_notes: Optional[str] = None
    recommendation: Optional[str] = None
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FindingUpdate(BaseModel):
    status: Optional[str] = Field(
        None, pattern="^(OPEN|ACKNOWLEDGED|IN_PROGRESS|RESOLVED|FALSE_POSITIVE)$"
    )
    remediation_owner: Optional[str] = None
    remediation_notes: Optional[str] = None
    recommendation: Optional[str] = None
    due_date: Optional[datetime] = None


class VerifyFixResponse(BaseModel):
    finding_id: str
    cve_id: str
    status: str
    verified: bool
    message: str
    verified_at: Optional[datetime] = None
    rescan_id: Optional[str] = None
