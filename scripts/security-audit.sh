#!/bin/bash
#
# Scout Badge Inventory - Security Audit Script
#
# Runs automated security checks on the codebase
# Usage: ./scripts/security-audit.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Scout Badge Inventory - Security Audit${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Project: $PROJECT_ROOT"
echo "Date: $(date)"
echo ""

# Track issues found
ISSUES_FOUND=0

# ============================================================================
# 1. Check for secrets in code
# ============================================================================
echo -e "${YELLOW}[1/8] Checking for hardcoded secrets...${NC}"

SECRETS_FOUND=0

# Check for common secret patterns
echo "  → Scanning for API keys, passwords, tokens..."
if grep -r -i -E "(api[_-]?key|password|secret|token|credentials).*=.*['\"][a-zA-Z0-9]{20,}" \
    --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=dist --exclude-dir=.next --exclude-dir=build \
    "$PROJECT_ROOT" 2>/dev/null | grep -v -E "(NEXT_PUBLIC|process\.env|config\.ts|\.md|vendor-chunks)"; then
    SECRETS_FOUND=1
    echo -e "${RED}    ✗ Potential secrets found!${NC}"
else
    echo -e "${GREEN}    ✓ No obvious secrets detected${NC}"
fi

# Check for AWS/cloud credentials
if grep -r -i -E "(AKIA|aws_access_key|aws_secret)" \
    --include="*.py" --include="*.ts" --include="*.tsx" \
    --exclude-dir=node_modules --exclude-dir=venv \
    "$PROJECT_ROOT" 2>/dev/null; then
    SECRETS_FOUND=1
    echo -e "${RED}    ✗ AWS credentials found!${NC}"
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}    ✓ Secrets check passed${NC}"
else
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo ""

# ============================================================================
# 2. Check file permissions
# ============================================================================
echo -e "${YELLOW}[2/8] Checking file permissions...${NC}"

if [ -f "$PROJECT_ROOT/.env" ]; then
    PERMS=$(stat -f "%A" "$PROJECT_ROOT/.env" 2>/dev/null || stat -c "%a" "$PROJECT_ROOT/.env" 2>/dev/null)
    if [ "$PERMS" != "600" ] && [ "$PERMS" != "400" ]; then
        echo -e "${RED}    ✗ .env file has insecure permissions: $PERMS${NC}"
        echo "      Recommended: chmod 600 .env"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}    ✓ .env permissions secure ($PERMS)${NC}"
    fi
else
    echo -e "${GREEN}    ✓ No .env file in root (using .env.example)${NC}"
fi

echo ""

# ============================================================================
# 3. Check Python dependencies for vulnerabilities
# ============================================================================
echo -e "${YELLOW}[3/8] Checking Python dependencies...${NC}"

cd "$PROJECT_ROOT/backend"

if command -v pip-audit &> /dev/null; then
    echo "  → Running pip-audit..."
    if pip-audit --format json > /tmp/pip-audit.json 2>&1; then
        VULNS=$(cat /tmp/pip-audit.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('vulnerabilities', [])))" 2>/dev/null || echo "0")
        if [ "$VULNS" -gt 0 ]; then
            echo -e "${RED}    ✗ Found $VULNS vulnerabilities in Python dependencies${NC}"
            pip-audit --format columns | head -20
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        else
            echo -e "${GREEN}    ✓ No known vulnerabilities in Python dependencies${NC}"
        fi
    else
        echo -e "${YELLOW}    ⚠ pip-audit check failed${NC}"
    fi
else
    echo -e "${YELLOW}    ⚠ pip-audit not installed (install: pip install pip-audit)${NC}"
fi

echo ""

# ============================================================================
# 4. Check Node.js dependencies for vulnerabilities
# ============================================================================
echo -e "${YELLOW}[4/8] Checking Node.js dependencies...${NC}"

cd "$PROJECT_ROOT/frontend"

if [ -d "node_modules" ]; then
    echo "  → Running npm audit..."
    if npm audit --json > /tmp/npm-audit.json 2>&1; then
        VULNS=$(cat /tmp/npm-audit.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('metadata', {}).get('vulnerabilities', {}).get('total', 0))" 2>/dev/null || echo "0")
        if [ "$VULNS" -gt 0 ]; then
            echo -e "${RED}    ✗ Found $VULNS vulnerabilities in Node dependencies${NC}"
            npm audit --production | head -30
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        else
            echo -e "${GREEN}    ✓ No known vulnerabilities in Node dependencies${NC}"
        fi
    else
        echo -e "${YELLOW}    ⚠ npm audit check failed${NC}"
    fi
