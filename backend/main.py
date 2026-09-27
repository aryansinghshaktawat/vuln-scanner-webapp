"""Northstar Network Vulnerability Management Platform.

FastAPI Application Entry Point.
Provides RESTful APIs, background scan worker orchestration, persistence layer,
and backward-compatible legacy endpoints for Quick and Full Nmap scanning.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import init_db, get_db, SessionLocal
from app.api import api_router
from app.scanner.engine import is_nmap_available, NmapEngine
from app.scanner.validator import validate_and_normalize_target
from app.scanner.parser import parse_ports, parse_vulnerabilities
from app.scanner.risk import calculate_risk_score
from app.scanner.diff import compute_scan_diff
from app.scanner.worker import scan_worker, safe_duration
from app.services.scheduler import scheduler_service
from app.services.intelligence import intelligence_service
from app.models.asset import Asset
from app.models.scan import Scan
from app.models.finding import VulnerabilityFinding, PortFinding
from app.models.schedule import ScanSchedule
import uuid

# Configure Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("northstar.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables and bootstrap records...")
    init_db()

    # Recover any stale scans left in RUNNING or QUEUED from an unexpected restart
    with SessionLocal() as db:
        stale_scans = db.query(Scan).filter(Scan.status.in_(["RUNNING", "QUEUED"])).all()
        for s in stale_scans:
            s.status = "FAILED"
            s.progress_phase = "Scan interrupted by server restart"
            s.error_message = "Scan process interrupted by server restart. Please re-run."
            s.completed_at = datetime.now(timezone.utc)
        if stale_scans:
            db.commit()
            logger.info("Recovered %d interrupted scan(s) from previous session", len(stale_scans))

    logger.info("Starting background scan worker...")
    scan_worker.start()

    logger.info("Starting background scan scheduler...")
    scheduler_service.start()

    # Asynchronously refresh CISA KEV threat intelligence in background
    asyncio.create_task(intelligence_service.refresh_cisa_kev())

    yield

    logger.info("Shutting down background services...")
    scheduler_service.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional Network Vulnerability Management Platform powered by Nmap.",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router, prefix=settings.API_PREFIX)


# =========================================================================
# BACKWARD COMPATIBILITY & SYSTEM HEALTH ENDPOINTS
# Preserves existing quick/full scanning, health checks, and dashboard calls
# =========================================================================


@app.get("/", tags=["System"])
def root() -> Dict[str, str]:
    """Service status and identification."""
    return {
        "service": "northstar-security-platform",
        "version": settings.VERSION,
        "status": "ready",
        "nmap_available": str(is_nmap_available()),
    }


@app.get("/health", tags=["System"])
def health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """System health check endpoint verifying database and Nmap availability."""
    db_ok = False
    try:
        db.execute(Asset.__table__.select().limit(1))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "api": True,
        "nmap": is_nmap_available(),
        "database": db_ok,
        "version": settings.VERSION,
    }


def _execute_sync_scan(target_raw: str, deep: bool, db: Session) -> Dict[str, Any]:
    """Execute scan synchronously for legacy HTTP endpoints and persist results to DB."""
    try:
        clean_target = validate_and_normalize_target(target_raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not is_nmap_available():
        raise HTTPException(
            status_code=503, detail="Nmap scanner is not available on this system"
        )

    profile_name = "full" if deep else "quick"

    # Find or link matching asset
    asset = db.query(Asset).filter(Asset.target == clean_target).first()

    scan_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    scan = Scan(
        id=scan_id,
        asset_id=asset.id if asset else None,
        target=clean_target,
        profile=profile_name,
        status="RUNNING",
        progress_phase="Executing scan",
        started_at=started_at,
        created_by="legacy_api",
        created_at=started_at,
    )
    db.add(scan)
    db.commit()

    try:
        # Run Nmap subprocess
        # Use asyncio runner to call NmapEngine cleanly
        loop = asyncio.get_event_loop()
        exit_code, stdout, stderr = loop.run_until_complete(
            NmapEngine.run_scan(clean_target, profile_name)
        )
    except TimeoutError as e:
        scan.status = "TIMEOUT"
        scan.error_message = str(e)
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        scan.status = "FAILED"
        scan.error_message = str(e)
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Scan execution error: {str(e)}")

    # Parse ports
    ports = parse_ports(stdout)
    for p in ports:
        db.add(
            PortFinding(
                id=str(uuid.uuid4()),
                scan_id=scan.id,
                asset_id=asset.id if asset else None,
                port=p["port"],
                protocol=p["protocol"],
                state=p["state"],
                service=p["service"],
                version=p["version"],
            )
        )

    # Parse vulnerabilities if full scan
    vulns = parse_vulnerabilities(stdout, clean_target, ports) if deep else []
    now = datetime.now(timezone.utc)
    for v in vulns:
        db.add(
            VulnerabilityFinding(
                id=str(uuid.uuid4()),
                scan_id=scan.id,
                asset_id=asset.id if asset else None,
                cve_id=v["cve_id"],
                title=v["title"],
                description=v["description"],
                affected_host=v["affected_host"],
                affected_port=v["affected_port"],
                service=v["service"],
                service_version=v["service_version"],
                severity=v["severity"],
                cvss_score=v["cvss_score"],
                evidence=v["evidence"],
                detection_source=v["detection_source"],
                first_seen=now,
                last_seen=now,
                status="OPEN",
                recommendation="Update service to current vendor release.",
            )
        )

    # Calculate explainable risk score
    crit = asset.criticality if asset else "high"
    env = asset.environment if asset else "production"
    tags = asset.tags if asset else ""
    risk_score, _ = calculate_risk_score(ports, vulns, crit, env, tags)

    completed_at = datetime.now(timezone.utc)
    duration = safe_duration(started_at, completed_at)

    scan.status = "COMPLETED"
    scan.progress_phase = "Completed"
    scan.completed_at = completed_at
    scan.duration_seconds = max(0.1, round(duration, 2))
    scan.risk_score = risk_score
    scan.raw_output = stdout

    if asset:
        asset.last_scanned_at = completed_at
        asset.scan_status = "COMPLETED"
        asset.current_risk_score = risk_score

    db.commit()

    return {
        "target": clean_target,
        "open_ports": ports,
        "cves": [v["cve_id"] for v in vulns],
        "risk_score": risk_score,
        "scanned_at": completed_at.isoformat(),
        "scan_id": scan.id,
    }


@app.get("/scan/quick", tags=["Scanning"])
def quick_scan_target(
    target: str = Query(..., min_length=1, max_length=253),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Legacy quick discovery scan endpoint (ports & services)."""
    return _execute_sync_scan(target, deep=False, db=db)


