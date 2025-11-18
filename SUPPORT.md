# Support

## 📚 Documentation

Check our documentation first:
- [README.md](README.md) - Quick start guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment instructions
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines

## � Issues

Found a bug or have a feature request?
- [Report a Bug](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues/new?template=feature_request.md)

## 💬 Getting Help

- Search [existing issues](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues)
- Check the FAQ below
- Create a new issue with the question template

## Frequently Asked Questions

### Installation & Setup

**Q: Nmap not found error?**
A: Install Nmap:
- macOS: `brew install nmap`
- Linux: `sudo apt-get install nmap`
- Windows: Download from [nmap.org](https://nmap.org)

**Q: Backend won't start?**
A: Check:
1. Python 3.8+ is installed
2. Virtual environment is activated
3. Dependencies are installed: `pip install -r requirements.txt`
4. Port 8000 is not in use

**Q: Frontend build errors?**
A: Try:
```bash
rm -rf node_modules .next
npm install
npm run build
```

### Docker Issues

**Q: Docker containers won't start?**
A: Try:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Q: Can't access the application?**
A: Verify:
- Containers are running: `docker-compose ps`
- Ports are exposed: 3000 (frontend), 8000 (backend)
- No firewall blocking

### Scanning Issues

**Q: Scans timeout?**
A: This is normal for some targets. The default timeouts are:
- Basic scan: 180 seconds
- Vulnerability scan: 300 seconds

You can increase timeouts in `.env` file.

**Q: Permission denied for scanning?**
A: Ensure you have permission to scan the target. Only scan networks/systems you own or have authorization to test.

**Q: No vulnerabilities found?**
A: This could mean:
- Target has no known CVEs
- Firewall is blocking scan
- Services are up-to-date
- Use full scan mode (not quick scan)

### Development Issues

**Q: How do I contribute?**
A: See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Q: Can I use this commercially?**
A: Yes! This project is MIT licensed. See [LICENSE](LICENSE).

**Q: How do I deploy to production?**
A: See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guides.

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Nmap Documentation](https://nmap.org/book/)
- [Docker Documentation](https://docs.docker.com/)

## 🙏 Thank You

Thank you for using and supporting this project! Your feedback helps make it better for everyone.

---

**Last Updated**: November 2025
