# Security Review Agent - Configuration & Testing Framework

This document defines the security agent configuration for automated and manual security reviews of the Scout Badge Inventory application.

## Purpose

Establish a repeatable security testing framework to identify and prevent vulnerabilities throughout the development lifecycle.

## Security Review Scope

### Components Reviewed
1. **Backend API** (Python/FastAPI)
2. **Frontend Application** (Next.js/React/TypeScript)
3. **Database Operations** (SQLite/SQLAlchemy)
4. **File Upload & Processing** (Image handling)
5. **Configuration & Secrets Management**
6. **Network & API Security**

---

## Security Agent Configuration

### Agent Profile

```yaml
Agent Name: Security Reviewer
Role: Automated Security Vulnerability Scanner
Frequency: On-demand, Pre-deployment, Weekly scheduled
Focus Areas:
  - OWASP Top 10 vulnerabilities
  - Input validation & sanitization
  - Authentication & authorization
  - Data exposure & information leakage
  - Secure file handling
  - Dependency vulnerabilities
  - Configuration security
```

### Review Checklist

#### 1. Input Validation & Injection Prevention

**Risk Level**: 🔴 Critical

**Check Points**:
- [ ] SQL Injection prevention (parameterized queries)
- [ ] Command Injection prevention (file operations, system calls)
- [ ] Path Traversal prevention (file uploads, reads)
- [ ] NoSQL/ORM Injection (SQLAlchemy queries)
- [ ] XSS prevention (output encoding, React auto-escaping)
- [ ] SSRF prevention (external API calls)

**Test Locations**:
- `backend/api/upload.py` - File upload validation
- `backend/api/processing.py` - Scan ID validation
- `backend/api/inventory.py` - Badge ID validation
- `backend/services/ollama_client.py` - External API calls
- `database/*.py` - All database queries

**Example Vulnerabilities to Check**:
```python
# ❌ BAD: SQL Injection vulnerable
query = f"SELECT * FROM badges WHERE id = '{badge_id}'"

# ✅ GOOD: Parameterized query
badge = db.query(Badge).filter(Badge.id == badge_id).first()

# ❌ BAD: Command Injection vulnerable
os.system(f"convert {user_file} output.jpg")

# ✅ GOOD: Use safe libraries
from PIL import Image
img = Image.open(validated_path)
```

---

#### 2. Authentication & Authorization

**Risk Level**: 🟡 High (Currently not implemented)

**Check Points**:
- [ ] No authentication currently exists (documented limitation)
- [ ] API endpoints are publicly accessible
- [ ] No rate limiting on API calls
- [ ] No session management
- [ ] No CSRF protection

**Current Status**: ⚠️ **MVP has no authentication**
- Acceptable for local/trusted network deployment
- **MUST be added before internet-facing deployment**

**Future Requirements** (ACTION-600):
- Implement user authentication (NextAuth.js)
- Add API key authentication
- Implement role-based access control (RBAC)
- Add rate limiting
- Implement CSRF tokens

---

#### 3. File Upload Security

**Risk Level**: 🔴 Critical

**Check Points**:
- [ ] File type validation (whitelist approach)
- [ ] File size limits enforced
- [ ] Filename sanitization
- [ ] Storage path validation (prevent directory traversal)
- [ ] Malicious file content detection
- [ ] Secure file serving (prevent direct access)

**Test Locations**:
- `backend/api/upload.py` - Upload validation
- `backend/main.py` - Static file serving configuration

**Test Cases**:
```python
# Test malicious filenames
test_files = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "file.php.jpg",  # Double extension
    "file\x00.jpg",  # Null byte injection
    "file.jpg.exe",
    "<script>alert('xss')</script>.jpg",
]

# Test file size limits
test_oversized = create_file(size=100_000_000)  # 100MB

# Test invalid file types
test_invalid = {
    "test.exe": "application/x-msdownload",
    "test.php": "application/x-php",
    "test.sh": "application/x-sh",
}
```

---

