# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Docker support with Dockerfile for both backend and frontend
- Docker Compose configuration for easy deployment
- Environment configuration with .env.example files
- Comprehensive deployment guide (DEPLOYMENT.md)
- Contributing guidelines (CONTRIBUTING.md)
- Security policy (SECURITY.md)
- CI/CD workflows with GitHub Actions
- License file (MIT License)

### Changed
- Updated Next.js configuration for standalone output
- Enhanced requirements.txt with additional dependencies
- Improved README with Docker deployment instructions

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
