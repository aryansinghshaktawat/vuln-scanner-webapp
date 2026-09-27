"""Background recurring scan scheduler using APScheduler."""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import SessionLocal
from app.models.schedule import ScanSchedule
from app.models.asset import Asset
from app.models.scan import Scan
from app.scanner.worker import scan_worker

logger = logging.getLogger("northstar.scheduler")


class ScanSchedulerService:
    """Manages recurring automated scans."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False

    def start(self) -> None:
        """Initialize scheduler jobs and start the async scheduler."""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            # Add periodic polling job to check for scheduled scans every 60 seconds
            self.scheduler.add_job(
                self._check_and_trigger_schedules,
                "interval",
                minutes=1,
                id="schedule_poller",
                replace_existing=True,
            )
            logger.info("ScanSchedulerService started")

    def shutdown(self) -> None:
        if self._is_running:
            self.scheduler.shutdown(wait=False)
            self._is_running = False

    async def _check_and_trigger_schedules(self) -> None:
        """Check database for active schedules whose next_run time has arrived."""
        now = datetime.now(timezone.utc)
        with SessionLocal() as db:
            schedules = (
                db.query(ScanSchedule)
                .filter(
                    ScanSchedule.enabled.is_(True),
                    ScanSchedule.next_run <= now,
                )
                .all()
            )

            for sched in schedules:
                asset = db.query(Asset).filter(Asset.id == sched.asset_id).first()
                if not asset:
                    continue

                logger.info(
                    "Triggering scheduled scan for asset '%s' (%s)",
                    asset.name,
                    asset.target,
                )

                # Create Scan record
                scan_id = str(uuid.uuid4())
                scan = Scan(
                    id=scan_id,
                    asset_id=asset.id,
                    target=asset.target,
                    profile=sched.profile,
                    status="QUEUED",
                    progress_phase="Queued by automated schedule",
                    created_by="scheduler",
                    created_at=now,
                )
                db.add(scan)

                # Advance next run time
                sched.last_run = now
                sched.next_run = now + timedelta(hours=sched.interval_hours)
                db.commit()

                # Queue scan execution
                await scan_worker.enqueue_scan(scan_id)


scheduler_service = ScanSchedulerService()
