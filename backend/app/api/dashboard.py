"""Security posture dashboard metrics and visualization aggregations."""

from datetime import datetime, timedelta, timezone
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.asset import Asset
from app.models.scan import Scan
from app.models.finding import VulnerabilityFinding, PortFinding
from app.schemas.dashboard import (
    DashboardMetrics,
    SeverityCount,
    FindingStatusCount,
    ServiceStat,
    AssetRiskDistribution,
    TrendPoint,
)

router = APIRouter(prefix="/dashboard", tags=["Security Dashboard"])


@router.get("", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate high-level security metrics, severity breakdown, and trends."""
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)

    # 1. Total Assets & Recently Scanned Assets (within 7 days)
    total_assets = db.query(Asset).count()
    scanned_recently = (
        db.query(Asset).filter(Asset.last_scanned_at >= seven_days_ago).count()
    )

    # 2. Vulnerability Findings Counts
    open_vulns = (
        db.query(VulnerabilityFinding)
        .filter(
            VulnerabilityFinding.status.in_(["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"])
        )
        .count()
    )

    crit_vulns = (
        db.query(VulnerabilityFinding)
        .filter(
            VulnerabilityFinding.severity == "CRITICAL",
            VulnerabilityFinding.status.in_(["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"]),
        )
        .count()
    )

    high_vulns = (
        db.query(VulnerabilityFinding)
        .filter(
            VulnerabilityFinding.severity == "HIGH",
            VulnerabilityFinding.status.in_(["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"]),
        )
        .count()
    )

    new_7d = (
        db.query(VulnerabilityFinding)
        .filter(VulnerabilityFinding.first_seen >= seven_days_ago)
        .count()
    )
    resolved_7d = (
        db.query(VulnerabilityFinding)
        .filter(
            VulnerabilityFinding.status == "RESOLVED",
            VulnerabilityFinding.resolved_at >= seven_days_ago,
        )
        .count()
    )

    failed_scans = db.query(Scan).filter(Scan.status.in_(["FAILED", "TIMEOUT"])).count()

    # 3. Severity Breakdown
    all_active_findings = (
        db.query(VulnerabilityFinding)
        .filter(
            VulnerabilityFinding.status.in_(["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"])
        )
        .all()
    )

    sev_counter = Counter(f.severity.upper() for f in all_active_findings)
    severity_breakdown = SeverityCount(
        critical=sev_counter.get("CRITICAL", 0),
        high=sev_counter.get("HIGH", 0),
        medium=sev_counter.get("MEDIUM", 0),
        low=sev_counter.get("LOW", 0),
        info=sev_counter.get("INFO", 0),
    )

    # 4. Status Breakdown
    all_findings = db.query(VulnerabilityFinding).all()
    status_counter = Counter(f.status.upper() for f in all_findings)
    status_breakdown = FindingStatusCount(
        open=status_counter.get("OPEN", 0),
        acknowledged=status_counter.get("ACKNOWLEDGED", 0),
        in_progress=status_counter.get("IN_PROGRESS", 0),
        resolved=status_counter.get("RESOLVED", 0),
        false_positive=status_counter.get("FALSE_POSITIVE", 0),
    )

    # 5. Most Common Affected Services
    port_findings = (
        db.query(PortFinding.service, func.count(PortFinding.id))
        .group_by(PortFinding.service)
        .order_by(func.count(PortFinding.id).desc())
        .limit(6)
        .all()
    )
    service_distribution = [
        ServiceStat(service=p[0], count=p[1]) for p in port_findings if p[0]
    ]

    # 6. Asset Risk Distribution
    assets = db.query(Asset).all()
    risk_dist = AssetRiskDistribution()
    for a in assets:
        if a.current_risk_score >= 80:
            risk_dist.critical += 1
        elif a.current_risk_score >= 60:
            risk_dist.high += 1
        elif a.current_risk_score >= 30:
            risk_dist.medium += 1
        else:
            risk_dist.low += 1

    # 7. 30-Day Activity Trends
    trends = []
    for day_offset in range(6, -1, -1):
        d = now - timedelta(days=day_offset * 4)
        date_str = d.strftime("%b %d")
        v_count = (
            db.query(VulnerabilityFinding)
            .filter(VulnerabilityFinding.first_seen <= d)
            .count()
        )
        s_count = db.query(Scan).filter(Scan.created_at <= d).count()
        trends.append(TrendPoint(date=date_str, vulnerabilities=v_count, scans=s_count))

    return DashboardMetrics(
        total_assets=total_assets,
        scanned_recently=scanned_recently,
        open_vulnerabilities=open_vulns,
        critical_vulnerabilities=crit_vulns,
        high_vulnerabilities=high_vulns,
        new_vulnerabilities_7d=new_7d,
        resolved_vulnerabilities_7d=resolved_7d,
        failed_scans_count=failed_scans,
        severity_breakdown=severity_breakdown,
        status_breakdown=status_breakdown,
        service_distribution=service_distribution,
        asset_risk_distribution=risk_dist,
        trends_30d=trends,
    )
