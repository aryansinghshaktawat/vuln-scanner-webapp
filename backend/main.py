import subprocess
import re
import logging
import ipaddress
import socket
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# VALIDATION FUNCTIONS
# -----------------------------


def validate_target(target: str) -> bool:
    """Validates if target is a valid IP address or domain name."""
    try:
        # Try to parse as IP address
        ipaddress.ip_address(target)
        return True
    except ValueError:
        # Try to resolve as domain name
        try:
            socket.gethostbyname(target)
            return True
        except socket.gaierror:
            return False


def check_nmap_installed() -> bool:
    """Checks if nmap is installed on the system."""
    try:
        result = subprocess.run(
            ["nmap", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# -----------------------------
# NMAP SCANNING FUNCTIONS
# -----------------------------


def run_nmap_basic(target: str) -> str:
    """Runs a basic Nmap scan with TCP connect."""
    logger.info(f"Running basic scan on target: {target}")
    try:
        # Use -sT (TCP connect) which doesn't require root privileges
        # Use -sV for version detection (may require sudo on some systems)
        # Use -T4 for faster scanning (aggressive timing)
        # Use -Pn to skip ping and assume host is up
        result = subprocess.run(
            ["nmap", "-sT", "-sV", "-T4", "-Pn", target],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for basic scan
        )
        if result.returncode != 0:
            logger.error(
                f"Nmap scan failed with return code {result.returncode}: {result.stderr}"
            )
            # If scan failed, try without -sV (version detection)
            logger.info("Retrying scan without version detection...")
            result = subprocess.run(
                ["nmap", "-sT", "-T4", "-Pn", target],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                raise HTTPException(
                    status_code=500, detail=f"Nmap scan failed: {result.stderr}"
                )

        logger.info("Basic scan completed successfully")
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Nmap scan timed out")
        raise HTTPException(
            status_code=408,
            detail="Scan timed out after 5 minutes. Target may be unresponsive.",
        )
    except FileNotFoundError:
        logger.error("Nmap not found on system")
        raise HTTPException(status_code=500, detail="Nmap not installed on system")


def parse_ports(nmap_output: str) -> List[Dict]:
    """Extracts open ports + service info."""
    ports = []
    in_section = False

    for line in nmap_output.splitlines():
        line = line.strip()

        if line.startswith("PORT"):
            in_section = True
            continue

        if in_section and (line == "" or "Service detection" in line):
            in_section = False

        if in_section:
            parts = line.split()
            if len(parts) >= 3:
                ports.append(
                    {
                        "port": parts[0],
                        "state": parts[1],
                        "service": parts[2],
                        "version": " ".join(parts[3:]) if len(parts) > 3 else "",
                    }
                )

    return ports


def run_nmap_vuln(target: str) -> str:
    """Runs Nmap vuln scripts."""
    logger.info(f"Running vulnerability scan on target: {target}")
    try:
        # Use more efficient scan options:
        # -sT: TCP connect scan (doesn't require root)
        # -sV: Service version detection
        # -T4: Faster timing template
        # -Pn: Skip ping, assume host is up
        # --script=vuln: Only vulnerability scripts
        # --script-timeout=120s: Timeout individual scripts at 2 minutes
        result = subprocess.run(
            [
                "nmap",
                "-sT",
                "-sV",
                "-T4",
                "-Pn",
                "--script",
                "vuln",
                "--script-timeout",
                "120s",
                target,
            ],
            capture_output=True,
            text=True,
            timeout=600,  # Increased to 10 minutes for vuln scans
        )
        if result.returncode != 0:
            logger.warning(f"Nmap vuln scan completed with warnings: {result.stderr}")
            # Try without -sV if it failed
            logger.info("Retrying vulnerability scan without version detection...")
            result = subprocess.run(
                [
                    "nmap",
                    "-sT",
                    "-T4",
                    "-Pn",
                    "--script",
                    "vuln",
                    "--script-timeout",
                    "120s",
                    target,
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

        logger.info("Vulnerability scan completed")
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Nmap vulnerability scan timed out")
        raise HTTPException(
            status_code=408,
            detail=(
                "Vulnerability scan timed out after 10 minutes. "
                "Try using Quick Scan mode for faster results."
            ),
        )
    except FileNotFoundError:
        logger.error("Nmap not found on system")
        raise HTTPException(status_code=500, detail="Nmap not installed on system")


def extract_cves(nmap_output: str) -> List[str]:
    """Extracts CVE numbers using regex."""
    found = re.findall(r"CVE-\d{4}-\d+", nmap_output)
    return list(sorted(set(found)))


# -----------------------------
# FASTAPI ROUTES
# -----------------------------


@app.get("/")
def root():
    return {"message": "Backend is working!"}


@app.get("/scan/quick")
def quick_scan_target(target: str):
    """Quick scan endpoint - ports only, no vulnerabilities."""

    # Validate input
    if not target or target.strip() == "":
        raise HTTPException(status_code=400, detail="Target parameter is required")

    target = target.strip()

    # Validate target format
    if not validate_target(target):
        raise HTTPException(
            status_code=400,
            detail="Invalid target. Must be a valid IP address or domain name",
        )

    # Check if nmap is installed
    if not check_nmap_installed():
        raise HTTPException(
            status_code=500, detail="Nmap is not installed on the system"
        )

    try:
        basic_output = run_nmap_basic(target)
        ports = parse_ports(basic_output)

        return {
            "target": target,
            "open_ports": ports,
            "cves": [],  # No CVE scan for quick mode
        }
    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during quick scan: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred during the quick scan"
        )


@app.get("/scan")
def scan_target(target: str):
    """Main API endpoint."""

    # Validate input
    if not target or target.strip() == "":
        raise HTTPException(status_code=400, detail="Target parameter is required")

    target = target.strip()

    # Validate target format
    if not validate_target(target):
        raise HTTPException(
            status_code=400,
            detail="Invalid target. Must be a valid IP address or domain name",
        )

    # Check if nmap is installed
    if not check_nmap_installed():
        raise HTTPException(
            status_code=500, detail="Nmap is not installed on the system"
        )

    try:
        basic_output = run_nmap_basic(target)
        ports = parse_ports(basic_output)

        vuln_output = run_nmap_vuln(target)
        cves = extract_cves(vuln_output)

        return {
            "target": target,
            "open_ports": ports,
            "cves": cves,
        }
    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during scan: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred during the scan"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