@app.get("/scan", tags=["Scanning"])
def scan_target(
    target: str = Query(..., min_length=1, max_length=253),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Legacy full assessment scan endpoint (ports, services, version detection & CVEs)."""
    return _execute_sync_scan(target, deep=True, db=db)


@app.get("/assets", tags=["Legacy Compatibility"])
def legacy_assets(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Legacy assets listing endpoint."""
    assets = db.query(Asset).all()
    results = []
    for a in assets:
        findings_count = (
            db.query(VulnerabilityFinding)
            .filter(
                VulnerabilityFinding.asset_id == a.id,
                VulnerabilityFinding.status.in_(
                    ["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"]
                ),
            )
            .count()
        )
        results.append(
            {
                "id": a.id,
                "target": a.target,
                "criticality": a.criticality,
                "owner": a.owner,
                "last_seen": (
                    a.last_scanned_at.strftime("%Y-%m-%d %H:%M")
                    if a.last_scanned_at
                    else "Never"
                ),
                "findings": findings_count,
            }
        )
    return results


@app.get("/scans/history", tags=["Legacy Compatibility"])
def legacy_scan_history(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Legacy scan history endpoint."""
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(20).all()
    return [
        {
            "id": s.id,
            "target": s.target,
            "time": s.created_at.strftime("%b %d, %H:%M") if s.created_at else "",
            "status": s.status.capitalize(),
            "findings": f"{len(s.findings)} findings",
            "open_ports": len(s.ports),
            "risk_score": s.risk_score,
            "cves": [f.cve_id for f in s.findings],
        }
        for s in scans
    ]


@app.get("/scans/diff", tags=["Legacy Compatibility"])
def legacy_scan_diff(
    target: str = Query(..., min_length=1, max_length=253),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Legacy diff endpoint between latest two scans of a target."""
    try:
        clean_target = validate_and_normalize_target(target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    scans = (
        db.query(Scan)
        .filter(Scan.target == clean_target, Scan.status == "COMPLETED")
        .order_by(Scan.created_at.desc())
        .limit(2)
        .all()
    )
    current = scans[0] if len(scans) > 0 else None
    previous = scans[1] if len(scans) > 1 else None

    diff_res = compute_scan_diff(current, previous)
    return {
        "target": clean_target,
        "added_cves": [v.cve_id for v in diff_res.new_vulnerabilities],
        "removed_cves": [v.cve_id for v in diff_res.resolved_vulnerabilities],
        "persisting_cves": [v.cve_id for v in diff_res.persisting_vulnerabilities],
        "new_ports": [p.port for p in diff_res.new_ports],
        "closed_ports": [p.port for p in diff_res.closed_ports],
        "current": (
            {
                "id": current.id,
                "risk_score": current.risk_score,
                "cves": [f.cve_id for f in current.findings],
            }
            if current
            else None
        ),
        "previous": (
            {
                "id": previous.id,
                "risk_score": previous.risk_score,
                "cves": [f.cve_id for f in previous.findings],
            }
            if previous
            else None
        ),
    }


@app.get("/schedules", tags=["Legacy Compatibility"])
def legacy_schedules(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Legacy schedules endpoint."""
    schedules = db.query(ScanSchedule).all()
    results = []
    for s in schedules:
        asset = db.query(Asset).filter(Asset.id == s.asset_id).first()
        results.append(
            {
                "id": s.id,
                "target": asset.target if asset else "unknown",
                "cadence": s.cadence,
                "next_run": (
                    s.next_run.strftime("%a, %H:%M") if s.next_run else "Pending"
                ),
                "enabled": s.enabled,
            }
        )
    return results


@app.get("/remediations", tags=["Legacy Compatibility"])
def legacy_remediations(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Legacy remediations endpoint."""
    findings = (
        db.query(VulnerabilityFinding)
        .filter(
            VulnerabilityFinding.status.in_(["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"])
        )
        .order_by(VulnerabilityFinding.severity.asc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": f.id,
            "title": f.title,
            "asset": f.affected_host,
            "severity": f.severity.lower(),
            "status": f.status.lower(),
            "verified_at": f.verified_at.isoformat() if f.verified_at else None,
        }
        for f in findings
    ]


@app.post("/remediations/{remediation_id}/verify", tags=["Legacy Compatibility"])
def legacy_verify_remediation(
    remediation_id: str, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Legacy remediation verification endpoint."""
    f = (
        db.query(VulnerabilityFinding)
        .filter(VulnerabilityFinding.id == remediation_id)
        .first()
    )
    if not f:
        raise HTTPException(status_code=404, detail="Remediation not found")
    f.status = "RESOLVED"
    f.verified_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "id": f.id,
        "title": f.title,
        "asset": f.affected_host,
        "severity": f.severity.lower(),
        "status": "resolved",
        "verified_at": f.verified_at.isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )
