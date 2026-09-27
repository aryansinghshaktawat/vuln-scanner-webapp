"""Application configuration module."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Northstar Vulnerability Management Platform"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"

    # Server & Environment
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Persistence
    DATABASE_URL: str = "sqlite:///./vuln_scanner.db"

    # Security & Auth
    SECRET_KEY: str = "northstar-secret-key-change-in-production-super-safe-32b"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    AUTH_REQUIRED: bool = (
        False  # Set to True to enforce JWT auth on all API endpoints; False allows transparent operator demo mode
    )

    # Pre-seeded Admin Credentials
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "Admin123!"
    DEFAULT_ADMIN_EMAIL: str = "admin@northstar.local"

    # CORS
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://frontend:3000"
    )

    # Scanner Configuration
    NMAP_BINARY: str = "nmap"
    QUICK_SCAN_TIMEOUT: int = 180
    DEEP_SCAN_TIMEOUT: int = 600
    MAX_TARGETS_PER_SCAN: int = 256
    MAX_CONCURRENT_SCANS: int = 3
    ALLOW_LOOPBACK_SCAN: bool = True  # Allows localhost/127.0.0.1 for local testing

    # Vulnerability Intelligence Feeds
    CISA_KEV_FEED_URL: str = (
        "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    )
    NVD_API_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    INTELLIGENCE_CACHE_HOURS: int = 24

    # Notifications & Alerting
    ALERT_WEBHOOK_URL: str | None = None
    ALERT_MIN_SEVERITY: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


settings = Settings()
