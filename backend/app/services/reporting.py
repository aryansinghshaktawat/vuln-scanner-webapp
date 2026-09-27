"""Security scan report generation service (JSON, CSV, and printable HTML)."""

import csv
import io
import html
from datetime import datetime, timezone
from typing import Dict, Any
from app.models.scan import Scan


class ReportService:
    """Generates structured vulnerability assessment reports."""

    @staticmethod
    def generate_json_report(scan: Scan) -> Dict[str, Any]:
        """Produce full JSON report payload."""
        asset_info = None
        if scan.asset:
            asset_info = {
                "id": scan.asset.id,
                "name": scan.asset.name,
                "environment": scan.asset.environment,
                "criticality": scan.asset.criticality,
                "owner": scan.asset.owner,
            }

        return {
            "report_metadata": {
                "report_id": f"REP-{scan.id[:8]}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "scan_id": scan.id,
                "target": scan.target,
                "scan_profile": scan.profile,
                "status": scan.status,
                "duration_seconds": scan.duration_seconds,
                "overall_risk_score": scan.risk_score,
            },
            "asset": asset_info,
            "summary": {
                "open_ports_count": len(scan.ports),
                "total_vulnerabilities": len(scan.findings),
                "critical_count": sum(
                    1 for f in scan.findings if f.severity == "CRITICAL"
                ),
                "high_count": sum(1 for f in scan.findings if f.severity == "HIGH"),
                "medium_count": sum(1 for f in scan.findings if f.severity == "MEDIUM"),
                "low_count": sum(1 for f in scan.findings if f.severity == "LOW"),
            },
            "open_ports": [
                {
                    "port": p.port,
                    "protocol": p.protocol,
                    "state": p.state,
                    "service": p.service,
                    "version": p.version,
                }
                for p in scan.ports
            ],
            "findings": [
                {
                    "cve_id": f.cve_id,
                    "title": f.title,
                    "severity": f.severity,
                    "cvss_score": f.cvss_score,
                    "is_known_exploit": f.is_known_exploit,
                    "affected_port": f.affected_port,
                    "service": f.service,
                    "status": f.status,
                    "recommendation": f.recommendation,
                    "remediation_owner": f.remediation_owner,
                    "remediation_notes": f.remediation_notes,
                }
                for f in scan.findings
            ],
        }

    @staticmethod
    def generate_csv_report(scan: Scan) -> str:
        """Produce structured CSV report export."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow(
            [
                "Scan ID",
                "Target",
                "Scan Date",
                "Port",
                "Protocol",
                "Service",
                "Service Version",
                "CVE ID",
                "Title",
                "Severity",
                "CVSS",
                "CISA KEV Exploit",
                "Status",
                "Remediation Owner",
                "Recommendation",
            ]
        )

        scan_date = (
            scan.completed_at.isoformat()
            if scan.completed_at
            else (scan.created_at.isoformat() if scan.created_at else "")
        )

        if scan.findings:
            for f in scan.findings:
                writer.writerow(
                    [
                        scan.id,
                        scan.target,
                        scan_date,
                        f.affected_port or "",
                        "tcp",
                        f.service or "",
                        f.service_version or "",
                        f.cve_id,
                        f.title,
                        f.severity,
                        f.cvss_score or "N/A",
                        f.is_known_exploit,
                        f.status,
                        f.remediation_owner or "Unassigned",
                        f.recommendation or "",
                    ]
                )
        else:
            for p in scan.ports:
                writer.writerow(
                    [
                        scan.id,
                        scan.target,
                        scan_date,
                        p.port,
                        p.protocol,
                        p.service,
                        p.version,
                        "N/A",
                        "No vulnerability detected",
                        "INFO",
                        "N/A",
                        "NO",
                        "OPEN",
                        "N/A",
                        "N/A",
                    ]
                )

        return output.getvalue()

    @staticmethod
    def generate_html_report(scan: Scan) -> str:
        """Generate human-readable, printable security assessment report."""
        target = html.escape(scan.target)
        asset_name = (
            html.escape(scan.asset.name) if scan.asset else "Unregistered Asset"
        )
        date_str = (
            scan.completed_at.strftime("%B %d, %Y at %H:%M UTC")
            if scan.completed_at
            else datetime.now(timezone.utc).strftime("%B %d, %Y")
        )

        crit_count = sum(1 for f in scan.findings if f.severity == "CRITICAL")
        high_count = sum(1 for f in scan.findings if f.severity == "HIGH")
        med_count = sum(1 for f in scan.findings if f.severity == "MEDIUM")
        low_count = sum(1 for f in scan.findings if f.severity == "LOW")

        port_rows = ""
        for p in scan.ports:
            port_rows += f"""
            <tr>
                <td style="font-family: monospace; font-weight: 600;">{p.port}/{p.protocol}</td>
                <td><span class="badge badge-success">{html.escape(p.state)}</span></td>
                <td>{html.escape(p.service)}</td>
                <td style="color: #666;">{html.escape(p.version or '-')}</td>
            </tr>
            """

        finding_rows = ""
        for f in scan.findings:
            sev_class = (
                "badge-crit"
                if f.severity == "CRITICAL"
                else ("badge-high" if f.severity == "HIGH" else "badge-med")
            )
            cisa_badge = (
                '<span class="badge badge-cisa">KEV EXPLOIT</span>'
                if f.is_known_exploit == "YES"
                else ""
            )
            finding_rows += f"""
            <div class="finding-card">
                <div class="finding-header">
                    <span class="badge {sev_class}">{f.severity}</span>
                    <strong style="font-family: monospace; margin-left: 8px;">{html.escape(f.cve_id)}</strong>
                    {cisa_badge}
                    <span style="margin-left: auto; font-size: 12px; color: #888;">Status: <b>{f.status}</b></span>
                </div>
                <h4 style="margin: 8px 0 4px 0;">{html.escape(f.title)}</h4>
                <p style="margin: 0 0 8px 0; color: #555; font-size: 13px;">{html.escape(f.description or 'Potential vulnerability detected by Nmap NSE script.')}</p>
                <div style="font-size: 12px; color: #777; background: #f8fafc; padding: 8px; border-radius: 4px;">
                    <div><b>Affected Port:</b> {f.affected_port or 'Host service'} ({html.escape(f.service or 'unknown')})</div>
                    <div><b>Recommendation:</b> {html.escape(f.recommendation or 'Apply latest security patches and restrict network perimeter access.')}</div>
                </div>
            </div>
            """

        if not finding_rows:
            finding_rows = "<p style='color: #2e7d32; font-weight: 500;'>No potential vulnerabilities were identified during this assessment.</p>"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Security Assessment Report - {target}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #1e293b; margin: 0; padding: 32px; background: #f8fafc; line-height: 1.5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        header {{ border-bottom: 2px solid #e2e8f0; padding-bottom: 24px; margin-bottom: 32px; display: flex; justify-content: space-between; align-items: flex-start; }}
        h1 {{ margin: 0; font-size: 26px; color: #0f172a; }}
        .meta {{ color: #64748b; font-size: 13px; margin-top: 6px; }}
        .score-box {{ text-align: right; }}
        .score-circle {{ display: inline-block; padding: 12px 20px; border-radius: 8px; background: #fee2e2; color: #dc2626; font-size: 28px; font-weight: bold; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
        .card {{ background: #f1f5f9; padding: 16px; border-radius: 6px; text-align: center; }}
        .card strong {{ display: block; font-size: 24px; color: #0f172a; margin-top: 4px; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }}
        .badge-crit {{ background: #fee2e2; color: #b91c1c; }}
        .badge-high {{ background: #ffedd5; color: #c2410c; }}
        .badge-med {{ background: #e0f2fe; color: #0369a1; }}
        .badge-success {{ background: #dcfce7; color: #15803d; }}
        .badge-cisa {{ background: #fae8ff; color: #86198f; margin-left: 6px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; margin-bottom: 32px; font-size: 13px; }}
        th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f8fafc; color: #475569; font-weight: 600; font-size: 12px; }}
        .finding-card {{ border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin-bottom: 16px; }}
        .finding-header {{ display: flex; align-items: center; margin-bottom: 8px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center; }}
        @media print {{ body {{ background: #fff; padding: 0; }} .container {{ box-shadow: none; padding: 0; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Vulnerability Assessment Report</h1>
                <div class="meta">
                    <b>Target:</b> {target} &bull; <b>Asset:</b> {asset_name} &bull; <b>Generated:</b> {date_str}
                </div>
            </div>
            <div class="score-box">
                <div class="score-circle">{scan.risk_score} / 100</div>
                <div style="font-size: 11px; color: #64748b; margin-top: 4px; font-weight: 600;">RISK SCORE</div>
            </div>
        </header>

        <section class="summary-grid">
            <div class="card"><span>Open Ports</span><strong>{len(scan.ports)}</strong></div>
            <div class="card"><span>Critical CVEs</span><strong style="color: #b91c1c;">{crit_count}</strong></div>
            <div class="card"><span>High CVEs</span><strong style="color: #c2410c;">{high_count}</strong></div>
            <div class="card"><span>Medium & Low</span><strong style="color: #0369a1;">{med_count + low_count}</strong></div>
        </section>

        <h3>Discovered Network Ports & Services</h3>
        <table>
            <thead>
                <tr>
                    <th>Port / Protocol</th>
                    <th>State</th>
                    <th>Service</th>
                    <th>Version Fingerprint</th>
                </tr>
            </thead>
            <tbody>
                {port_rows}
            </tbody>
        </table>

        <h3>Potential Vulnerabilities Identified</h3>
        {finding_rows}

        <div class="footer">
            Generated by Northstar Security Platform &bull; Nmap Scanning Engine &bull; Defensive Security Audit Record
        </div>
    </div>
</body>
</html>
"""


report_service = ReportService()
