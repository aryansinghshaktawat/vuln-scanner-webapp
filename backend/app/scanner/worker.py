"""Asynchronous scan execution worker and SSE live progress publisher."""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Set, Optional, Any
from app.config import settings
from app.database import SessionLocal
from app.models.scan import Scan
from app.models.asset import Asset
from app.models.finding import PortFinding, VulnerabilityFinding
from app.scanner.engine import NmapEngine
from app.scanner.parser import parse_ports, parse_vulnerabilities
from app.scanner.risk import calculate_risk_score
from app.services.intelligence import intelligence_service
from app.services.notifications import notification_service

logger = logging.getLogger("northstar.worker")


def safe_duration(started: Optional[datetime], completed: Optional[datetime]) -> float:
    """Calculate scan duration in seconds safely handling naive and aware datetimes."""
    if not started or not completed:
        return 0.0
    s = started if started.tzinfo else started.replace(tzinfo=timezone.utc)
    c = completed if completed.tzinfo else completed.replace(tzinfo=timezone.utc)
    return max(0.1, round((c - s).total_seconds(), 2))


class ScanWorker:
    """Orchestrates async background scanning jobs and real-time SSE stream events."""

    def __init__(self):
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self._semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_SCANS)
        self._worker_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        """Start the background consumer loop."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())
            logger.info("ScanWorker background loop started")

    async def enqueue_scan(self, scan_id: str) -> None:
        """Place a scan ID onto the processing queue."""
        await self._queue.put(scan_id)
        await self._broadcast_status(
            scan_id,
            {
                "status": "QUEUED",
                "progress_phase": "Queued for scan worker",
            },
        )

    def cancel_scan(self, scan_id: str) -> bool:
        """Cancel an ongoing scan job."""
        if scan_id in self._running_tasks:
            task = self._running_tasks[scan_id]
            task.cancel()
            return True
        return False

    def subscribe(self, scan_id: str) -> asyncio.Queue:
        """Subscribe to real-time status updates for a scan."""
        queue: asyncio.Queue = asyncio.Queue()
        if scan_id not in self._subscribers:
            self._subscribers[scan_id] = set()
        self._subscribers[scan_id].add(queue)
        return queue

    def unsubscribe(self, scan_id: str, queue: asyncio.Queue) -> None:
        """Remove an active subscription queue."""
        if scan_id in self._subscribers:
            self._subscribers[scan_id].discard(queue)
            if not self._subscribers[scan_id]:
                del self._subscribers[scan_id]

    async def _broadcast_status(self, scan_id: str, payload: Dict[str, Any]) -> None:
        """Deliver live state update to all SSE subscribers."""
        if scan_id in self._subscribers:
            for q in list(self._subscribers[scan_id]):
                try:
                    await q.put(payload)
                except Exception:
                    pass

    async def _process_queue(self) -> None:
        """Continuously consume scan IDs and execute them with concurrency bounds."""
        while True:
            scan_id = await self._queue.get()
            # Dispatch processing task with concurrency semaphore
            task = asyncio.create_task(self._guarded_execute(scan_id))
            self._running_tasks[scan_id] = task
            self._queue.task_done()

    async def _guarded_execute(self, scan_id: str) -> None:
        async with self._semaphore:
            try:
                await self._execute_scan(scan_id)
            except asyncio.CancelledError:
                logger.info("Scan %s cancelled", scan_id)
                self._update_scan_cancelled(scan_id)
            except Exception as e:
                logger.exception("Unexpected error in scan %s: %s", scan_id, str(e))
                self._update_scan_failed(scan_id, str(e))
            finally:
                self._running_tasks.pop(scan_id, None)

    async def _execute_scan(self, scan_id: str) -> None:
        with SessionLocal() as db:
            scan: Optional[Scan] = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                logger.error("Scan %s not found in DB", scan_id)
                return

            target = scan.target
            profile = scan.profile
            asset: Optional[Asset] = (
                db.query(Asset).filter(Asset.id == scan.asset_id).first()
                if scan.asset_id
                else None
            )

            # 1. Update status to RUNNING
            scan.status = "RUNNING"
            scan.progress_phase = "Executing host discovery and port enumeration"
            scan.started_at = datetime.now(timezone.utc)
            if asset:
                asset.scan_status = "RUNNING"
            db.commit()

        await self._broadcast_status(
            scan_id,
            {
                "status": "RUNNING",
                "progress_phase": "Executing host discovery and port enumeration",
                "started_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        # 2. Run Nmap via isolated subprocess engine
        try:
            exit_code, stdout, stderr = await NmapEngine.run_scan(target, profile)
        except TimeoutError as e:
            self._update_scan_timeout(scan_id, str(e))
            return
        except RuntimeError as e:
            self._update_scan_failed(scan_id, str(e))
            return

        with SessionLocal() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return

            asset = (
                db.query(Asset).filter(Asset.id == scan.asset_id).first()
                if scan.asset_id
                else None
            )

            # 3. Update phase: Parsing results
            scan.progress_phase = "Parsing open ports and vulnerability scripts"
            db.commit()
            await self._broadcast_status(
                scan_id,
                {
                    "status": "RUNNING",
                    "progress_phase": "Parsing open ports and vulnerability scripts",
                },
            )

            # Parse ports
            ports = parse_ports(stdout)
            for p in ports:
                port_finding = PortFinding(
                    id=str(uuid.uuid4()),
                    scan_id=scan.id,
                    asset_id=scan.asset_id,
                    port=p["port"],
                    protocol=p["protocol"],
                    state=p["state"],
                    service=p["service"],
                    version=p["version"],
                )
                db.add(port_finding)

            # Parse vulnerabilities
            vulns = parse_vulnerabilities(stdout, target, ports)
            now = datetime.now(timezone.utc)

            for v in vulns:
                # Enrich with CISA KEV intelligence
                cve_info = await intelligence_service.enrich_cve(v["cve_id"])

                # Check if asset already has this finding from a prior scan
                existing_finding = None
                if scan.asset_id:
                    existing_finding = (
                        db.query(VulnerabilityFinding)
                        .filter(
                            VulnerabilityFinding.asset_id == scan.asset_id,
                            VulnerabilityFinding.cve_id == v["cve_id"],
                        )
                        .first()
                    )

                if existing_finding:
                    existing_finding.last_seen = now
                    existing_finding.evidence = v["evidence"]
                    # If it was marked resolved, but reappeared, reset to OPEN
                    if existing_finding.status == "RESOLVED":
                        existing_finding.status = "OPEN"
                    finding_rec = existing_finding
                else:
                    finding_rec = VulnerabilityFinding(
                        id=str(uuid.uuid4()),
                        scan_id=scan.id,
                        asset_id=scan.asset_id,
                        cve_id=v["cve_id"],
                        title=v["title"],
                        description=v["description"],
                        affected_host=v["affected_host"],
                        affected_port=v["affected_port"],
                        service=v["service"],
                        service_version=v["service_version"],
                        severity=v["severity"],
                        cvss_score=v["cvss_score"],
                        is_known_exploit=cve_info.get("is_known_exploit", "UNKNOWN"),
                        evidence=v["evidence"],
                        detection_source=v["detection_source"],
                        first_seen=now,
                        last_seen=now,
                        status="OPEN",
                        recommendation=(
                            "Review service version and apply vendor security "
                            "patches or port access restrictions."
                        ),
                    )
                    db.add(finding_rec)

            # 4. Compute Explainable Risk Score
            criticality = asset.criticality if asset else "high"
            environment = asset.environment if asset else "production"
            tags = asset.tags if asset else ""
            risk_score, reasons = calculate_risk_score(
                ports, vulns, criticality, environment, tags
            )

            # 5. Finalize Scan Record
            completed_at = datetime.now(timezone.utc)
            duration = safe_duration(scan.started_at, completed_at)

            scan.status = "COMPLETED"
            scan.progress_phase = "Scan completed successfully"
            scan.completed_at = completed_at
            scan.duration_seconds = duration
            scan.risk_score = risk_score
            scan.raw_output = stdout

            if asset:
                asset.last_scanned_at = completed_at
                asset.scan_status = "COMPLETED"
                asset.current_risk_score = risk_score

            db.commit()

            # 6. Trigger Alerts if critical or high findings found
            crit_findings = [v for v in vulns if v["severity"] == "CRITICAL"]
            if crit_findings:
                await notification_service.send_alert(
                    db=db,
                    title=f"Critical Vulnerability Discovered on {target}",
                    message=(
                        f"Scan detected {len(crit_findings)} Critical vulnerabilities "
                        f"(e.g. {crit_findings[0]['cve_id']}). Immediate remediation required."
                    ),
                    severity="CRITICAL",
                    event_type="VULNERABILITY_CRITICAL",
                    target_id=target,
                )

        await self._broadcast_status(
            scan_id,
            {
                "status": "COMPLETED",
                "progress_phase": "Completed",
                "risk_score": risk_score,
                "duration_seconds": duration,
            },
        )
        logger.info(
            "Scan %s on %s completed in %.2fs with risk score %d",
            scan_id,
            target,
            duration,
            risk_score,
        )

    def _update_scan_timeout(self, scan_id: str, message: str) -> None:
        with SessionLocal() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "TIMEOUT"
                scan.progress_phase = "Scan timed out"
                scan.error_message = message
                scan.completed_at = datetime.now(timezone.utc)
                scan.duration_seconds = safe_duration(scan.started_at, scan.completed_at)
                if scan.asset_id:
                    asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
                    if asset:
                        asset.scan_status = "FAILED"
                db.commit()
        asyncio.create_task(
            self._broadcast_status(
                scan_id,
                {
                    "status": "TIMEOUT",
                    "progress_phase": "Scan timed out",
                    "error": message,
                },
            )
        )

    def _update_scan_failed(self, scan_id: str, message: str) -> None:
        with SessionLocal() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "FAILED"
                scan.progress_phase = "Scan failed"
                scan.error_message = message
                scan.completed_at = datetime.now(timezone.utc)
                scan.duration_seconds = safe_duration(scan.started_at, scan.completed_at)
                if scan.asset_id:
                    asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
                    if asset:
                        asset.scan_status = "FAILED"
                db.commit()
        asyncio.create_task(
            self._broadcast_status(
                scan_id,
                {
                    "status": "FAILED",
                    "progress_phase": "Scan failed",
                    "error": message,
                },
            )
        )

    def _update_scan_cancelled(self, scan_id: str) -> None:
        with SessionLocal() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "CANCELLED"
                scan.progress_phase = "Scan cancelled by operator"
                scan.completed_at = datetime.now(timezone.utc)
                scan.duration_seconds = safe_duration(scan.started_at, scan.completed_at)
                if scan.asset_id:
                    asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
                    if asset:
                        asset.scan_status = "CANCELLED"
                db.commit()
        asyncio.create_task(
            self._broadcast_status(
                scan_id,
                {
                    "status": "CANCELLED",
                    "progress_phase": "Cancelled",
                },
            )
        )


scan_worker = ScanWorker()