#### 4. Sensitive Data Exposure

**Risk Level**: 🔴 Critical

**Check Points**:
- [ ] No secrets in code (API keys, passwords)
- [ ] Environment variables used correctly
- [ ] No sensitive data in logs
- [ ] No sensitive data in error messages
- [ ] Database credentials secured
- [ ] No data leakage in API responses

**Test Locations**:
- `.env` files (should not be in git)
- `backend/main.py` - Error handling
- `backend/api/*.py` - API response content
- `frontend/lib/api.ts` - API keys

**Security Patterns**:
```python
# ✅ GOOD: Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# ❌ BAD: Hardcoded credentials
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# ✅ GOOD: Generic error messages
return {"error": "Processing failed"}

# ❌ BAD: Information leakage
return {"error": f"Database connection failed: {str(exception)}"}
```

---

#### 5. Cross-Site Scripting (XSS)

**Risk Level**: 🟡 High

**Check Points**:
- [ ] React auto-escaping (enabled by default)
- [ ] No `dangerouslySetInnerHTML` usage
- [ ] User input sanitized before display
- [ ] Content Security Policy (CSP) headers
- [ ] No inline scripts

**Test Locations**:
- `frontend/components/*.tsx` - All components
- `frontend/app/**/*.tsx` - All pages

**Test Cases**:
```javascript
// Test XSS payloads
const xss_payloads = [
  '<script>alert("XSS")</script>',
  '<img src=x onerror=alert("XSS")>',
  'javascript:alert("XSS")',
  '<iframe src="javascript:alert(\'XSS\')">',
  '<svg onload=alert("XSS")>',
]

// Test in:
// - Badge names
// - Detection names
// - Inventory notes
// - Error messages
```

---

#### 6. Insecure Dependencies

**Risk Level**: 🟡 High

**Check Points**:
- [ ] No known vulnerable dependencies
- [ ] Dependencies up to date
- [ ] Unused dependencies removed
- [ ] Lock files committed (package-lock.json, requirements.txt)

**Test Commands**:
```bash
# Python dependencies
pip install safety
safety check

# Or use pip-audit
pip install pip-audit
pip-audit

# Node.js dependencies
npm audit
npm audit fix

# Check for outdated packages
npm outdated
pip list --outdated
```

---

#### 7. API Security

**Risk Level**: 🟡 High

**Check Points**:
- [ ] CORS configured correctly
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Proper error handling (no stack traces)
- [ ] HTTPS enforced (production)
- [ ] API versioning considered

**Test Locations**:
- `backend/main.py` - CORS configuration
- `backend/api/*.py` - All endpoint handlers

**CORS Configuration Review**:
```python
# Current (development)
origins = ["http://localhost:3000"]

# Production checklist:
# - Use specific origins (not "*")
# - Enable credentials if needed
# - Limit allowed methods
# - Set appropriate headers
```

---

#### 8. File System Security

**Risk Level**: 🔴 Critical

**Check Points**:
- [ ] Path traversal prevention
- [ ] Secure file permissions
- [ ] No arbitrary file access
- [ ] Upload directory isolated
- [ ] Temporary files cleaned up

**Test Cases**:
```python
# Path traversal attempts
malicious_paths = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32",
    "/etc/passwd",
    "C:\\Windows\\System32",
    "uploads/../database/inventory.db",
    "uploads/../../secrets.env",
]

# Each should be rejected or sanitized
```

---

#### 9. Denial of Service (DoS)

**Risk Level**: 🟡 High

**Check Points**:
- [ ] File size limits enforced
- [ ] Request rate limiting
- [ ] Resource cleanup (connections, files)
- [ ] Timeout configurations
- [ ] Memory usage limits

**Test Scenarios**:
- Upload extremely large files
- Send rapid-fire API requests
- Submit very complex queries
- Upload many files simultaneously

---

#### 10. Configuration Security

**Risk Level**: 🟡 High

