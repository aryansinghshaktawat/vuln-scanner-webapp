"""Database engine, session management, and lifecycle initialization."""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

logger = logging.getLogger("northstar.database")

# Handle SQLite specific parameters
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables and seed initial records if empty."""
    from app.models.user import User
    from app.models.asset import Asset
    from app.models.schedule import ScanSchedule
    from app.core.security import get_password_hash
    from datetime import datetime, timezone
    import uuid

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

    # Seed default admin user and sample assets if database is newly initialized
    with SessionLocal() as db:
        admin = (
            db.query(User)
            .filter(User.username == settings.DEFAULT_ADMIN_USERNAME)
            .first()
        )
        if not admin:
            logger.info(
                "Seeding default admin user: %s", settings.DEFAULT_ADMIN_USERNAME
            )
            admin_user = User(
                id=str(uuid.uuid4()),
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                role="ADMIN",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()

        # Seed initial assets if none exist
        if db.query(Asset).count() == 0:
            logger.info("Seeding initial inventory assets")
            initial_assets = [
                Asset(
                    id="ast-001",
                    name="Core Gateway & DMZ",
                    target="10.24.18.0/24",
                    description="Corporate perimeter subnet hosting internal gateways and proxy endpoints.",
                    environment="production",
                    owner="Infrastructure & NetOps",
                    criticality="high",
                    tags="dmz,gateway,production",
                    created_at=datetime.now(timezone.utc),
                    last_scanned_at=datetime.now(timezone.utc),
                    scan_status="COMPLETED",
                ),
                Asset(
                    id="ast-002",
                    name="Staging Payments API Gateway",
                    target="api.staging.northstar.io",
                    description="Staging cluster fronting PCI-DSS candidate microservices.",
                    environment="staging",
                    owner="Payments Engineering",
                    criticality="critical",
                    tags="api,public-facing,payments,pci",
                    created_at=datetime.now(timezone.utc),
                    last_scanned_at=datetime.now(timezone.utc),
                    scan_status="COMPLETED",
                ),
                Asset(
                    id="ast-003",
                    name="Identity Provider Replica",
                    target="10.24.12.44",
                    description="Read replica directory server for internal staff SSO and directory services.",
                    environment="internal",
                    owner="Identity & Access Management",
                    criticality="medium",
                    tags="sso,ldap,internal",
                    created_at=datetime.now(timezone.utc),
                    last_scanned_at=datetime.now(timezone.utc),
                    scan_status="COMPLETED",
                ),
            ]
            db.add_all(initial_assets)
            db.commit()

            # Seed sample schedules
            schedules = [
                ScanSchedule(
                    id="sch-001",
                    asset_id="ast-001",
                    profile="full",
                    cadence="Every 24 hours",
                    interval_hours=24,
                    next_run=datetime.now(timezone.utc),
                    enabled=True,
                ),
                ScanSchedule(
                    id="sch-002",
                    asset_id="ast-002",
                    profile="full",
                    cadence="Every 7 days",
                    interval_hours=168,
                    next_run=datetime.now(timezone.utc),
                    enabled=True,
                ),
            ]
            db.add_all(schedules)
            db.commit()
