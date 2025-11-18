import subprocess
import re
import logging
import ipaddress
import socket
from typing import List, Dict, Set, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
            ["nmap", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

# -----------------------------
# NMAP SCANNING FUNCTIONS
# -----------------------------

def run_nmap_basic(target: str) -> str:
    """Runs a basic Nmap -sV scan."""
    logger.info(f"Running basic scan on target: {target}")
    try:
        result = subprocess.run(
            ["nmap", "-sV", target],
            capture_output=True,
            text=True,
            timeout=180  # Increased to 3 minutes
        )
        if result.returncode != 0:
            logger.error(f"Nmap scan failed with return code {result.returncode}: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Nmap scan failed: {result.stderr}")
        
        logger.info("Basic scan completed successfully")
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Nmap scan timed out")
        raise HTTPException(status_code=408, detail="Scan timed out after 180 seconds")
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
                ports.append({
                    "port": parts[0],
                    "state": parts[1],
                    "service": parts[2],
                    "version": " ".join(parts[3:]) if len(parts) > 3 else ""
                })
                
    return ports

def run_nmap_vuln(target: str) -> str:
    """Runs Nmap vuln scripts."""
    logger.info(f"Running vulnerability scan on target: {target}")
    try:
        result = subprocess.run(
            ["nmap", "-sV", "--script", "vuln", target],
            capture_output=True,
            text=True,
            timeout=300  # Increased to 5 minutes for vuln scans
        )
        if result.returncode != 0:
            logger.warning(f"Nmap vuln scan completed with warnings: {result.stderr}")
        
        logger.info("Vulnerability scan completed")
        return result.stdout
    except subprocess.TimeoutExpired:
        logger.error("Nmap vulnerability scan timed out")
        raise HTTPException(status_code=408, detail="Vulnerability scan timed out after 300 seconds")
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
        raise HTTPException(status_code=400, detail="Invalid target. Must be a valid IP address or domain name")
    
    # Check if nmap is installed
    if not check_nmap_installed():
        raise HTTPException(status_code=500, detail="Nmap is not installed on the system")
    
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
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the quick scan")

@app.get("/scan")
def scan_target(target: str):
    """Main API endpoint."""
    
    # Validate input
    if not target or target.strip() == "":
        raise HTTPException(status_code=400, detail="Target parameter is required")
    
    target = target.strip()
    
    # Validate target format
    if not validate_target(target):
        raise HTTPException(status_code=400, detail="Invalid target. Must be a valid IP address or domain name")
    
    # Check if nmap is installed
    if not check_nmap_installed():
        raise HTTPException(status_code=500, detail="Nmap is not installed on the system")
    
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
        raise HTTPException(status_code=500, detail="An unexpected error occurred during the scan")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)