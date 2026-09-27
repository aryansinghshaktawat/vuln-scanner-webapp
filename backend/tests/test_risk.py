"""Unit tests for the explainable risk-scoring system."""

from app.scanner.risk import calculate_risk_score


def test_clean_host_risk_score():
    score, reasons = calculate_risk_score(
        open_ports=[],
        findings=[],
        asset_criticality="low",
        asset_environment="development",
    )
    assert score == 0
    assert any("clean" in r.lower() for r in reasons)


def test_high_risk_findings():
    open_ports = [
        {"port": 80, "protocol": "tcp", "service": "http"},
        {"port": 443, "protocol": "tcp", "service": "https"},
    ]
    findings = [
        {"severity": "CRITICAL", "is_known_exploit": "YES"},
        {"severity": "HIGH", "is_known_exploit": "NO"},
    ]
    score, reasons = calculate_risk_score(
        open_ports=open_ports,
        findings=findings,
        asset_criticality="critical",
        asset_environment="production",
        asset_tags="public-facing,payments",
    )
    # Critical vuln + High vuln + CISA KEV + Critical weight + Production exposure
    assert score >= 75
    assert len(reasons) >= 4
    assert any("Critical-severity" in r for r in reasons)
    assert any("CISA KEV" in r for r in reasons)
    assert any("Critical" in r for r in reasons)


def test_risky_service_detection():
    open_ports = [
        {"port": 23, "protocol": "tcp", "service": "telnet"},
        {"port": 3389, "protocol": "tcp", "service": "ms-wbt-server"},
    ]
    score, reasons = calculate_risk_score(
        open_ports=open_ports,
        findings=[],
        asset_criticality="medium",
        asset_environment="internal",
    )
    assert score > 0
    assert any("high-risk network services" in r for r in reasons)
