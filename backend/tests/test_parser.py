"""Unit tests for Nmap output parser (ports & NSE vulnerabilities)."""

from app.scanner.parser import parse_ports, parse_vulnerabilities, extract_cves

SAMPLE_NMAP_OUTPUT = """
Starting Nmap 7.94 ( https://nmap.org ) at 2026-09-26 12:00 UTC
Nmap scan report for test-target.local (192.168.1.50)
Host is up (0.0010s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.6
80/tcp   open  http    Apache httpd 2.4.52 ((Ubuntu))
| http-vuln-cve2017-5638:
|   VULNERABLE:
|   Apache Struts 2 Remote Code Execution Vulnerability
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-5638
|     Risk factor: High  CVSSv2: 10.0
|     Description:
|       Apache Struts 2 2.3.5 through 2.3.31 allows remote attackers to execute arbitrary code.
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-5638
|_      https://nvd.nist.gov/vuln/detail/CVE-2017-5638
443/tcp  open  ssl/http Apache httpd 2.4.52
| ssl-heartbleed:
|   VULNERABLE:
|   The Heartbleed Bug
|     State: VULNERABLE
|     Risk factor: High
|     Description:
|       OpenSSL 1.0.1 through 1.0.1f is vulnerable to memory disclosure.
|     References:
|       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-0160
|_      http://www.heartbleed.com
3306/tcp open  mysql   MySQL 8.0.35

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 12.34 seconds
"""


def test_parse_ports():
    ports = parse_ports(SAMPLE_NMAP_OUTPUT)
    assert len(ports) == 4

    port_22 = next(p for p in ports if p["port"] == 22)
    assert port_22["protocol"] == "tcp"
    assert port_22["state"] == "open"
    assert port_22["service"] == "ssh"
    assert "OpenSSH 8.9p1" in port_22["version"]

    port_80 = next(p for p in ports if p["port"] == 80)
    assert port_80["service"] == "http"
    assert "Apache httpd 2.4.52" in port_80["version"]

    port_3306 = next(p for p in ports if p["port"] == 3306)
    assert port_3306["service"] == "mysql"


def test_extract_cves():
    cves = extract_cves(SAMPLE_NMAP_OUTPUT)
    assert "CVE-2017-5638" in cves
    assert "CVE-2014-0160" in cves


def test_parse_vulnerabilities():
    ports = parse_ports(SAMPLE_NMAP_OUTPUT)
    findings = parse_vulnerabilities(SAMPLE_NMAP_OUTPUT, "test-target.local", ports)
    assert len(findings) >= 2

    struts_finding = next((f for f in findings if f["cve_id"] == "CVE-2017-5638"), None)
    assert struts_finding is not None
    assert struts_finding["severity"] in ["CRITICAL", "HIGH"]
    assert struts_finding["affected_port"] == 80

    heartbleed_finding = next(
        (f for f in findings if f["cve_id"] == "CVE-2014-0160"), None
    )
    assert heartbleed_finding is not None
    assert heartbleed_finding["affected_port"] == 443
