"""Scan diff engine: comparing vulnerabilities, ports, and service changes across scans."""

from typing import Optional
from app.models.scan import Scan
from app.schemas.diff import (
    DiffResponse,
    DiffFindingItem,
    PortChange,
    ServiceVersionChange,
)


def compute_scan_diff(
    current_scan: Optional[Scan], previous_scan: Optional[Scan]
) -> DiffResponse:
    """Compare a current scan against a previous scan for the same asset/target.

    Identifies:
    - NEW vulnerabilities (in current scan, not in previous)
    - RESOLVED vulnerabilities (in previous scan, not in current)
    - PERSISTING vulnerabilities (present in both)
    - NEW ports (open now, were not open before)
    - CLOSED ports (were open before, closed now)
    - SERVICE VERSION changes (same port open in both, but service or version changed)
    """
    target = (
        current_scan.target
        if current_scan
        else (previous_scan.target if previous_scan else "")
    )
    asset_id = (
        current_scan.asset_id
        if current_scan
        else (previous_scan.asset_id if previous_scan else None)
    )

    diff = DiffResponse(
        target=target,
        asset_id=asset_id,
        current_scan_id=current_scan.id if current_scan else None,
        previous_scan_id=previous_scan.id if previous_scan else None,
        new_vulnerabilities=[],
        resolved_vulnerabilities=[],
        persisting_vulnerabilities=[],
        new_ports=[],
        closed_ports=[],
        version_changes=[],
        summary={},
    )

    if not current_scan or not previous_scan:
        # If there is no previous scan, all current findings are considered new
        if current_scan:
            for f in current_scan.findings:
                diff.new_vulnerabilities.append(
                    DiffFindingItem(
                        cve_id=f.cve_id,
                        title=f.title,
                        severity=f.severity,
                        affected_port=f.affected_port,
                        service=f.service,
                    )
                )
            for p in current_scan.ports:
                diff.new_ports.append(
                    PortChange(
                        port=p.port,
                        protocol=p.protocol,
                        service=p.service,
                        version=p.version or "",
                    )
                )
        diff.summary = {
            "new_vulnerabilities": len(diff.new_vulnerabilities),
            "resolved_vulnerabilities": 0,
            "persisting_vulnerabilities": 0,
            "new_ports": len(diff.new_ports),
            "closed_ports": 0,
            "version_changes": 0,
        }
        return diff

    # 1. Map CVEs for both scans
    curr_cves = {f.cve_id: f for f in current_scan.findings}
    prev_cves = {f.cve_id: f for f in previous_scan.findings}

    # NEW: in current, not in previous
    for cve_id, f in curr_cves.items():
        if cve_id not in prev_cves:
            diff.new_vulnerabilities.append(
                DiffFindingItem(
                    cve_id=f.cve_id,
                    title=f.title,
                    severity=f.severity,
                    affected_port=f.affected_port,
                    service=f.service,
                )
            )

    # RESOLVED: in previous, not in current
    for cve_id, f in prev_cves.items():
        if cve_id not in curr_cves:
            diff.resolved_vulnerabilities.append(
                DiffFindingItem(
                    cve_id=f.cve_id,
                    title=f.title,
                    severity=f.severity,
                    affected_port=f.affected_port,
                    service=f.service,
                )
            )

    # PERSISTING: in both
    for cve_id, f in curr_cves.items():
        if cve_id in prev_cves:
            diff.persisting_vulnerabilities.append(
                DiffFindingItem(
                    cve_id=f.cve_id,
                    title=f.title,
                    severity=f.severity,
                    affected_port=f.affected_port,
                    service=f.service,
                )
            )

    # 2. Map Ports for both scans
    curr_ports = {(p.port, p.protocol): p for p in current_scan.ports}
    prev_ports = {(p.port, p.protocol): p for p in previous_scan.ports}

    # NEW ports
    for (port_num, proto), p in curr_ports.items():
        if (port_num, proto) not in prev_ports:
            diff.new_ports.append(
                PortChange(
                    port=p.port,
                    protocol=p.protocol,
                    service=p.service,
                    version=p.version or "",
                )
            )

    # CLOSED ports
    for (port_num, proto), p in prev_ports.items():
        if (port_num, proto) not in curr_ports:
            diff.closed_ports.append(
                PortChange(
                    port=p.port,
                    protocol=p.protocol,
                    service=p.service,
                    version=p.version or "",
                )
            )

    # VERSION changes on persisting open ports
    for (port_num, proto), curr_p in curr_ports.items():
        if (port_num, proto) in prev_ports:
            prev_p = prev_ports[(port_num, proto)]
            if (curr_p.version != prev_p.version) or (curr_p.service != prev_p.service):
                diff.version_changes.append(
                    ServiceVersionChange(
                        port=port_num,
                        protocol=proto,
                        service=curr_p.service,
                        old_version=prev_p.version or "(none)",
                        new_version=curr_p.version or "(none)",
                    )
                )

    diff.summary = {
        "new_vulnerabilities": len(diff.new_vulnerabilities),
        "resolved_vulnerabilities": len(diff.resolved_vulnerabilities),
        "persisting_vulnerabilities": len(diff.persisting_vulnerabilities),
        "new_ports": len(diff.new_ports),
        "closed_ports": len(diff.closed_ports),
        "version_changes": len(diff.version_changes),
    }

    return diff
