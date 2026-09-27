"""Explainable network vulnerability risk scoring engine."""

from typing import List, Dict, Any, Tuple

RISKY_SERVICES = {
    21: "FTP (plain text protocol)",
    23: "Telnet (unencrypted remote access)",
    445: "SMB (vulnerable to network worm propagation)",
    1433: "Microsoft SQL Server exposed directly",
    3306: "MySQL Database exposed directly",
    3389: "RDP Remote Desktop Protocol exposed to network",
    5432: "PostgreSQL Database exposed directly",
    6379: "Redis in-memory store exposed without proxy",
    27017: "MongoDB exposed directly",
}


def calculate_risk_score(
    open_ports: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
    asset_criticality: str = "high",
    asset_environment: str = "production",
    asset_tags: str = "",
) -> Tuple[int, List[str]]:
    """Calculate an explainable 0-100 risk score with detailed factor justifications.

    Returns:
        (score: int, reasons: List[str])
    """
    reasons: List[str] = []
    raw_score = 0.0

    # 1. Vulnerability Findings Severity Assessment
    crit_count = sum(1 for f in findings if f.get("severity") == "CRITICAL")
    high_count = sum(1 for f in findings if f.get("severity") == "HIGH")
    med_count = sum(1 for f in findings if f.get("severity") == "MEDIUM")
    low_count = sum(1 for f in findings if f.get("severity") == "LOW")

    finding_score = (
        (crit_count * 25.0)
        + (high_count * 15.0)
        + (med_count * 6.0)
        + (low_count * 2.0)
    )
    raw_score += finding_score

    if crit_count > 0:
        reasons.append(
            f"{crit_count} Critical-severity potential vulnerabilities detected (+{crit_count * 25} pts)"
        )
    if high_count > 0:
        reasons.append(
            f"{high_count} High-severity potential vulnerabilities detected (+{high_count * 15} pts)"
        )
    if med_count > 0:
        reasons.append(
            f"{med_count} Medium-severity potential vulnerabilities detected (+{med_count * 6} pts)"
        )

    # 2. Known Active Exploits (CISA KEV)
    exploited_count = sum(1 for f in findings if f.get("is_known_exploit") == "YES")
    if exploited_count > 0:
        exploit_bonus = exploited_count * 15.0
        raw_score += exploit_bonus
        reasons.append(
            f"CISA KEV Catalog Match: {exploited_count} vulnerabilities "
            f"have known active exploits (+{int(exploit_bonus)} pts)"
        )
    else:
        # Check if intelligence was checked or unknown
        has_cve = len(findings) > 0
        if has_cve:
            reasons.append(
                "CISA KEV Catalog: No active in-the-wild exploitation cataloged for detected CVEs"
            )

    # 3. High-Risk / Sensitive Network Services
    detected_risky_ports: List[str] = []
    for p in open_ports:
        port_num = p.get("port")
        if port_num in RISKY_SERVICES:
            detected_risky_ports.append(f"Port {port_num} ({RISKY_SERVICES[port_num]})")

    if detected_risky_ports:
        port_penalty = len(detected_risky_ports) * 8.0
        raw_score += port_penalty
        reasons.append(
            f"Exposed high-risk network services: {', '.join(detected_risky_ports)} (+{int(port_penalty)} pts)"
        )

    # 4. Attack Surface Volume (Open Ports Exposure)
    open_port_count = len(open_ports)
    if open_port_count > 0:
        exposure_pts = min(15.0, open_port_count * 1.5)
        raw_score += exposure_pts
        reasons.append(
            f"Exposed attack surface: {open_port_count} listening ports detected (+{int(exposure_pts)} pts)"
        )
    else:
        reasons.append("No exposed TCP listening ports detected")

    # 5. Asset Criticality Multiplier
    criticality = asset_criticality.lower()
    multiplier = 1.0
    if criticality == "critical":
        multiplier = 1.35
        reasons.append("Asset criticality weight 'Critical' (1.35x multiplier applied)")
    elif criticality == "high":
        multiplier = 1.15
        reasons.append("Asset criticality weight 'High' (1.15x multiplier applied)")
    elif criticality == "medium":
        multiplier = 1.0
        reasons.append("Asset criticality weight 'Medium' (1.0x baseline weight)")
    elif criticality == "low":
        multiplier = 0.80
        reasons.append("Asset criticality weight 'Low' (0.80x discount applied)")

    raw_score *= multiplier

    # 6. Environmental Exposure
    tags_lower = asset_tags.lower()
    is_public = (
        asset_environment.lower() == "production"
        or "public-facing" in tags_lower
        or "dmz" in tags_lower
        or "internet" in tags_lower
    )
    if is_public and open_port_count > 0:
        raw_score += 10.0
        reasons.append("Public-facing / DMZ / Production environment posture (+10 pts)")

    # 7. Clamp Final Score to [0, 100]
    final_score = int(round(max(0.0, min(100.0, raw_score))))

    # If completely clean
    if final_score == 0 and not findings:
        reasons.append(
            "Clean host posture: No vulnerabilities or exposed risky services"
        )

    return final_score, reasons
