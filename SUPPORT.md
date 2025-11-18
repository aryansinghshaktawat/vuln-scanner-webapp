# Support

## Getting Help

Thank you for using the Vulnerability Scanner Web Application! If you need help, here are your options:

## 📚 Documentation

Before asking for help, please check our documentation:

- **[README.md](README.md)** - Quick start and overview
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines
- **[SECURITY.md](SECURITY.md)** - Security policy
- **[FAQ](#frequently-asked-questions)** - Common questions

## 💬 Community Support

### GitHub Discussions
For questions, ideas, and general discussions:
- [Start a Discussion](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/discussions)
- Search existing discussions first
- Be clear and provide context

### GitHub Issues
For bug reports and feature requests:
- [Report a Bug](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues/new?template=feature_request.md)
- [Documentation Issue](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues/new?template=documentation.md)
- [Ask a Question](https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues/new?template=question.md)

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description** - Clear description of the issue
2. **Steps to reproduce** - Detailed steps
3. **Expected behavior** - What should happen
4. **Actual behavior** - What actually happens
5. **Environment** - OS, browser, versions
6. **Screenshots** - If applicable
7. **Logs** - Any error messages

## ✨ Requesting Features

When requesting features, please include:

1. **Problem statement** - What problem does this solve?
2. **Proposed solution** - Your suggested approach
3. **Alternatives** - Other solutions considered
4. **Use case** - How would you use this feature?
5. **Impact** - Who benefits from this?

## 🔒 Security Issues

**DO NOT** report security vulnerabilities through public GitHub issues!

Please report security issues privately:
- Email: [INSERT SECURITY EMAIL]
- See [SECURITY.md](SECURITY.md) for details

## 📧 Direct Contact

For other inquiries:
- Email: [INSERT CONTACT EMAIL]
- GitHub: [@aryansinghshaktawat](https://github.com/aryansinghshaktawat)

## ⏱️ Response Time

- **Bug reports**: 2-3 business days
- **Feature requests**: 5-7 business days  
- **Security issues**: 24-48 hours
- **General questions**: 3-5 business days

Please note: This is an open-source project maintained by volunteers. Response times may vary.

## 🤝 How to Help

Want to help others? Here's how:

1. **Answer questions** in Discussions and Issues
2. **Improve documentation** with pull requests
3. **Share your experience** in Discussions
4. **Report bugs** you encounter
5. **Contribute code** to fix issues

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
