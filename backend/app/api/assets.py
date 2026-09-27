"""Asset Inventory REST endpoints."""

import uuid
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.asset import Asset
from app.models.scan import Scan
from app.models.finding import VulnerabilityFinding, PortFinding
from app.models.audit import AuditEvent
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.schemas.scan import ScanHistoryItem
from app.schemas.finding import FindingResponse
from app.schemas.diff import DiffResponse
from app.scanner.validator import validate_and_normalize_target
from app.scanner.diff import compute_scan_diff

router = APIRouter(prefix="/assets", tags=["Asset Inventory"])


@router.get("", response_model=List[AssetResponse])
def list_assets(
    search: Optional[str] = Query(None, description="Search by name, target, or owner"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    criticality: Optional[str] = Query(None, description="Filter by criticality"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all monitored assets in inventory."""
    query = db.query(Asset)
    if environment:
        query = query.filter(Asset.environment == environment.lower())
    if criticality:
        query = query.filter(Asset.criticality == criticality.lower())
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (Asset.name.ilike(s)) | (Asset.target.ilike(s)) | (Asset.owner.ilike(s))
        )

    assets = query.order_by(Asset.created_at.desc()).all()
    results = []
    for a in assets:
        resp = AssetResponse.model_validate(a)
        # Compute open ports count and vuln count from latest completed scan
        latest_scan = (
            db.query(Scan)
            .filter(Scan.asset_id == a.id, Scan.status == "COMPLETED")
            .order_by(Scan.created_at.desc())
            .first()
        )
        if latest_scan:
            resp.open_ports_count = (
                db.query(PortFinding)
                .filter(PortFinding.scan_id == latest_scan.id)
                .count()
            )
            resp.vulnerabilities_count = (
                db.query(VulnerabilityFinding)
                .filter(
                    VulnerabilityFinding.asset_id == a.id,
                    VulnerabilityFinding.status.in_(
                        ["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"]
                    ),
                )
                .count()
            )
        results.append(resp)
    return results


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Register an authorized network asset into inventory."""
    try:
        normalized_target = validate_and_normalize_target(payload.target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Check for existing asset with same target
    existing = db.query(Asset).filter(Asset.target == normalized_target).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Asset with target '{normalized_target}' already exists",
        )

    asset = Asset(
        id=str(uuid.uuid4()),
        name=payload.name.strip(),
        target=normalized_target,
        description=payload.description,
        environment=payload.environment.lower(),
        owner=payload.owner.strip(),
        criticality=payload.criticality.lower(),
        tags=payload.tags.strip(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        scan_status="UNCHECKED",
        current_risk_score=0,
    )
    db.add(asset)

    audit = AuditEvent(
        id=str(uuid.uuid4()),
        user_id=current_user.username,
        action="ASSET_CREATED",
        resource_type="asset",
        resource_id=asset.id,
        details=f"Asset '{asset.name}' with target '{asset.target}' created",
    )
    db.add(audit)
    db.commit()
    db.refresh(asset)
    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed metadata for a specific asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    resp = AssetResponse.model_validate(asset)
    latest_scan = (
        db.query(Scan)
        .filter(Scan.asset_id == asset.id, Scan.status == "COMPLETED")
        .order_by(Scan.created_at.desc())
        .first()
    )
    if latest_scan:
        resp.open_ports_count = (
            db.query(PortFinding).filter(PortFinding.scan_id == latest_scan.id).count()
        )
        resp.vulnerabilities_count = (
            db.query(VulnerabilityFinding)
            .filter(
                VulnerabilityFinding.asset_id == asset.id,
                VulnerabilityFinding.status.in_(
                    ["OPEN", "IN_PROGRESS", "ACKNOWLEDGED"]
                ),
            )
            .count()
        )
    return resp


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: str,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Update metadata for an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if payload.name is not None:
        asset.name = payload.name.strip()
    if payload.description is not None:
        asset.description = payload.description
    if payload.environment is not None:
        asset.environment = payload.environment.lower()
    if payload.owner is not None:
        asset.owner = payload.owner.strip()
    if payload.criticality is not None:
        asset.criticality = payload.criticality.lower()
    if payload.tags is not None:
        asset.tags = payload.tags.strip()

    asset.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(asset)
    return AssetResponse.model_validate(asset)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"])),
):
    """Delete an asset and cascade its associated scans/findings."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    audit = AuditEvent(
        id=str(uuid.uuid4()),
        user_id=current_user.username,
        action="ASSET_DELETED",
        resource_type="asset",
        resource_id=asset_id,
        details=f"Asset '{asset.name}' deleted",
    )
    db.add(audit)
    db.commit()
    return None


@router.get("/{asset_id}/scans", response_model=List[ScanHistoryItem])
def get_asset_scans(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve scan execution history for an asset."""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    scans = (
        db.query(Scan)
        .filter(Scan.asset_id == asset_id)
        .order_by(Scan.created_at.desc())
        .all()
    )
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


@router.get("/{asset_id}/vulnerabilities", response_model=List[FindingResponse])
def get_asset_vulnerabilities(
    asset_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all vulnerability findings associated with an asset."""
    query = db.query(VulnerabilityFinding).filter(
        VulnerabilityFinding.asset_id == asset_id
    )
    if status_filter:
        query = query.filter(VulnerabilityFinding.status == status_filter.upper())
    findings = query.order_by(VulnerabilityFinding.first_seen.desc()).all()
    return [FindingResponse.model_validate(f) for f in findings]


@router.get("/{asset_id}/diff", response_model=DiffResponse)
def get_asset_scan_diff(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare latest completed scan against the previous scan for this asset."""
    scans = (
        db.query(Scan)
        .filter(Scan.asset_id == asset_id, Scan.status == "COMPLETED")
        .order_by(Scan.created_at.desc())
        .limit(2)
        .all()
    )

    current_scan = scans[0] if len(scans) > 0 else None
    previous_scan = scans[1] if len(scans) > 1 else None

    return compute_scan_diff(current_scan, previous_scan)
