"""Notification and alert center endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.audit import Notification
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NotificationItem(BaseModel):
    id: str
    event_type: str
    severity: str
    title: str
    message: str
    target_id: str | None = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


router = APIRouter(prefix="/notifications", tags=["Notifications & Alerts"])


@router.get("", response_model=List[NotificationItem])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the most recent security notifications."""
    notifications = (
        db.query(Notification).order_by(Notification.created_at.desc()).limit(30).all()
    )
    return [NotificationItem.model_validate(n) for n in notifications]


@router.post("/{notification_id}/read", status_code=status.HTTP_200_OK)
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read."""
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    return {"success": True}


@router.post("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all unread notifications as read."""
    db.query(Notification).filter(Notification.is_read.is_(False)).update(
        {"is_read": True}
    )
    db.commit()
    return {"success": True}
