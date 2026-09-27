"""Vulnerability intelligence enrichment service (CISA KEV & NVD caching)."""

import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any
import httpx
from app.config import settings

logger = logging.getLogger("northstar.intelligence")


class VulnerabilityIntelligenceService:
    """Provides cached threat intelligence for detected CVEs."""

    def __init__(self):
        self._cisa_kev_cache: Dict[str, Dict[str, Any]] = {}
        self._cisa_last_fetched: float = 0.0
        self._cve_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl_seconds = settings.INTELLIGENCE_CACHE_HOURS * 3600

    async def refresh_cisa_kev(self, force: bool = False) -> None:
        """Download CISA Known Exploited Vulnerabilities (KEV) catalog with caching."""
        now = time.time()
        if (
            not force
            and self._cisa_kev_cache
            and (now - self._cisa_last_fetched < self._cache_ttl_seconds)
        ):
            return

        try:
            logger.info("Fetching CISA KEV catalog feed...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(settings.CISA_KEV_FEED_URL)
                if resp.status_code == 200:
                    data = resp.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    new_cache: Dict[str, Dict[str, Any]] = {}
                    for item in vulnerabilities:
                        cve_id = item.get("cveID", "").upper()
                        if cve_id:
                            new_cache[cve_id] = {
                                "vendorProject": item.get("vendorProject"),
                                "product": item.get("product"),
                                "vulnerabilityName": item.get("vulnerabilityName"),
                                "dateAdded": item.get("dateAdded"),
                                "shortDescription": item.get("shortDescription"),
                                "requiredAction": item.get("requiredAction"),
                            }
                    self._cisa_kev_cache = new_cache
                    self._cisa_last_fetched = now
                    logger.info(
                        "Loaded %d CVEs from CISA KEV catalog",
                        len(self._cisa_kev_cache),
                    )
                else:
                    logger.warning("CISA KEV feed returned HTTP %s", resp.status_code)
        except Exception as e:
            logger.warning(
                "Could not reach CISA KEV feed (%s). Continuing with existing cache.",
                str(e),
            )

    async def enrich_cve(self, cve_id: str) -> Dict[str, Any]:
        """Enrich a detected CVE with CISA KEV and public vulnerability metadata."""
        clean_cve = cve_id.upper().strip()

        # Check local cache
        if clean_cve in self._cve_cache:
            return self._cve_cache[clean_cve]

        # Ensure KEV cache is populated if possible
        if not self._cisa_kev_cache:
            await self.refresh_cisa_kev()

        is_known_exploit = "NO"
        evidence_note = ""
        cisa_item = self._cisa_kev_cache.get(clean_cve)

        if cisa_item:
            is_known_exploit = "YES"
            vuln_name = cisa_item.get("vulnerabilityName", "")
            action = cisa_item.get("requiredAction", "")
            evidence_note = f"CISA KEV Match: {vuln_name}. Action required: {action}"

        enriched = {
            "cve_id": clean_cve,
            "is_known_exploit": is_known_exploit,
            "enrichment_source": (
                "CISA KEV Catalog" if cisa_item else "Nmap NSE Signature Database"
            ),
            "enrichment_timestamp": datetime.now(timezone.utc).isoformat(),
            "exploit_notes": evidence_note,
        }

        self._cve_cache[clean_cve] = enriched
        return enriched


intelligence_service = VulnerabilityIntelligenceService()