**Check Points**:
- [ ] Debug mode disabled in production
- [ ] Secure default configurations
- [ ] Environment-specific settings
- [ ] No hardcoded secrets
- [ ] Proper file permissions (600 for .env)

**Files to Review**:
- `.env` files
- `backend/main.py` - App configuration
- `frontend/lib/config.ts` - Frontend configuration
- `docker-compose.yml` - Container configuration

---

## Security Testing Procedures

### 1. Pre-Deployment Review

**When**: Before deploying to production or exposing to network

**Process**:
```bash
# 1. Run dependency checks
cd backend
pip-audit
cd ../frontend
npm audit

# 2. Review code changes
git diff main...feature-branch

# 3. Check for secrets
git secrets --scan

# 4. Manual security review
# Use this checklist document

# 5. Run integration tests
python tests/integration/run_all_tests.py
```

---

### 2. Scheduled Weekly Review

**When**: Every Monday at 9:00 AM

**Automated Checks**:
```yaml
schedule:
  - dependency_scan:
      frequency: weekly
      tools: [pip-audit, npm audit]

  - static_analysis:
      frequency: weekly
      tools: [bandit, eslint-security]

  - secret_scan:
      frequency: weekly
      tools: [git-secrets, truffleHog]
```

---

### 3. Code Review Security Checklist

**Use During Pull Requests**:

```markdown
## Security Review Checklist

- [ ] No new SQL injection vectors
- [ ] Input validation on all user inputs
- [ ] No sensitive data logged
- [ ] No hardcoded secrets or credentials
- [ ] File uploads properly validated
- [ ] Error messages don't leak information
- [ ] No dangerous functions (eval, exec, os.system)
- [ ] Dependencies checked for vulnerabilities
- [ ] CORS settings reviewed
- [ ] Authentication/authorization preserved
```

---

## Security Testing Tools

### Automated Tools

#### Backend (Python/FastAPI)

1. **Bandit** - Security linter
   ```bash
   pip install bandit
   bandit -r backend/ -f json -o security-report.json
   ```

2. **Safety** - Dependency vulnerability scanner
   ```bash
   pip install safety
   safety check --json
   ```

3. **pip-audit** - Python dependency auditor
   ```bash
   pip install pip-audit
   pip-audit --format json
   ```

#### Frontend (TypeScript/React)

1. **npm audit** - Built-in vulnerability scanner
   ```bash
   npm audit --json
   ```

2. **ESLint Security Plugin**
   ```bash
   npm install --save-dev eslint-plugin-security
   ```

3. **Snyk** - Comprehensive security scanner
   ```bash
   npm install -g snyk
   snyk test
   ```

#### General

1. **OWASP ZAP** - Web application security scanner
   ```bash
   docker run -t owasp/zap2docker-stable zap-baseline.py \
     -t http://localhost:3000
   ```

2. **git-secrets** - Prevent committing secrets
   ```bash
   brew install git-secrets
   git secrets --scan
   ```

---

## Vulnerability Severity Levels

### 🔴 Critical
- Requires immediate fix
- Could lead to data breach or system compromise
- Examples: SQL injection, arbitrary file upload, authentication bypass

### 🟡 High
- Should be fixed before next release
- Could lead to data exposure or service disruption
- Examples: XSS, sensitive data in logs, DoS vulnerabilities

### 🟢 Medium
- Should be fixed in near future
- Limited impact or requires specific conditions
- Examples: information disclosure, missing security headers

### ⚪ Low
- Consider fixing if time permits
- Minimal security impact
- Examples: outdated dependencies (no known exploits)

---

## Current Known Limitations

### Documented Security Limitations (MVP)

1. **No Authentication** 🔴
   - Status: Accepted for local deployment
   - Risk: Anyone on network can access
   - Mitigation: Deploy only on trusted networks
   - Planned: ACTION-600 (Multi-User Support)

2. **No Rate Limiting** 🟡
   - Status: Not implemented
   - Risk: API abuse, DoS attacks
   - Mitigation: Deploy behind firewall
   - Planned: ACTION-604 (API improvements)

