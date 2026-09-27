"""Pydantic schemas for Security Scan and Asset Reports."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReportMetadata(BaseModel):
    generated_at: datetime
    report_title: str
    target: str
    asset_name: Optional[str] = None
    environment: Optional[str] = None
    criticality: Optional[str] = None
    scan_id: Optional[str] = None
    risk_score: int
    executive_summary: str
