"""Nmap output parser for ports, services, and NSE vulnerability findings."""

import re
from typing import List, Dict, Any, Optional

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
PORT_LINE_PATTERN = re.compile(r"^(\d+)/(tcp|udp)\s+(\w+)\s+([^\s]+)(?:\s+(.*))?$")


def extract_cves(output: str) -> List[str]:
    """Extract distinct CVE IDs from text."""
    matches = CVE_PATTERN.findall(output)
    return sorted(list(set(cve.upper() for cve in matches)))


def parse_ports(output: str) -> List[Dict[str, Any]]:
    """Parse open port rows from standard Nmap output."""
    ports: List[Dict[str, Any]] = []
    in_port_section = False

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line.startswith("PORT") and "STATE" in line and "SERVICE" in line:
            in_port_section = True
            continue

        if in_port_section:
            # Stop port section when blank line or next phase section is reached
            if (
                not line
                or line.startswith("Service detection")
                or line.startswith("Nmap done")
            ):
                in_port_section = False
                continue

            # Ignore NSE script lines beginning with pipe '|' or '|_'
            if line.startswith("|") or line.startswith("|_"):
                continue

            match = PORT_LINE_PATTERN.match(line)
            if match:
                port_num = int(match.group(1))
                protocol = match.group(2).lower()
                state = match.group(3).lower()
                service = match.group(4)
                version = match.group(5).strip() if match.group(5) else ""

                ports.append(
                    {
                        "port": port_num,
                        "protocol": protocol,
                        "state": state,
                        "service": service,
                        "version": version,
                    }
                )
            else:
                parts = line.split()
                if len(parts) >= 3 and "/" in parts[0]:
                    try:
                        p_num, proto = parts[0].split("/")
                        ports.append(
                            {
                                "port": int(p_num),
                                "protocol": proto.lower(),
                                "state": parts[1].lower(),
                                "service": parts[2],
                                "version": (
                                    " ".join(parts[3:]) if len(parts) > 3 else ""
                                ),
                            }
                        )
                    except (ValueError, IndexError):
                        continue

    return ports


def parse_vulnerabilities(
    output: str, target: str, open_ports: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Parse structured vulnerability findings from Nmap NSE output."""
    findings: List[Dict[str, Any]] = []
    seen_cves: set[str] = set()

    current_port: Optional[int] = None
    current_service: Optional[str] = None
    current_version: Optional[str] = None

    lines = output.splitlines()
    i = 0
    total_lines = len(lines)

    # Build port mapping for quick lookup
    port_map = {p["port"]: p for p in open_ports}

    while i < total_lines:
        line = lines[i].strip()

        # Check if line indicates current port block
        port_match = PORT_LINE_PATTERN.match(line)
        if port_match:
            current_port = int(port_match.group(1))
            current_service = port_match.group(4)
            current_version = port_match.group(5).strip() if port_match.group(5) else ""
            i += 1
            continue

        # Look for NSE script block headers (e.g. '| http-vuln-cve2017-5638:' or '| ssl-heartbleed:')
        if line.startswith("|") and (
            "vuln" in line.lower()
            or "cve" in line.lower()
            or "ssl-" in line.lower()
            or "smb-" in line.lower()
        ):
            script_header = line.lstrip("|_ ").rstrip(":")
            evidence_lines = [line]
            block_cves: List[str] = []
            title = script_header
            description = ""
            severity = "MEDIUM"
            cvss_score = None

            # Collect script block lines
            j = i + 1
            while j < total_lines and (
                lines[j].strip().startswith("|") or lines[j].strip().startswith("|_")
            ):
                sub_line = lines[j].strip()
                evidence_lines.append(sub_line)
                clean_sub = sub_line.lstrip("|_ ")

                # Extract CVEs
                found_cves = CVE_PATTERN.findall(clean_sub)
                for c in found_cves:
                    block_cves.append(c.upper())

                # Check for explicit VULNERABLE indicator or title
                if clean_sub.startswith("VULNERABLE:"):
                    # The next line might be the title
                    if j + 1 < total_lines and lines[j + 1].strip().startswith("|"):
                        title = lines[j + 1].strip().lstrip("|_ ")

                # Check for CVSS / Risk factor
                if "risk factor:" in clean_sub.lower():
                    lower_sub = clean_sub.lower()
                    if "critical" in lower_sub:
                        severity = "CRITICAL"
                    elif "high" in lower_sub:
                        severity = "HIGH"
                    elif "medium" in lower_sub:
                        severity = "MEDIUM"
                    elif "low" in lower_sub:
                        severity = "LOW"

                cvss_match = re.search(
                    r"cvss(?:v[23])?:\s*([0-9.]+)", clean_sub, re.IGNORECASE
                )
                if cvss_match:
                    try:
                        cvss_score = float(cvss_match.group(1))
                        if cvss_score >= 9.0:
                            severity = "CRITICAL"
                        elif cvss_score >= 7.0:
                            severity = "HIGH"
                        elif cvss_score >= 4.0:
                            severity = "MEDIUM"
                        else:
                            severity = "LOW"
                    except ValueError:
                        pass

                if clean_sub.startswith("Description:"):
                    description = clean_sub.replace("Description:", "").strip()

                j += 1

            # If CVEs were found in this block, create finding entries
            if block_cves:
                for cve in set(block_cves):
                    if cve not in seen_cves:
                        seen_cves.add(cve)
                        findings.append(
                            {
                                "cve_id": cve,
                                "title": title or f"Potential vulnerability {cve}",
                                "description": description
                                or f"Potential vulnerability {cve} detected via Nmap script {script_header}",
                                "affected_host": target,
                                "affected_port": current_port,
                                "service": current_service
                                or (
                                    port_map.get(current_port, {}).get("service")
                                    if current_port
                                    else None
                                ),
                                "service_version": current_version
                                or (
                                    port_map.get(current_port, {}).get("version")
                                    if current_port
                                    else None
                                ),
                                "severity": severity,
                                "cvss_score": cvss_score,
                                "evidence": "\n".join(evidence_lines[:15]),
                                "detection_source": f"nmap-nse:{script_header}",
                            }
                        )
            i = j
            continue

        i += 1

    # Catch any additional unassociated CVEs mentioned in the output
    all_cves = extract_cves(output)
    for cve in all_cves:
        if cve not in seen_cves:
            seen_cves.add(cve)
            findings.append(
                {
                    "cve_id": cve,
                    "title": f"Potential Vulnerability {cve}",
                    "description": f"Potential vulnerability identifier {cve} detected in Nmap scan output.",
                    "affected_host": target,
                    "affected_port": current_port,
                    "service": current_service,
                    "service_version": current_version,
                    "severity": "HIGH",
                    "cvss_score": None,
                    "evidence": f"Pattern {cve} identified in raw scan output stream.",
                    "detection_source": "nmap-nse-vuln",
                }
            )

    return findings
