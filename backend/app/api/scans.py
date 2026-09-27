"""Scan management, orchestration, diffing, and SSE live progress endpoints."""

import asyncio
import json
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.asset import Asset
from app.models.scan import Scan
from app.models.audit import AuditEvent
from app.schemas.scan import (
    ScanCreate,
    ScanResponse,
    ScanHistoryItem,
    PortResponse,
    FindingSummary,
)
from app.schemas.diff import DiffResponse
from app.scanner.validator import validate_and_normalize_target
from app.scanner.worker import scan_worker
from app.scanner.diff import compute_scan_diff
from app.scanner.risk import calculate_risk_score

router = APIRouter(prefix="/scans", tags=["Scan Management"])


@router.post("", response_model=ScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_and_start_scan(
    payload: ScanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Initiate a new authorized Nmap scan job."""
    target = ""
    asset_id = payload.asset_id

    if asset_id:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Selected asset does not exist")
        target = asset.target
    elif payload.target:
        try:
            target = validate_and_normalize_target(payload.target)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        # Check if matching asset already exists for this target
        matched_asset = db.query(Asset).filter(Asset.target == target).first()
        if matched_asset:
            asset_id = matched_asset.id
    else:
        raise HTTPException(
            status_code=400, detail="Either 'asset_id' or 'target' must be provided"
        )

    scan_id = str(uuid.uuid4())
    scan = Scan(
        id=scan_id,
        asset_id=asset_id,
        target=target,
        profile=payload.profile,
        status="QUEUED",
        progress_phase="Queued in scan scheduler",
        created_by=current_user.username,
        created_at=datetime.now(timezone.utc),
    )
    db.add(scan)

    audit = AuditEvent(
        id=str(uuid.uuid4()),
        user_id=current_user.username,
        action="SCAN_STARTED",
        resource_type="scan",
        resource_id=scan_id,
        details=f"Scan initiated for {target} ({payload.profile} profile)",
    )
    db.add(audit)
    db.commit()
    db.refresh(scan)

    # Enqueue scan to background worker
    await scan_worker.enqueue_scan(scan_id)

    return ScanResponse(
        id=scan.id,
        asset_id=scan.asset_id,
        target=scan.target,
        profile=scan.profile,
        status=scan.status,
        progress_phase=scan.progress_phase,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        duration_seconds=scan.duration_seconds,
        risk_score=scan.risk_score,
        raw_output=scan.raw_output,
        error_message=scan.error_message,
        created_by=scan.created_by,
        created_at=scan.created_at,
        open_ports=[],
        findings=[],
        risk_reasons=[],
    )


@router.get("", response_model=List[ScanHistoryItem])
def list_scans(
    status_filter: Optional[str] = Query(None, alias="status"),
    target_filter: Optional[str] = Query(None, alias="target"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List historical scan executions with filtering."""
    query = db.query(Scan)
    if status_filter:
        query = query.filter(Scan.status == status_filter.upper())
    if target_filter:
        query = query.filter(Scan.target.ilike(f"%{target_filter.strip()}%"))

    scans = query.order_by(Scan.created_at.desc()).offset(offset).limit(limit).all()
    results = []
    for s in scans:
        results.append(
            ScanHistoryItem(
                id=s.id,
                asset_id=s.asset_id,
                target=s.target,
                profile=s.profile,
                status=s.status,
                started_at=s.started_at,
                completed_at=s.completed_at,
                duration_seconds=s.duration_seconds,
                open_ports_count=len(s.ports),
                vulnerabilities_count=len(s.findings),
                risk_score=s.risk_score,
            )
        )
    return results


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve full details, open ports, and findings for a specific scan."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    ports_resp = [
        PortResponse(
            id=p.id,
            port=p.port,
            protocol=p.protocol,
            state=p.state,
            service=p.service,
            version=p.version or "",
        )
        for p in scan.ports
    ]

    findings_resp = [
        FindingSummary(
            id=f.id,
            cve_id=f.cve_id,
            title=f.title,
            severity=f.severity,
            affected_port=f.affected_port,
            service=f.service,
            status=f.status,
            is_known_exploit=f.is_known_exploit,
        )
        for f in scan.findings
    ]

    # Calculate explainable risk reasons
    crit = scan.asset.criticality if scan.asset else "high"
    env = scan.asset.environment if scan.asset else "production"
    tags = scan.asset.tags if scan.asset else ""
    port_dicts = [
        {"port": p.port, "protocol": p.protocol, "service": p.service}
        for p in scan.ports
    ]
    finding_dicts = [
        {"severity": f.severity, "is_known_exploit": f.is_known_exploit}
        for f in scan.findings
    ]
    _, reasons = calculate_risk_score(port_dicts, finding_dicts, crit, env, tags)

    return ScanResponse(
        id=scan.id,
        asset_id=scan.asset_id,
        target=scan.target,
        profile=scan.profile,
        status=scan.status,
        progress_phase=scan.progress_phase,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        duration_seconds=scan.duration_seconds,
        risk_score=scan.risk_score,
        raw_output=scan.raw_output,
        error_message=scan.error_message,
        created_by=scan.created_by,
        created_at=scan.created_at,
        open_ports=ports_resp,
        findings=findings_resp,
        risk_reasons=reasons,
    )


@router.post("/{scan_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Cancel an active or queued scan job."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status in ["COMPLETED", "FAILED", "CANCELLED", "TIMEOUT"]:
        return {"message": f"Scan is already in terminal state: {scan.status}"}

    cancelled = scan_worker.cancel_scan(scan_id)
    scan.status = "CANCELLED"
    scan.progress_phase = "Scan cancelled by operator"
    scan.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Scan cancellation signal dispatched", "success": cancelled}


@router.get("/{scan_id}/diff", response_model=DiffResponse)
def get_scan_diff_endpoint(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare this scan against the immediately preceding scan on the same target."""
    current_scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not current_scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Find prior scan for same target
    previous_scan = (
        db.query(Scan)
        .filter(
            Scan.target == current_scan.target,
            Scan.created_at < current_scan.created_at,
            Scan.status == "COMPLETED",
        )
        .order_by(Scan.created_at.desc())
        .first()
    )

    return compute_scan_diff(current_scan, previous_scan)


@router.get("/{scan_id}/stream")
async def stream_scan_progress(scan_id: str, db: Session = Depends(get_db)):
    """Server-Sent Events (SSE) endpoint providing real-time status and phase updates."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    async def event_generator():
        # First send initial current state
        initial_data = {
            "status": scan.status,
            "progress_phase": scan.progress_phase,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": (
                scan.completed_at.isoformat() if scan.completed_at else None
            ),
            "risk_score": scan.risk_score,
        }
        yield f"data: {json.dumps(initial_data)}\n\n"

        # If already done, close stream immediately
        if scan.status in ["COMPLETED", "FAILED", "CANCELLED", "TIMEOUT"]:
            return

        # Subscribe to live updates from worker
        queue = scan_worker.subscribe(scan_id)
        try:
            while True:
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(update)}\n\n"
                    if update.get("status") in [
                        "COMPLETED",
                        "FAILED",
                        "CANCELLED",
                        "TIMEOUT",
                    ]:
                        break
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield ": keepalive\n\n"
        finally:
            scan_worker.unsubscribe(scan_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
