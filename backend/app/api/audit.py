"""Audit logging trail endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import require_role
from app.models.user import User
from app.models.audit import AuditEvent
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AuditItem(BaseModel):
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str | None = None
    details: str | None = None
    ip_address: str | None = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/audit", tags=["Audit Log"])


@router.get("", response_model=List[AuditItem])
def list_audit_trail(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["ADMIN"])),
):
    """Retrieve immutable audit logging records (Admin only)."""
    events = (
        db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
    )
    return [AuditItem.model_validate(e) for e in events]
