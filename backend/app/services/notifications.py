"""Extensible alerting and notification dispatching architecture."""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
from sqlalchemy.orm import Session
from app.config import settings
from app.models.audit import Notification
import uuid

logger = logging.getLogger("northstar.notifications")


class BaseNotificationChannel(ABC):
    """Abstract base class for notification delivery providers."""

    name: str

    @abstractmethod
    async def dispatch(
        self,
        title: str,
        message: str,
        severity: str,
        event_type: str,
        target_id: Optional[str] = None,
    ) -> bool:
        pass


class LogNotificationChannel(BaseNotificationChannel):
    name = "log"

    async def dispatch(
        self,
        title: str,
        message: str,
        severity: str,
        event_type: str,
        target_id: Optional[str] = None,
    ) -> bool:
        logger.warning(
            "[SECURITY ALERT %s] %s: %s (target: %s)",
            severity,
            title,
            message,
            target_id,
        )
        return True


class WebhookNotificationChannel(BaseNotificationChannel):
    name = "webhook"

    async def dispatch(
        self,
        title: str,
        message: str,
        severity: str,
        event_type: str,
        target_id: Optional[str] = None,
    ) -> bool:
        if not settings.ALERT_WEBHOOK_URL:
            return False

        payload = {
            "title": title,
            "message": message,
            "severity": severity,
            "event_type": event_type,
            "target_id": target_id,
            "platform": "Northstar Security Platform",
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(settings.ALERT_WEBHOOK_URL, json=payload)
                return resp.status_code < 300
        except Exception as e:
            logger.error("Failed to deliver alert webhook: %s", str(e))
            return False


class NotificationService:
    """Manages dispatch of security events across configured notification channels."""

    def __init__(self):
        self.channels: List[BaseNotificationChannel] = [
            LogNotificationChannel(),
            WebhookNotificationChannel(),
        ]

    def register_channel(self, channel: BaseNotificationChannel) -> None:
        self.channels.append(channel)

    async def send_alert(
        self,
        db: Session,
        title: str,
        message: str,
        severity: str = "INFO",
        event_type: str = "GENERIC_EVENT",
        target_id: Optional[str] = None,
    ) -> Notification:
        """Persist alert notification in database and broadcast to external channels."""
        # 1. Store in database for UI notification center
        notification = Notification(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            severity=severity.upper(),
            event_type=event_type,
            target_id=target_id,
            is_read=False,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # 2. Dispatch to registered external channels asynchronously
        for channel in self.channels:
            try:
                await channel.dispatch(title, message, severity, event_type, target_id)
            except Exception as e:
                logger.error("Channel %s error: %s", channel.name, str(e))

        return notification


notification_service = NotificationService()
