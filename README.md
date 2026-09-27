<div align="center">

# 🛡️ Northstar Vulnerability Management Platform

### Defensive Network Security, Asset Perimeter & Vulnerability Lifecycle Platform

An end-to-end, portfolio-ready defensive cybersecurity platform transforming standard Nmap network audits into continuous asset inventory, explainable risk scoring, scan history diffs, vulnerability lifecycle tracking, scheduled scans, and multi-format reporting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16_App_Router-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![Nmap](https://img.shields.io/badge/Scanner-Nmap_7.9+-00599C.svg)](https://nmap.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](docker-compose.yml)
[![CI/CD](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg)](.github/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-22%2F22_Passing-brightgreen.svg)](backend/tests/)

[Platform Overview](#-platform-overview) • [Console Walkthrough](#-console-walkthrough) • [Architecture](#-architecture) • [Security Controls](#-security-controls--authorized-use-policy) • [Quick Start](#-quick-start) • [Risk Scoring Model](#-explainable-risk-scoring-model) • [Vulnerability Diff](#-vulnerability-diff-engine) • [API Reference](#-api-reference)

---

</div>

## ⚠️ Defensive Security & Authorized Use Policy

> **CRITICAL LEGAL NOTICE**: This application is built strictly as a defensive security auditing and vulnerability management tool for authorized perimeters. Users must scan **only** IP addresses, hostnames, and subnets that they personally own or have received formal, written authorization to assess.
>
> Probing or scanning unauthorized networks without consent violates the United States Computer Fraud and Abuse Act (CFAA), the UK Computer Misuse Act, and international telecommunications statutes.
>
> The platform includes mandatory server-side protections: SSRF cloud metadata filtering (`169.254.169.254`), loopback restrictions, CIDR range limits (maximum /24, 256 hosts), and audit event logging for all initiated operations.

---

## 🧭 Platform Overview

**Northstar Vulnerability Management Platform** is engineered to provide defensive security engineers and SecOps teams with continuous visibility into their external and internal attack surfaces. Rather than treating port scanning as a one-off CLI action, Northstar wraps the trusted **Nmap** engine with an enterprise-grade operational management plane:

1. **Asset Inventory**: Register and categorize servers, web endpoints, database instances, and network appliances with owner metadata, environment tiers, and business criticality ratings.
2. **Scan Orchestration & Isolated Workers**: Asynchronous execution via dedicated background worker queues and concurrency semaphores, preventing HTTP request blocking and command-line injection.
3. **Real-Time Scan Telemetry**: Server-Sent Events (SSE) broadcast live scan stages (`Host Discovery`, `Port Scanning`, `Service Probing`, `NSE Vulnerability Scripts`) without artificial progress simulation.
4. **Persistent Historical Records**: Full scan audit trails stored in SQLAlchemy models (SQLite local fallback, PostgreSQL for production deployments).
5. **Vulnerability Diff Engine**: Instant comparison between the current scan and the prior scan for the same asset, pinpointing `NEW`, `RESOLVED`, and `PERSISTING` vulnerabilities, as well as port state and service version changes.
6. **Explainable Risk Scoring**: Deterministic 0–100 risk calculation based on asset criticality, internet exposure, CVSS metrics, open sensitive ports, and CISA Known Exploited Vulnerabilities (KEV) data—accompanied by human-readable justification reasons.
7. **Remediation & "Verify Fix" Workflow**: Finding lifecycle tracking (`OPEN`, `ACKNOWLEDGED`, `IN_PROGRESS`, `RESOLVED`, `FALSE_POSITIVE`) with automated re-scan verification routines.
8. **Automated Scanning Schedules**: Durable cron-style recurring background scans powered by APScheduler.
9. **Multi-Format Export Reporting**: Automated generation of technical JSON payloads, CSV finding sheets, and human-readable executive HTML reports ready for printing/PDF conversion.

---

## 🖥️ Console Walkthrough

The platform features a Next.js 16 Security Operations Console designed for incident triage and vulnerability lifecycle tracking:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  🛡️ NORTHSTAR VULNERABILITY PLATFORM            Active Perimeter | SecOps Analyst (Tier 1)│
├──────────────┬─────────────────────────────────────────────────────────────────────────┤
│ [Dashboard]  │  PERIMETER OVERVIEW                                                     │
│ [Assets]     │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│ [Scans]      │  │ Assets: 8    │  │ Scanned: 6   │  │ Open Vulns:14│  │ Critical: 2  │ │
│ [Vulns]      │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│ [Schedules]  │                                                                         │
│ [Reports]    │  POSTURE METRICS                  EXPLAINABLE RISK GAUGE                │
│ [Settings]   │  • High Risk: 5                   Score: 78 / 100 [HIGH RISK]           │
│              │  • Medium Risk: 7                 - Critical asset (Tier 1 core)        │
│              │  • New Vulns (24h): 3             - Internet-facing production host     │
│              │  • Resolved: 4                    - High-severity finding (CVE-2023)    │
│              │                                                                         │
│              │  RECENT SCANS & DIFFS                                                   │
│              │  • 192.168.1.100 [Production API]  COMPLETED  14.2s  Diff: 1 New, 1 Res │
│              │  • dev-bastion.internal            COMPLETED   4.8s  Diff: 0 New, 0 Res │
└──────────────┴─────────────────────────────────────────────────────────────────────────┘
```

- **`/dashboard`** — Perimeter health metrics, severity distributions, risk gauge, and quick-launcher.
- **`/assets`** — Asset inventory table with filtering by environment (Production, Staging, Dev, Internal) and criticality (Critical, High, Medium, Low).
- **`/assets/[id]`** — Detailed asset security posture, detected open ports, active findings, scan history, and drift diff.
- **`/scans`** — Live scan management dashboard with real-time status indicators and abort/cancel actions.
- **`/scans/[id]`** — Real-time SSE progress monitor, open ports list, CVE findings, and side-by-side diff viewer.
- **`/vulnerabilities`** — Centralized remediation center with status filters, owner assignment, due dates, notes, and *"Verify Fix"* automation.
- **`/vulnerabilities/[id]`** — Individual finding dossier with CVSS scores, raw NSE evidence, and remediation tracking.
- **`/schedules`** — Automated recurring scanning configuration with APScheduler.
- **`/reports`** — Multi-format reporting export center (JSON technical export, CSV spreadsheet, and printable HTML executive summary).
- **`/settings`** — Target safety policy, legal notices, scanner engine health diagnostics, and environment configuration.

---

## 🏗️ Architecture

```
                       ┌────────────────────────────────────────────────────────┐
                       │               Next.js 16 Security Console              │
                       │   Dashboard • Inventory • Findings • Reports • Audit   │
                       └──────────────────────────┬─────────────────────────────┘
                                                  │ REST / SSE
                                                  ▼
                       ┌────────────────────────────────────────────────────────┐
                       │                      FastAPI API                       │
                       │   Router • Auth/RBAC • Target Validator • Rate Limiter │
                       └─────────────┬────────────────────────────┬─────────────┘
                                     │                            │
             ┌───────────────────────▼─────────┐        ┌─────────▼─────────────┐
             │       Job Worker & Queue        │        │   Database / Models   │
             │   APScheduler Recurring Jobs    │        │  SQLAlchemy (SQLite / │
             │   Concurrency Limiter (max 3)   │        │      PostgreSQL)      │
             └───────────────┬─────────────────┘        └───────────────────────┘
                             │ Subprocess Array (shell=False)
                             ▼
             ┌─────────────────────────────────┐        ┌───────────────────────┐
             │           Nmap Engine           │        │ Security Intelligence │
             │  TCP SYN • Service Probing •    │◄───────┤    CISA KEV Cache     │
             │  NSE Scripts (vulners/vulscan)  │        │     (Rate-Limited)    │
             └─────────────────────────────────┘        └───────────────────────┘
```

### Component Breakdown

- **Web Operator Console (`frontend/`)**: Modern security console built on Next.js 16 (App Router), TypeScript, and custom CSS design tokens. Optimized for rapid incident triage with dark mode visual hierarchy, severity pills, risk meters, and diff sidebars.
- **REST & SSE API Layer (`backend/app/api/`)**: FastAPI application providing structured endpoints with Pydantic v2 validation, JWT authentication, and Server-Sent Event streams (`/api/scans/{id}/stream`).
- **Target Safety Validator (`backend/app/scanner/validator.py`)**: Sanitizes inputs, prevents shell injection, enforces CIDR limits (max /24), blocks AWS/GCP/Azure cloud metadata (`169.254.169.254`), and prevents loopback scanning unless explicitly enabled.
- **Nmap Subprocess Engine (`backend/app/scanner/engine.py`)**: Executes Nmap directly using safe subprocess argument lists (`shell=False`), captures stdout/stderr, and enforces execution timeouts.
- **Parser & Intelligence Feed (`backend/app/scanner/parser.py`, `backend/app/services/intelligence.py`)**: Parses Nmap text output into open ports, services, versions, and potential CVEs. Correlates CVEs against cached CISA Known Exploited Vulnerabilities (KEV) data.
- **Risk Calculator (`backend/app/scanner/risk.py`)**: Applies an explainable scoring rubric that factors in asset business criticality, network exposure, discovered port risks, and vulnerability severity.
- **Diff Engine (`backend/app/scanner/diff.py`)**: Compares successive scan snapshots on the same asset to detect changes in open ports, service versions, and vulnerability presence.
- **Persistence Layer (`backend/app/database.py`)**: Relational database schema with SQLAlchemy ORM. Automatically defaults to SQLite for local development and supports PostgreSQL via `DATABASE_URL`.

---

## 📁 Repository Structure

```
vuln-scanner-webapp/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI (Nmap, Pytest, Linters, Next.js Build)
├── backend/
│   ├── app/
│   │   ├── api/                 # REST & SSE routers
│   │   │   ├── assets.py        # Asset CRUD & posture endpoints
│   │   │   ├── audit.py         # Audit event queries
│   │   │   ├── auth.py          # JWT authentication & RBAC
│   │   │   ├── dashboard.py     # Aggregated security metrics
│   │   │   ├── findings.py      # Vulnerability tracking & "Verify Fix"
│   │   │   ├── notifications.py # Alerting and notifications
│   │   │   ├── reports.py       # JSON, CSV, and HTML report endpoints
│   │   │   ├── scans.py         # Scan dispatcher, cancellation, and SSE streams
│   │   │   └── schedules.py     # Recurring scan schedule CRUD
│   │   ├── core/                # Password hashing, JWT tokens, RBAC dependencies
│   │   ├── models/              # SQLAlchemy ORM models (Asset, Scan, Finding, User, etc.)
│   │   ├── scanner/             # Safe Nmap engine, profiles, parser, diff, validator, worker
│   │   ├── schemas/             # Pydantic v2 schemas for all entities
│   │   ├── services/            # CISA KEV intelligence, notifications, reports, APScheduler
│   │   ├── config.py            # Pydantic Settings & environment variables
│   │   └── database.py          # Database session & default seeding
│   ├── tests/                   # 22 Unit & integration tests (pytest)
│   ├── Dockerfile               # Production-ready Python + Nmap image
│   ├── requirements.txt         # Backend Python dependencies
│   └── main.py                  # FastAPI application entrypoint & legacy endpoints
├── frontend/
│   ├── app/
│   │   ├── assets/              # Asset inventory & asset detail pages
│   │   ├── components/          # Sidebar, Topbar, Badges, DiffViewer, RiskGauge, Modals
│   │   ├── lib/                 # Typed API client & data interfaces
│   │   ├── reports/             # Multi-format report export center
│   │   ├── scans/               # Scan history table & live SSE scan page
│   │   ├── schedules/           # Recurring schedule management page
│   │   ├── settings/            # Target safety policy & governance page
│   │   ├── vulnerabilities/     # Remediation tracker & finding detail page
│   │   ├── globals.css          # Design system tokens and styles
│   │   └── page.tsx             # Overview security dashboard
│   ├── Dockerfile               # Node 20 alpine multi-stage build
│   └── package.json             # Next.js 16 dependencies
├── docker-compose.yml           # Multi-container orchestration with persistent storage
├── CHANGELOG.md                 # Semantic versioning release history
└── README.md                    # Platform documentation
```

---

## 🔒 Security Controls & Scanner Safeguards

| Threat Vector | Mitigation Strategy | Implementation |
| :--- | :--- | :--- |
| **Command Injection** | No shell invocation; raw string interpolation prohibited | `subprocess.Popen(cmd_list, shell=False)` in `engine.py` |
| **Server-Side Request Forgery (SSRF)** | Cloud metadata and restricted subnets blocked | IP & DNS check in `validator.py` blocks `169.254.169.254` |
| **Denial of Service (Oversized Scan)** | Bounded IP address targets per execution | Maximum `/24` (256 IP addresses) enforced in `validator.py` |
| **Hanging Scan Processes** | Per-profile watchdog timers | Enforced timeouts (180s Quick, 600s Full) with process kill |
| **Scan Overload** | Concurrency control | Background semaphore limiting simultaneous scans (`MAX_CONCURRENT_SCANS=3`) |
| **Unauthorized Action Tracking** | Tamper-evident activity recording | Audit events logged on asset creation, scan trigger, and remediation update |
| **Data Integrity / Precision** | Clear terminology separation | Tagged as *"potential vulnerability detected by Nmap NSE"* |

---

## 🚀 Quick Start

### Default Development Credentials
- **Username**: `admin`
- **Password**: `Admin123!`
- **Role**: `admin` (full permissions)

---

### Option A: Local Development Setup

#### Prerequisites
- **Python**: 3.10+ installed
- **Node.js**: 20+ installed
- **Nmap**: Installed and available in `$PATH`
  - macOS: `brew install nmap`
  - Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y nmap`
  - Fedora: `sudo dnf install nmap`

#### 1. Start the Backend API & Worker
```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# Run database setup and launch FastAPI server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend automatically seeds an initial administrator account (`admin` / `Admin123!`), sample monitored assets, and starts the background scan scheduler.*

#### 2. Start the Frontend Console
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

### Option B: Docker Compose Deployment

Run the complete platform (frontend, backend, database, and Nmap) using Docker Compose:

```bash
# Clone and enter directory
git clone https://github.com/aryansinghshaktawat/vuln-scanner-webapp.git
cd vuln-scanner-webapp

# Build and start services
docker-compose up --build
```

- **Frontend Console**: [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Persistent Data**: Preserved in Docker volume `backend-storage`

---

## 📊 Explainable Risk Scoring Model

Northstar calculates an asset risk score between **0 and 100** based exclusively on verifiable technical and contextual factors. The score is transparently justified with specific reasons:

$$\text{Final Risk Score} = \min(100, \, \text{Base Severity} + \text{Criticality Bonus} + \text{Exposure Bonus} + \text{Exploitation Bonus})$$

### Scoring Rubric Breakdown:

1. **Vulnerability Severity Weight**:
   - `CRITICAL` finding (CVSS $\ge$ 9.0): **+40 points**
   - `HIGH` finding (CVSS 7.0–8.9): **+25 points**
   - `MEDIUM` finding (CVSS 4.0–6.9): **+15 points**
   - `LOW` finding (CVSS 0.1–3.9): **+5 points**
2. **Asset Criticality Multiplier**:
   - `Critical` (Tier 1 core infrastructure): **+20 points**
   - `High` (Tier 2 business operations): **+15 points**
   - `Medium` (Tier 3 internal services): **+8 points**
   - `Low` (Tier 4 non-critical test bench): **+2 points**
3. **Network Exposure Level**:
   - `Production` environment: **+15 points**
   - `Staging`: **+8 points**
   - `Development` / `Internal`: **+3 points**
4. **Threat Intelligence Correlation**:
   - CVE listed in CISA KEV (Known Exploited Vulnerabilities catalog): **+15 points**
5. **High-Risk Exposed Services**:
   - Insecure remote management (Telnet port 23, cleartext FTP port 21, RDP port 3389): **+10 points**

*If external vulnerability intelligence is unavailable for a CVE, the platform explicitly notes the missing data rather than synthesizing scores.*

---

## 🔄 Vulnerability Diff Engine

The diff engine analyzes successive scans for any asset to track perimeter drift:

- 🆕 **NEW Vulnerabilities**: Findings identified in the latest scan that were not present previously.
- ✅ **RESOLVED Vulnerabilities**: Findings present in the prior scan that are no longer detected (verified remediations).
- 🔁 **PERSISTING Vulnerabilities**: Outstanding findings identified across both scans.
- 🔌 **NEW / CLOSED Ports**: Ports that opened or closed between scan runs.
- 🏷️ **SERVICE VERSION Changes**: Version updates (e.g., `nginx 1.14.0` $\rightarrow$ `nginx 1.24.0`).

---

## 🎯 Scan Profiles

| Profile Name | Flag Configuration | Target Scope | Timeout | Intended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Quick Scan (`quick`)** | `-sT -F --top-ports 100 -T4 --open` | Top 100 common TCP ports | 180s | Rapid availability and perimeter triage |
| **Full Assessment (`full`)** | `-sV -sC --script=vulners,vulscan -T3` | Top 1000 ports + Version + NSE Vuln Scripts | 600s | Deep vulnerability and compliance audit |
| **Port Discovery (`port_only`)** | `-sT -p 1-1024 -T4` | Privileged ports (1–1024) | 180s | Discovery of listening system services |
| **Vulnerability Scripts (`vuln_only`)** | `--script=vulners -sV` | Running service vulnerability interrogation | 300s | Targeted vulnerability correlation |

---

## 🛡️ Vulnerability Lifecycle & Remediation

Each vulnerability finding tracks its resolution state:

```
    ┌──────────┐
    │   OPEN   │ ◄─── Discovered during scan
    └────┬─────┘
         │
         ▼
  ┌──────────────┐
  │ ACKNOWLEDGED │ ◄─── Assigned to owner with triage note
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ IN_PROGRESS  │ ◄─── Patching or compensating control applied
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   RESOLVED   │ ◄─── Closed manually or confirmed by automated "Verify Fix" scan
  └──────────────┘
```

- **Verify Fix**: Clicking *"Verify Fix"* initiates a targeted Nmap scan on the affected host and port. If the vulnerability is no longer identified, its status is updated to `RESOLVED` and recorded in the audit log.

---

## 📡 API Reference

Interactive OpenAPI documentation is automatically served at **`/docs`** or **`/redoc`**.

### Core Endpoints

#### Asset Management
- `GET /api/assets` — List registered assets (supports search, environment, and criticality filtering).
- `POST /api/assets` — Register an authorized asset.
- `GET /api/assets/{id}` — Fetch asset metadata and posture overview.
- `DELETE /api/assets/{id}` — Delete an asset and associated records.
- `GET /api/assets/{id}/scans` — Scan history for a specific asset.
- `GET /api/assets/{id}/diff` — Vulnerability diff between the asset's last two scans.

#### Scan Orchestration
- `GET /api/scans` — List scan jobs with status, duration, and findings summary.
- `POST /api/scans` — Dispatch an asynchronous scan (`asset_id`, `target`, `profile`).
- `GET /api/scans/{id}` — Fetch detailed scan results (ports, findings, raw output).
- `POST /api/scans/{id}/cancel` — Abort a running or queued scan job.
- `GET /api/scans/{id}/stream` — Server-Sent Events (SSE) live progress stream.
- `GET /api/scans/{id}/diff` — Scan-level diff against the preceding scan.

#### Vulnerability Tracking & Remediation
- `GET /api/vulnerabilities` — Query vulnerability findings (severity, status, and CVE filters).
- `GET /api/vulnerabilities/{id}` — Detailed finding view including evidence and remediation notes.
- `PUT /api/vulnerabilities/{id}` — Update remediation status, assigned owner, or due date.
- `POST /api/vulnerabilities/{id}/verify` — Launch an automated re-scan to verify remediation.

#### Recurring Schedules & Automation
- `GET /api/schedules` — List automated scan schedules.
- `POST /api/schedules` — Configure recurring scan job (`asset_id`, `profile`, `interval_hours`).
- `PUT /api/schedules/{id}` — Enable or disable an automated schedule.
- `DELETE /api/schedules/{id}` — Remove a recurring schedule.

#### Reporting & Dashboards
- `GET /api/dashboard` — Platform overview metrics (total assets, open vulns, severity distribution).
- `GET /api/reports/{scan_id}?format=json` — Export structured JSON report.
- `GET /api/reports/{scan_id}?format=csv` — Export CSV spreadsheet of findings.
- `GET /api/reports/{scan_id}?format=html` — Download printable HTML audit report.

#### Backward Compatibility Endpoints
- `POST /scan/quick` — Legacy quick port scan endpoint.
- `POST /scan` — Legacy full scan endpoint.
- `GET /health` — Diagnostic health check (API, Nmap, Database).

---

## 🧪 Testing & Code Quality

The repository maintains automated unit, integration, and linting test suites.

### Run Backend Tests (Pytest)
```bash
cd backend
source env/bin/activate
pytest -v
```
*Executes all 22 unit tests covering target validation, SSRF defenses, Nmap output parsing, risk calculations, diff engines, and API endpoints.*

### Run Backend Linters
```bash
cd backend
black --check main.py
flake8 main.py --max-line-length=100
```

### Run Frontend Linting & Build Validation
```bash
cd frontend
npm run lint
npm run build
```

---

## ⚙️ Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./vuln_scanner.db` | SQLAlchemy connection URI (supports PostgreSQL) |
| `JWT_SECRET` | *(Random development secret)* | Cryptographic key for JWT session validation |
| `MAX_CONCURRENT_SCANS` | `3` | Maximum number of concurrent background Nmap processes |
| `QUICK_SCAN_TIMEOUT_SEC` | `180` | Subprocess timeout for quick scans |
| `FULL_SCAN_TIMEOUT_SEC` | `600` | Subprocess timeout for full vulnerability scans |
| `CORS_ORIGINS` | `http://localhost:3000` | Permitted origins for Cross-Origin Resource Sharing |
| `NMAP_BINARY` | `nmap` | Path or name of the Nmap executable |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Public backend endpoint URL consumed by browser client |

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><strong>Why does Northstar default to TCP Connect (-sT) rather than SYN Stealth (-sS)?</strong></summary>
<p>
SYN stealth scans (-sS) require raw socket capabilities provided only by root/administrator privileges. Using TCP Connect (-sT) allows the platform and workers to execute safely in unprivileged environments, standard containers, and multi-tenant cloud hosts without running containers as root.
</p>
</details>

<details>
<summary><strong>How are long-running scans prevented from blocking the API?</strong></summary>
<p>
FastAPI accepts the scan request, writes a <code>QUEUED</code> record to the database, and delegates execution to a non-blocking asynchronous <code>ScanWorker</code>. The worker streams real-time state changes via Server-Sent Events (SSE) while the API responds immediately with the newly registered scan record.
</p>
</details>

<details>
<summary><strong>Can I integrate PostgreSQL instead of SQLite?</strong></summary>
<p>
Yes. Set the <code>DATABASE_URL</code> environment variable to your PostgreSQL connection string (e.g. <code>postgresql://user:password@localhost:5432/northstar</code>). SQLAlchemy automatically handles engine creation and connection pooling.
</p>
</details>

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
