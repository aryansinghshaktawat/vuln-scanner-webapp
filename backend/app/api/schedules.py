"""Automated recurring scan schedule endpoints."""

import uuid
from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.models.asset import Asset
from app.models.schedule import ScanSchedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse

router = APIRouter(prefix="/schedules", tags=["Scan Schedules"])


@router.get("", response_model=List[ScheduleResponse])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all recurring scan schedules."""
    schedules = db.query(ScanSchedule).all()
    results = []
    for s in schedules:
        asset = db.query(Asset).filter(Asset.id == s.asset_id).first()
        results.append(
            ScheduleResponse(
                id=s.id,
                asset_id=s.asset_id,
                asset_name=asset.name if asset else "Unknown Asset",
                asset_target=asset.target if asset else "Unknown Target",
                profile=s.profile,
                cadence=s.cadence,
                interval_hours=s.interval_hours,
                next_run=s.next_run,
                last_run=s.last_run,
                enabled=s.enabled,
                created_at=s.created_at,
            )
        )
    return results


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Configure a new recurring scan schedule for an asset."""
    asset = db.query(Asset).filter(Asset.id == payload.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    now = datetime.now(timezone.utc)
    sched = ScanSchedule(
        id=str(uuid.uuid4()),
        asset_id=payload.asset_id,
        profile=payload.profile,
        cadence=payload.cadence,
        interval_hours=payload.interval_hours,
        next_run=now + timedelta(hours=payload.interval_hours),
        enabled=payload.enabled,
        created_at=now,
    )
    db.add(sched)
    db.commit()
    db.refresh(sched)

    return ScheduleResponse(
        id=sched.id,
        asset_id=sched.asset_id,
        asset_name=asset.name,
        asset_target=asset.target,
        profile=sched.profile,
        cadence=sched.cadence,
        interval_hours=sched.interval_hours,
        next_run=sched.next_run,
        last_run=sched.last_run,
        enabled=sched.enabled,
        created_at=sched.created_at,
    )


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: str,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN", "ANALYST"])),
):
    """Modify cadence or toggle active state of a scan schedule."""
    sched = db.query(ScanSchedule).filter(ScanSchedule.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if payload.profile is not None:
        sched.profile = payload.profile
    if payload.cadence is not None:
        sched.cadence = payload.cadence
    if payload.interval_hours is not None:
        sched.interval_hours = payload.interval_hours
    if payload.enabled is not None:
        sched.enabled = payload.enabled

    db.commit()
    db.refresh(sched)

    asset = db.query(Asset).filter(Asset.id == sched.asset_id).first()
    return ScheduleResponse(
        id=sched.id,
        asset_id=sched.asset_id,
        asset_name=asset.name if asset else "Unknown Asset",
        asset_target=asset.target if asset else "Unknown Target",
        profile=sched.profile,
        cadence=sched.cadence,
        interval_hours=sched.interval_hours,
        next_run=sched.next_run,
        last_run=sched.last_run,
        enabled=sched.enabled,
        created_at=sched.created_at,
    )


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"])),
):
    """Delete a scan schedule."""
    sched = db.query(ScanSchedule).filter(ScanSchedule.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db.delete(sched)
    db.commit()
    return None
