"""Unit tests for the vulnerability and port scan diff engine."""

from types import SimpleNamespace
from app.scanner.diff import compute_scan_diff


def make_mock_scan(id: str, target: str, cves: list, ports: list):
    findings = [
        SimpleNamespace(
            cve_id=cve,
            title=f"Title for {cve}",
            severity="HIGH",
            affected_port=80,
            service="http",
        )
        for cve in cves
    ]
    port_objs = [
        SimpleNamespace(port=p[0], protocol="tcp", service=p[1], version=p[2])
        for p in ports
    ]
    return SimpleNamespace(
        id=id,
        target=target,
        asset_id="ast-1",
        findings=findings,
        ports=port_objs,
    )


def test_vulnerability_diff():
    # Previous scan has CVE-2024-1234, CVE-2024-5678, Port 22 OpenSSH 8.2, Port 80 Apache 2.4.41
    prev = make_mock_scan(
        "scan-1",
        "10.24.18.5",
        cves=["CVE-2024-1234", "CVE-2024-5678"],
        ports=[
            (22, "ssh", "OpenSSH 8.2"),
            (80, "http", "Apache 2.4.41"),
            (3306, "mysql", "MySQL 8.0"),
        ],
    )

    # Current scan has CVE-2024-5678 (persisting), CVE-2025-1111 (new). CVE-2024-1234 resolved!
    # Port 3306 is closed now, Port 443 is new, Port 80 upgraded to Apache 2.4.52!
    curr = make_mock_scan(
        "scan-2",
        "10.24.18.5",
        cves=["CVE-2024-5678", "CVE-2025-1111"],
        ports=[
            (22, "ssh", "OpenSSH 8.2"),
            (80, "http", "Apache 2.4.52"),
            (443, "https", "Apache 2.4.52"),
        ],
    )

    diff = compute_scan_diff(curr, prev)

    # Verify Vulnerability Diffs
    new_cves = [v.cve_id for v in diff.new_vulnerabilities]
    resolved_cves = [v.cve_id for v in diff.resolved_vulnerabilities]
    persisting_cves = [v.cve_id for v in diff.persisting_vulnerabilities]

    assert new_cves == ["CVE-2025-1111"]
    assert resolved_cves == ["CVE-2024-1234"]
    assert persisting_cves == ["CVE-2024-5678"]

    # Verify Port Diffs
    new_ports = [p.port for p in diff.new_ports]
    closed_ports = [p.port for p in diff.closed_ports]
    assert new_ports == [443]
    assert closed_ports == [3306]

    # Verify Service Version Change
    assert len(diff.version_changes) == 1
    assert diff.version_changes[0].port == 80
    assert diff.version_changes[0].old_version == "Apache 2.4.41"
    assert diff.version_changes[0].new_version == "Apache 2.4.52"
