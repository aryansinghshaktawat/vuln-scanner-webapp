# Vulnerability Scanner Web Application

A modern, full-stack web application for automated network vulnerability scanning using Nmap. Built with Next.js 14 frontend and FastAPI backend.

![Vulnerability Scanner](https://img.shields.io/badge/Status-Production%20Ready-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)

## 🚀 Features

- **Automated Port Scanning**: Discovers open ports and running services
- **Vulnerability Detection**: Identifies CVE vulnerabilities using Nmap's vulnerability scripts
- **Modern UI**: Clean, responsive interface built with Tailwind CSS
- **Real-time Results**: Live scanning with progress indicators
- **CVE Integration**: Direct links to MITRE CVE database for vulnerability details
- **Cross-platform**: Works on macOS, Linux, and Windows (with Nmap installed)
- **Error Handling**: Comprehensive validation and user-friendly error messages

## 🏗️ Architecture

```
vuln-scanner-webapp/
├── backend/           # FastAPI Python backend
│   ├── main.py       # Core application with Nmap integration
│   └── __pycache__/
├── frontend/         # Next.js 14 React frontend
│   ├── app/
│   │   ├── page.tsx  # Main scanning interface
│   │   └── layout.tsx
│   ├── package.json
│   └── ...
└── README.md
```

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **React** with hooks for state management

### Backend
- **FastAPI** for high-performance API
- **Python 3.8+** runtime
- **Uvicorn** ASGI server
- **Nmap** for network scanning
- **Subprocess** for secure command execution

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or later) or **Bun** runtime
- **Python** (3.8 or later)
- **Nmap** network scanner

### Installing Nmap

**macOS:**
```bash
brew install nmap
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install nmap
```

**Windows:**
Download and install from [nmap.org](https://nmap.org/download.html)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/aryansinghshaktawat/vuln-scanner-webapp.git
cd vuln-scanner-webapp
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn

# Start the backend server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# or with bun:
# bun install

# Start the frontend development server
npm run dev
# or with bun:
# bun dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## 🎯 Usage

1. **Open the web application** at http://localhost:3000
2. **Enter a target** (domain name or IP address) in the input field
   - Example: `scanme.nmap.org`, `127.0.0.1`, `google.com`
3. **Click "Start Scan"** or press Enter
4. **Wait for results** (typically 30-120 seconds depending on target)
5. **View the results**:
   - Open ports table with service information
   - CVE vulnerabilities with links to MITRE database

### Example Scan Targets

- `scanme.nmap.org` - Official Nmap test server
- `127.0.0.1` - Your local machine
- `httpbin.org` - HTTP testing service

## 🔧 API Endpoints

### GET `/`
Returns backend status
```json
{"message": "Backend is working!"}
```

### GET `/scan?target=<target>`
Performs vulnerability scan on the specified target

**Parameters:**
- `target` (string): Domain name or IP address to scan

**Response:**
```json
{
  "target": "scanme.nmap.org",
  "open_ports": [
    {
      "port": "80/tcp",
      "state": "open",
      "service": "http",
      "version": "Apache httpd 2.4.7"
    }
  ],
  "cves": ["CVE-2021-34527", "CVE-2021-1675"]
}
```

**Error Responses:**
- `400` - Invalid target format
- `408` - Scan timeout
- `500` - Nmap not installed or scan failed

## 🔒 Security Considerations

- **Input Validation**: All targets are validated before scanning
- **Command Injection Protection**: Subprocess calls are properly sanitized
- **Timeout Limits**: Scans are limited to prevent hanging
- **Error Handling**: Sensitive error details are not exposed to users
- **CORS Configuration**: Proper cross-origin request handling

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Test API endpoints
curl "http://127.0.0.1:8000/"
curl "http://127.0.0.1:8000/scan?target=127.0.0.1"
```

### Frontend Testing
1. Open http://localhost:3000
2. Test with various targets (valid domains, IPs, invalid inputs)
3. Verify responsive design on mobile and desktop
4. Test error states (invalid targets, backend offline)

## 🚨 Troubleshooting

### Common Issues

**"Nmap not installed" Error**
```bash
# Check if nmap is installed
which nmap
nmap --version

# Install if missing (macOS)
brew install nmap
```

**Backend Connection Failed**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify CORS configuration

**Scan Timeouts**
- Some targets may take longer to scan
- Increase timeout values in backend code if needed
- Check network connectivity to target

**Permission Denied**
```bash
# Some nmap scans require sudo (especially SYN scans)
# The application uses TCP connect scans which don't require privileges
```

## 📁 Project Structure

```
vuln-scanner-webapp/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── .venv/              # Python virtual environment
│   └── __pycache__/        # Python cache
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # Main scan interface
│   │   ├── layout.tsx      # App layout
│   │   └── globals.css     # Global styles
│   ├── public/             # Static assets
│   ├── package.json        # Dependencies
│   ├── tsconfig.json       # TypeScript config
│   └── tailwind.config.js  # Tailwind CSS config
├── README.md
└── TaskList                # Development task list
```

## 🔮 Future Enhancements

- [ ] **Scan History**: Store and manage previous scan results
- [ ] **Export Reports**: Download results as PDF/JSON
- [ ] **Advanced Scanning**: OS detection, stealth scans
- [ ] **User Authentication**: Multi-user support
- [ ] **Database Integration**: Persistent data storage
- [ ] **API Rate Limiting**: Prevent abuse
- [ ] **Docker Deployment**: Containerized deployment
- [ ] **Scheduling**: Automated periodic scans

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Legal Disclaimer

This tool is for educational and authorized security testing purposes only. Users must:

- Only scan networks and systems they own or have explicit permission to test
- Comply with all applicable laws and regulations
- Respect rate limits and target system resources
- Use responsibly and ethically

The developers are not responsible for any misuse of this software.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Aryan Singh Shaktawat**
- GitHub: [@aryansinghshaktawat](https://github.com/aryansinghshaktawat)

## 🙏 Acknowledgments

- [Nmap](https://nmap.org/) - The Network Mapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

---

⭐ **Star this repository** if you found it helpful!
