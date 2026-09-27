"""Pydantic schemas for Scan and Vulnerability Diff Comparison."""

from typing import List, Optional, Dict
from pydantic import BaseModel


class PortChange(BaseModel):
    port: int
    protocol: str
    service: str
    version: str


class ServiceVersionChange(BaseModel):
    port: int
    protocol: str
    service: str
    old_version: str
    new_version: str


class DiffFindingItem(BaseModel):
    cve_id: str
    title: str
    severity: str
    affected_port: Optional[int] = None
    service: Optional[str] = None


class DiffResponse(BaseModel):
    target: str
    asset_id: Optional[str] = None
    current_scan_id: Optional[str] = None
    previous_scan_id: Optional[str] = None

    # Vulnerability Changes
    new_vulnerabilities: List[DiffFindingItem] = []
    resolved_vulnerabilities: List[DiffFindingItem] = []
    persisting_vulnerabilities: List[DiffFindingItem] = []

    # Port & Service Changes
    new_ports: List[PortChange] = []
    closed_ports: List[PortChange] = []
    version_changes: List[ServiceVersionChange] = []

    # Summary Counts
    summary: Dict[str, int] = {}
