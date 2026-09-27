"""Pydantic schemas for Scan orchestration and history."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PortResponse(BaseModel):
    id: Optional[str] = None
    port: int
    protocol: str = "tcp"
    state: str = "open"
    service: str = "unknown"
    version: str = ""

    model_config = ConfigDict(from_attributes=True)


class FindingSummary(BaseModel):
    id: str
    cve_id: str
    title: str
    severity: str
    affected_port: Optional[int] = None
    service: Optional[str] = None
    status: str
    is_known_exploit: str

    model_config = ConfigDict(from_attributes=True)


class ScanCreate(BaseModel):
    target: Optional[str] = Field(None, min_length=1, max_length=253)
    asset_id: Optional[str] = None
    profile: str = Field("quick", pattern="^(quick|full|port_only|vuln_only)$")


class ScanResponse(BaseModel):
    id: str
    asset_id: Optional[str] = None
    target: str
    profile: str
    status: str
    progress_phase: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float
    risk_score: int
    raw_output: Optional[str] = None
    error_message: Optional[str] = None
    created_by: str
    created_at: datetime

    open_ports: List[PortResponse] = []
    findings: List[FindingSummary] = []
    risk_reasons: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class ScanHistoryItem(BaseModel):
    id: str
    asset_id: Optional[str] = None
    target: str
    profile: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float
    open_ports_count: int
    vulnerabilities_count: int
    risk_score: int

    model_config = ConfigDict(from_attributes=True)