3. **No HTTPS** 🟡
   - Status: HTTP only
   - Risk: Traffic can be intercepted
   - Mitigation: Use trusted local network only
   - Planned: Production deployment guide

4. **Verbose Error Messages** 🟢
   - Status: Development mode enabled
   - Risk: Information leakage
   - Mitigation: Disable debug mode in production
   - Action: Set `DEBUG=False` before deployment

---

## Security Incident Response

### If Vulnerability Discovered

1. **Assess Severity** (Critical/High/Medium/Low)
2. **Document**:
   - Description of vulnerability
   - Affected components
   - Potential impact
   - Reproduction steps
3. **Create Fix**:
   - Develop patch
   - Test thoroughly
   - Review with checklist
4. **Deploy**:
   - Emergency deployment if critical
   - Notify users if data affected
5. **Post-Mortem**:
   - Root cause analysis
   - Update this checklist
   - Improve testing procedures

---

## Security Testing Schedule

### Daily
- Automated dependency checks (CI/CD)
- Git secret scanning (pre-commit hooks)

### Weekly
- Manual security review of new code
- Run full test suite
- Review logs for anomalies

### Monthly
- Full security audit using OWASP ZAP
- Review and update security documentation
- Dependency updates and patches

### Quarterly
- External security assessment (if available)
- Penetration testing
- Security training for team

---

## Security Best Practices

### Development Guidelines

1. **Input Validation**
   - Validate all user inputs
   - Use whitelist validation (not blacklist)
   - Sanitize before processing
   - Never trust client-side validation alone

2. **Output Encoding**
   - Encode output based on context (HTML, URL, JavaScript)
   - Use framework's built-in escaping
   - Never use `dangerouslySetInnerHTML`

3. **Authentication & Authorization**
   - Implement authentication before internet deployment
   - Use proven libraries (don't roll your own)
   - Implement principle of least privilege
   - Session management best practices

4. **Sensitive Data**
   - Never log sensitive data
   - Use environment variables for secrets
   - Encrypt sensitive data at rest
   - Use HTTPS for data in transit

5. **Error Handling**
   - Generic error messages to users
   - Detailed errors to logs only
   - Never expose stack traces
   - Log security events

6. **Dependencies**
   - Keep dependencies up to date
   - Remove unused dependencies
   - Review security advisories
   - Use lock files

---

## Integration with CI/CD

### GitHub Actions Workflow Example

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r backend/

      - name: Run npm audit
        run: |
          cd frontend
          npm install
          npm audit

      - name: Check for secrets
        run: |
          pip install detect-secrets
          detect-secrets scan
```

---

## Resources

### Security References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security Best Practices](https://reactjs.org/docs/security.html)

### Tools Documentation
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [npm audit Documentation](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [OWASP ZAP](https://www.zaproxy.org/docs/)

---

## Changelog

| Date | Version | Changes | Reviewer |
|------|---------|---------|----------|
| 2025-11-10 | 1.0 | Initial security framework created | Claude Code |
| | | Documented known limitations | |
| | | Created testing procedures | |

---

**Last Updated**: 2025-11-10
**Next Review**: 2025-11-17
**Document Owner**: Development Team

---

## Appendix A: Quick Security Audit Commands

```bash
# Complete security audit script
#!/bin/bash

echo "=== Scout Badge Inventory - Security Audit ==="

echo "\n1. Checking Python dependencies..."
cd backend
pip-audit || echo "pip-audit not installed"

echo "\n2. Checking Node dependencies..."
cd ../frontend
npm audit

echo "\n3. Running Bandit security linter..."
cd ../backend
bandit -r . -f screen || echo "Bandit not installed"

echo "\n4. Checking for secrets in git history..."
cd ..
git secrets --scan || echo "git-secrets not installed"

echo "\n5. Checking file permissions..."
ls -la .env* 2>/dev/null || echo "No .env files found"

echo "\n=== Audit Complete ==="
```

Save as `scripts/security-audit.sh` and run regularly.
