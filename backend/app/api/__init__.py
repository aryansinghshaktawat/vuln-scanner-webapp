"""API router initialization and route registration."""

from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.assets import router as assets_router
from app.api.scans import router as scans_router
from app.api.findings import router as findings_router
from app.api.schedules import router as schedules_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.notifications import router as notifications_router
from app.api.audit import router as audit_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(assets_router)
api_router.include_router(scans_router)
api_router.include_router(findings_router)
api_router.include_router(schedules_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(notifications_router)
api_router.include_router(audit_router)