else
    echo -e "${YELLOW}    ⚠ node_modules not found (run: npm install)${NC}"
fi

echo ""

# ============================================================================
# 5. Check for dangerous code patterns
# ============================================================================
echo -e "${YELLOW}[5/8] Checking for dangerous code patterns...${NC}"

cd "$PROJECT_ROOT"

DANGEROUS_FOUND=0

# Check for eval/exec in Python
if grep -r -E "(eval|exec)\(" --include="*.py" --exclude-dir=venv backend/ 2>/dev/null | grep -v "^Binary"; then
    echo -e "${RED}    ✗ Dangerous eval/exec found in Python code${NC}"
    DANGEROUS_FOUND=1
fi

# Check for os.system/subprocess.call with shell=True
if grep -r -E "os\.system|subprocess\.(call|run|Popen).*shell\s*=\s*True" --include="*.py" --exclude-dir=venv backend/ 2>/dev/null; then
    echo -e "${RED}    ✗ Dangerous shell command execution found${NC}"
    DANGEROUS_FOUND=1
fi

# Check for dangerouslySetInnerHTML in React
if grep -r "dangerouslySetInnerHTML" --include="*.tsx" --include="*.jsx" frontend/ 2>/dev/null; then
    echo -e "${RED}    ✗ dangerouslySetInnerHTML usage found (XSS risk)${NC}"
    DANGEROUS_FOUND=1
fi

if [ $DANGEROUS_FOUND -eq 0 ]; then
    echo -e "${GREEN}    ✓ No dangerous code patterns detected${NC}"
else
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo ""

# ============================================================================
# 6. Check SQL injection prevention
# ============================================================================
echo -e "${YELLOW}[6/8] Checking SQL injection prevention...${NC}"

SQL_ISSUES=0

# Check for string formatting in SQL queries
if grep -r -E "f\".*SELECT|\".*SELECT.*\{|%.*SELECT" --include="*.py" backend/ 2>/dev/null | grep -v "^Binary"; then
    echo -e "${RED}    ✗ Potential SQL injection via string formatting${NC}"
    SQL_ISSUES=1
fi

# Check for raw SQL execution
if grep -r "execute.*%" --include="*.py" backend/ 2>/dev/null | grep -v "^Binary"; then
    echo -e "${RED}    ✗ Potential SQL injection via execute with %${NC}"
    SQL_ISSUES=1
fi

if [ $SQL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}    ✓ No SQL injection patterns detected${NC}"
else
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo ""

# ============================================================================
# 7. Check file upload security
# ============================================================================
echo -e "${YELLOW}[7/8] Checking file upload security...${NC}"

UPLOAD_ISSUES=0

# Check if upload validation exists
if ! grep -q "ALLOWED_EXTENSIONS\|allowed.*extensions" backend/api/upload.py 2>/dev/null; then
    echo -e "${RED}    ✗ No file extension whitelist found${NC}"
    UPLOAD_ISSUES=1
fi

# Check for path traversal prevention
if ! grep -q "secure_filename\|sanitize.*path\|basename" backend/api/upload.py 2>/dev/null; then
    echo -e "${YELLOW}    ⚠ Path traversal prevention not obvious${NC}"
fi

if [ $UPLOAD_ISSUES -eq 0 ]; then
    echo -e "${GREEN}    ✓ File upload security checks present${NC}"
else
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

echo ""

# ============================================================================
# 8. Check CORS configuration
# ============================================================================
echo -e "${YELLOW}[8/8] Checking CORS configuration...${NC}"

if grep -q "allow_origins=\[\"*\"\]" backend/main.py 2>/dev/null; then
    echo -e "${RED}    ✗ CORS allows all origins (insecure for production)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}    ✓ CORS configuration appears restricted${NC}"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Security Audit Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! No security issues found.${NC}"
    echo ""
    echo "Note: This is an automated scan. Manual review is still recommended."
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES_FOUND potential security issue(s)${NC}"
    echo ""
    echo "Please review the issues above and address them before deployment."
    echo ""
    echo "For detailed security guidelines, see:"
    echo "  - docs/SECURITY_REVIEW.md"
    echo "  - https://owasp.org/www-project-top-ten/"
    exit 1
fi
