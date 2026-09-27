"""Report export endpoints (JSON, CSV, HTML)."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.scan import Scan
from app.services.reporting import report_service

router = APIRouter(prefix="/reports", tags=["Reporting"])


@router.get("/scans/{scan_id}")
def export_scan_report(
    scan_id: str,
    format: str = Query("json", pattern="^(json|csv|html)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and export a security assessment report in JSON, CSV, or HTML format."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found")

    fmt = format.lower()
    if fmt == "csv":
        csv_content = report_service.generate_csv_report(scan)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=scan_report_{scan.target}_{scan.id[:8]}.csv"
            },
        )
    elif fmt == "html":
        html_content = report_service.generate_html_report(scan)
        return HTMLResponse(content=html_content)
    else:
        return report_service.generate_json_report(scan)
