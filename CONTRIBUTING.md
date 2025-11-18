# Contributing to Vulnerability Scanner Web Application

Thank you for considering contributing to the Vulnerability Scanner Web Application! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

---

## Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

### Unacceptable Behavior
- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites
Before contributing, ensure you have:
- Git installed
- Python 3.8+ installed
- Node.js 18+ or Bun installed
- Nmap installed
- Basic understanding of FastAPI and Next.js

### Fork and Clone
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/vuln-scanner-webapp.git
cd vuln-scanner-webapp

# Add upstream remote
git remote add upstream https://github.com/aryansinghshaktawat/vuln-scanner-webapp.git
```

---

## Development Setup

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run development server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# or with bun:
bun install

# Copy environment file
cp .env.example .env.local

# Run development server
npm run dev
# or with bun:
bun dev
```

### Running Tests
```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

---

## How to Contribute

### Types of Contributions

1. **Bug Fixes**
   - Fix reported issues
   - Improve error handling
   - Fix security vulnerabilities

2. **New Features**
   - Implement features from the roadmap
   - Add new scanning capabilities
   - Improve UI/UX

3. **Documentation**
   - Improve README or guides
   - Add code comments
   - Create tutorials or examples

4. **Testing**
   - Write unit tests
   - Write integration tests
   - Improve test coverage

5. **Performance**
   - Optimize scanning algorithms
   - Improve frontend performance
   - Reduce API response times

---

## Coding Standards

### Python (Backend)

**Style Guide:**
- Follow PEP 8 style guide
- Use type hints
- Maximum line length: 100 characters

**Example:**
```python
from typing import List, Dict

def parse_ports(nmap_output: str) -> List[Dict]:
    """
    Extracts open ports from Nmap output.
    
    Args:
        nmap_output: Raw output from Nmap command
        
    Returns:
        List of dictionaries containing port information
    """
    ports = []
    # Implementation...
    return ports
```

**Linting:**
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black main.py

# Check style
flake8 main.py

# Type checking
mypy main.py
```

### TypeScript/React (Frontend)

**Style Guide:**
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Use Tailwind CSS for styling

**Example:**
```typescript
interface ScanResult {
  target: string;
  open_ports: Port[];
  cves: string[];
}

export default function ScanResults({ result }: { result: ScanResult }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      {/* Implementation */}
    </div>
  );
}
```

**Linting:**
```bash
# Check linting
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

### Commit Messages

Follow the Conventional Commits specification:

```
type(scope): brief description

Detailed explanation if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(backend): add rate limiting to scan endpoint
fix(frontend): resolve mobile responsive issue
docs(readme): update installation instructions
refactor(backend): improve error handling
```

---

## Pull Request Process

### Before Submitting

1. **Create a new branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clean, well-documented code
   - Follow coding standards
   - Add tests if applicable

3. **Test your changes**
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run build
```

4. **Update documentation**
   - Update README if needed
   - Add inline comments
   - Update CHANGELOG

5. **Commit your changes**
```bash
git add .
git commit -m "feat: add new feature"
```

6. **Sync with upstream**
```bash
git fetch upstream
git rebase upstream/main
```

7. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

### Creating the Pull Request

1. Go to the repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tested locally
- [ ] Added unit tests
- [ ] Updated documentation

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Fixes #123
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs
   - Linting and tests must pass

2. **Code Review**
   - Maintainers will review your code
   - Address feedback and comments
   - Make requested changes

3. **Approval and Merge**
   - Once approved, maintainers will merge
   - Your contribution will be credited

---

## Reporting Bugs

### Before Reporting
- Check if the bug has already been reported
- Verify it's reproducible
- Gather relevant information

### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 95]
- Python Version: [e.g., 3.11]
- Node Version: [e.g., 18.0]

**Screenshots**
If applicable, add screenshots

**Additional Context**
Any other relevant information
```

---

## Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired solution

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Any other relevant information

**Implementation ideas**
If you have ideas on how to implement
```

---

## Development Workflow

### Project Structure
```
vuln-scanner-webapp/
├── backend/           # FastAPI application
│   ├── main.py       # Main application file
│   └── tests/        # Backend tests (to be added)
├── frontend/         # Next.js application
│   ├── app/          # App directory
│   └── components/   # Reusable components
└── docs/             # Additional documentation
```

### Branch Strategy
- `main`: Stable, production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent fixes for production

### Release Process
1. Create release branch from `develop`
2. Update version numbers
3. Update CHANGELOG
4. Create pull request to `main`
5. Tag release after merge
6. Deploy to production

---

## Getting Help

### Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Nmap Documentation](https://nmap.org/book/man.html)

### Contact
- GitHub Issues: For bug reports and feature requests
- GitHub Discussions: For questions and discussions
- Email: aryan@example.com (replace with actual email)

---

## Recognition

Contributors will be recognized in:
- README Contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉

---

**Last Updated:** November 2025
