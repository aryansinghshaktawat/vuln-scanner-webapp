"""Vulnerability findings lifecycle and remediation tracking endpoints."""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.scan import Scan
from app.models.finding import VulnerabilityFinding
from app.models.audit import AuditEvent
from app.schemas.finding import FindingResponse, FindingUpdate, VerifyFixResponse
from app.scanner.worker import scan_worker

router = APIRouter(
    prefix="/vulnerabilities", tags=["Vulnerability Tracking & Remediation"]
)


@router.get("", response_model=List[FindingResponse])
def list_vulnerabilities(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity_filter: Optional[str] = Query(None, alias="severity"),
    asset_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List vulnerability findings across monitored assets with multi-parameter filtering."""
    query = db.query(VulnerabilityFinding)
    if status_filter:
        query = query.filter(VulnerabilityFinding.status == status_filter.upper())
    if severity_filter:
        query = query.filter(VulnerabilityFinding.severity == severity_filter.upper())
    if asset_id:
        query = query.filter(VulnerabilityFinding.asset_id == asset_id)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (VulnerabilityFinding.cve_id.ilike(s))
            | (VulnerabilityFinding.title.ilike(s))
            | (VulnerabilityFinding.affected_host.ilike(s))
        )

    findings = (
        query.order_by(VulnerabilityFinding.last_seen.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [FindingResponse.model_validate(f) for f in findings]


@router.get("/{finding_id}", response_model=FindingResponse)
def get_vulnerability(
    finding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full finding details including evidence and remediation history."""
    finding = (
        db.query(VulnerabilityFinding)
        .filter(VulnerabilityFinding.id == finding_id)
        .first()
    )
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return FindingResponse.model_validate(finding)


@router.put("/{finding_id}", response_model=FindingResponse)
def update_vulnerability_remediation(
    finding_id: str,
    payload: FindingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Update remediation status, assigned owner, or analyst mitigation notes."""
    finding = (
        db.query(VulnerabilityFinding)
        .filter(VulnerabilityFinding.id == finding_id)
        .first()
    )
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_status = finding.status
    if payload.status is not None:
        finding.status = payload.status
        if payload.status == "RESOLVED":
            finding.resolved_at = datetime.now(timezone.utc)
    if payload.remediation_owner is not None:
        finding.remediation_owner = payload.remediation_owner
    if payload.remediation_notes is not None:
        finding.remediation_notes = payload.remediation_notes
    if payload.recommendation is not None:
        finding.recommendation = payload.recommendation
    if payload.due_date is not None:
        finding.due_date = payload.due_date

    audit = AuditEvent(
        id=str(uuid.uuid4()),
        user_id=current_user.username,
        action="FINDING_UPDATED",
        resource_type="finding",
        resource_id=finding.id,
        details=f"Finding {finding.cve_id} status changed from {old_status} to {finding.status}",
    )
    db.add(audit)
    db.commit()
    db.refresh(finding)
    return FindingResponse.model_validate(finding)


@router.post("/{finding_id}/verify", response_model=VerifyFixResponse)
async def verify_remediation_fix(
    finding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Trigger a verification scan to confirm whether a vulnerability has been remediated."""
    finding = (
        db.query(VulnerabilityFinding)
        .filter(VulnerabilityFinding.id == finding_id)
        .first()
    )
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    target = finding.affected_host
    scan_id = str(uuid.uuid4())
    scan = Scan(
        id=scan_id,
        asset_id=finding.asset_id,
        target=target,
        profile="full",
        status="QUEUED",
        progress_phase=f"Verification scan for {finding.cve_id}",
        created_by=f"verify:{current_user.username}",
        created_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    db.commit()

    # Enqueue verification scan
    await scan_worker.enqueue_scan(scan_id)

    return VerifyFixResponse(
        finding_id=finding.id,
        cve_id=finding.cve_id,
        status="IN_VERIFICATION",
        verified=False,
        message=(
            f"Verification scan ({scan_id[:8]}) scheduled for {target}. "
            "Results will update finding status upon scan completion."
        ),
        rescan_id=scan_id,
    )
