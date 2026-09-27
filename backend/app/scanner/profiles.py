"""Scan profiles and command-line argument construction."""

from abc import ABC, abstractmethod
from typing import List, Dict
from app.config import settings


class BaseScanProfile(ABC):
    name: str
    description: str
    timeout_seconds: int

    @abstractmethod
    def build_args(self, target: str) -> List[str]:
        """Construct isolated subprocess arguments list for Nmap."""
        pass


class QuickScanProfile(BaseScanProfile):
    name = "quick"
    description = "Quick TCP Port Discovery & Service Probing (Fast, non-intrusive)"
    timeout_seconds = settings.QUICK_SCAN_TIMEOUT

    def build_args(self, target: str) -> List[str]:
        return [
            settings.NMAP_BINARY,
            "-sT",
            "-Pn",
            "-T4",
            "--top-ports",
            "1000",
            "-oN",
            "-",
            target,
        ]


class FullScanProfile(BaseScanProfile):
    name = "full"
    description = "Comprehensive Vulnerability Assessment (TCP + Service Versions + NSE Vulnerability Scripts)"
    timeout_seconds = settings.DEEP_SCAN_TIMEOUT

    def build_args(self, target: str) -> List[str]:
        return [
            settings.NMAP_BINARY,
            "-sT",
            "-sV",
            "-Pn",
            "-T4",
            "--script",
            "vuln",
            "--script-timeout",
            "120s",
            "-oN",
            "-",
            target,
        ]


class PortOnlyProfile(BaseScanProfile):
    name = "port_only"
    description = "Fast Top 100 Port Discovery"
    timeout_seconds = settings.QUICK_SCAN_TIMEOUT

    def build_args(self, target: str) -> List[str]:
        return [
            settings.NMAP_BINARY,
            "-sT",
            "-Pn",
            "-F",
            "-oN",
            "-",
            target,
        ]


class VulnOnlyProfile(BaseScanProfile):
    name = "vuln_only"
    description = "Targeted Vulnerability Audit with Version Detection"
    timeout_seconds = settings.DEEP_SCAN_TIMEOUT

    def build_args(self, target: str) -> List[str]:
        return [
            settings.NMAP_BINARY,
            "-sT",
            "-sV",
            "-Pn",
            "-T3",
            "--script",
            "vuln",
            "--script-timeout",
            "120s",
            "-oN",
            "-",
            target,
        ]


PROFILES: Dict[str, BaseScanProfile] = {
    "quick": QuickScanProfile(),
    "full": FullScanProfile(),
    "port_only": PortOnlyProfile(),
    "vuln_only": VulnOnlyProfile(),
}


def get_profile(name: str) -> BaseScanProfile:
    """Retrieve profile by key, defaulting to quick profile."""
    return PROFILES.get(name.lower(), PROFILES["quick"])
