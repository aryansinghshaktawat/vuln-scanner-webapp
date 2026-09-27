"""Pydantic schemas for Dashboard metrics and visualizations."""

from typing import List
from pydantic import BaseModel


class SeverityCount(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class FindingStatusCount(BaseModel):
    open: int = 0
    acknowledged: int = 0
    in_progress: int = 0
    resolved: int = 0
    false_positive: int = 0


class ServiceStat(BaseModel):
    service: str
    count: int


class AssetRiskDistribution(BaseModel):
    critical: int = 0  # Score >= 80
    high: int = 0  # Score 60-79
    medium: int = 0  # Score 30-59
    low: int = 0  # Score < 30


class TrendPoint(BaseModel):
    date: str
    vulnerabilities: int
    scans: int


class DashboardMetrics(BaseModel):
    total_assets: int
    scanned_recently: int
    open_vulnerabilities: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    new_vulnerabilities_7d: int
    resolved_vulnerabilities_7d: int
    failed_scans_count: int

    severity_breakdown: SeverityCount
    status_breakdown: FindingStatusCount
    service_distribution: List[ServiceStat]
    asset_risk_distribution: AssetRiskDistribution
    trends_30d: List[TrendPoint]
