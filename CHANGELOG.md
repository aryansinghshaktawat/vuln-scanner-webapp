# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-09-27

### Added
- **Asset Inventory System**: CRUD operations for managing IP addresses, hostnames, and subnets with criticality (Critical, High, Medium, Low), environment tiers, ownership, and tags.
- **Persistent Database Layer**: Full SQLAlchemy models for Users, Assets, Scans, PortFindings, VulnerabilityFindings, ScanSchedules, AuditEvents, and Notifications. Supports SQLite and PostgreSQL.
- **Asynchronous Background Scanner & SSE**: Non-blocking background worker queue (`ScanWorker`) with concurrency controls (`MAX_CONCURRENT_SCANS=3`) and Server-Sent Events (`/api/scans/{id}/stream`) for real-time phase updates.
- **Explainable Risk Scoring Engine**: Deterministic 0–100 risk scoring algorithm factoring asset criticality, network exposure, CVSS metrics, open sensitive ports, and CISA KEV data with human-readable justification reasons.
- **Vulnerability Diff Engine**: Snapshot comparator identifying NEW, RESOLVED, and PERSISTING vulnerabilities, as well as port and service version changes between consecutive scans.
- **Vulnerability Remediation Tracking**: Finding lifecycle management (`OPEN`, `ACKNOWLEDGED`, `IN_PROGRESS`, `RESOLVED`, `FALSE_POSITIVE`) with automated "Verify Fix" re-scanning workflows.
- **Scheduled Automated Scanning**: Recurring scan scheduler powered by APScheduler supporting customizable intervals and automatic job queuing.
- **Multi-Format Report Generator**: Export scan assessments in structured JSON, CSV finding spreadsheets, and print-ready executive HTML reports.
- **Target Safety & SSRF Safeguards**: Mandatory validation preventing shell command injection, blocking cloud metadata addresses (`169.254.169.254`), and enforcing CIDR boundaries (max /24).
- **Security Operations Console UI**: Next.js 16 operator console featuring interactive dashboards, asset profiles, live scan terminals, diff viewers, and settings.
- **Automated Test Suite**: 22 unit and integration tests covering SSRF validation, Nmap parsing, risk scoring, diff algorithms, and REST APIs.

### Changed
- Refactored backend into clean modular packages (`app.api`, `app.scanner`, `app.models`, `app.services`, `app.core`).
- Upgraded Next.js frontend to Next.js 16 App Router with strict TypeScript interfaces.
- Enhanced Docker Compose with persistent database volume and modernized Dockerfiles.
- Updated GitHub Actions CI to install Nmap, run Pytest, and validate builds on Node 20.
- Preserved all legacy endpoints (`/scan/quick`, `/scan`, `/health`) for 100% backward compatibility.

## [1.0.0] - 2025-11-18

### Added
- Initial release of Vulnerability Scanner Web Application
- FastAPI backend with Nmap integration
- Next.js 14 frontend with TypeScript
- Automated port scanning functionality
- CVE vulnerability detection
- Real-time scanning with progress indicators
- Responsive UI with Tailwind CSS
- Quick scan mode (ports only)
- Full scan mode (ports + vulnerabilities)
- Input validation and error handling
- CORS middleware configuration
- Comprehensive logging system
- API documentation with FastAPI auto-docs

### Features
- **Port Scanning**: Discover open ports and running services
- **Service Detection**: Identify service versions
- **CVE Detection**: Extract and display CVE vulnerabilities
- **Modern UI**: Clean, responsive interface
- **Error Handling**: User-friendly error messages
- **Cross-platform**: Support for macOS, Linux, and Windows

### Backend
- FastAPI application with Uvicorn server
- Nmap integration using subprocess
- Input validation for IP addresses and domains
- Timeout handling for long scans
- Regex-based CVE extraction
- Structured error responses
- Health check endpoint

### Frontend
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS styling
- Loading states and animations
- Scan timer display
- CVE links to MITRE database
- Mobile-responsive design
- Two-button scan interface (quick/full)

### Security
- Input validation and sanitization
- Subprocess command safety
- Timeout protection
- Error message sanitization
- CORS configuration

## [0.1.0] - 2025-11-10

### Added
- Initial project structure
- Basic backend skeleton
- Basic frontend skeleton
- Project documentation

---

## Version History

- **v1.0.0** - Production-ready release with full features
- **v0.1.0** - Initial development version

---

**Note:** For detailed information about each change, see the [commit history](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/commits/main).
