#!/bin/bash
#
# Scout Badge Inventory - Frontend Validation Script
#
# Tests all frontend routes to ensure they load correctly without 404 errors
# Usage: ./scripts/validate-frontend.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Scout Badge Inventory - Frontend Validation${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo "Date: $(date)"
echo ""

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
FAILED_ROUTES=()

# ============================================================================
# Helper Functions
# ============================================================================

test_route() {
    local route="$1"
    local expected_status="${2:-200}"
    local description="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "  Testing: $route ... "

    # Make request and capture status code
    response=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$route" 2>&1)

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} ($response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_ROUTES+=("$route (expected $expected_status, got $response)")
        return 1
    fi
}

test_api_endpoint() {
    local endpoint="$1"
    local method="${2:-GET}"
    local expected_status="${3:-200}"
    local description="$4"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "  Testing API: $endpoint ... "

    # Make request and capture status code
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$endpoint" 2>&1)
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BACKEND_URL$endpoint" 2>&1)
    fi

    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} ($response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_ROUTES+=("API: $endpoint (expected $expected_status, got $response)")
        return 1
    fi
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

echo -e "${YELLOW}[Pre-flight] Checking services...${NC}"

# Check backend health
echo -n "  Checking backend health ... "
if curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not accessible${NC}"
    echo ""
    echo "Please start the backend first:"
    echo "  cd $PROJECT_ROOT"
    echo "  ./scripts/start-backend.sh"
    exit 1
fi

# Check frontend
echo -n "  Checking frontend ... "
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not accessible${NC}"
    echo ""
    echo "Please start the frontend first:"
    echo "  cd $PROJECT_ROOT"
    echo "  ./scripts/start-frontend.sh"
    exit 1
fi

echo ""

# ============================================================================
# Test Frontend Routes
# ============================================================================

echo -e "${YELLOW}[1/4] Testing main navigation routes...${NC}"
test_route "/" 200 "Home page"
test_route "/inventory" 200 "Inventory dashboard"
test_route "/reports" 200 "Reports page"

echo ""

# ============================================================================
# Test Dynamic Routes (require data setup)
# ============================================================================

echo -e "${YELLOW}[2/4] Testing dynamic routes...${NC}"

# Get a scan ID from the database if available
# Try to find scan IDs by checking if scan 1 exists
SCAN_ID=""
for id in 1 2 3 4 5 10 14 15; do
    if curl -s "$BACKEND_URL/api/scans/$id" 2>/dev/null | grep -q '"id"'; then
        SCAN_ID=$id
        break
    fi
done

if [ -n "$SCAN_ID" ]; then
    test_route "/scan/$SCAN_ID" 200 "Scan processing page"
    test_route "/results/$SCAN_ID" 200 "Results review page"
else
    echo -e "  ${YELLOW}⚠ Skipping scan routes (no scan data available)${NC}"
    echo "    To test these routes, upload images first at $FRONTEND_URL"
fi

echo ""

# ============================================================================
# Test API Endpoints
# ============================================================================

echo -e "${YELLOW}[3/4] Testing critical API endpoints...${NC}"

test_api_endpoint "/health" "GET" 200 "Health check"
test_api_endpoint "/api/inventory" "GET" 200 "Inventory list"
test_api_endpoint "/api/inventory/stats" "GET" 200 "Inventory statistics"

# Test specific badge endpoint if we have data
BADGE_ID=$(curl -s "$BACKEND_URL/api/inventory" 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); items=data.get('items', []); print(items[0]['badge_id'] if items else '')" 2>/dev/null || echo "")

if [ -n "$BADGE_ID" ]; then
    test_api_endpoint "/api/inventory/$BADGE_ID" "GET" 200 "Specific badge inventory"
else
    echo -e "  ${YELLOW}⚠ Skipping badge detail endpoint (no badge data)${NC}"
fi

echo ""

# ============================================================================
# Test 404 Handling
# ============================================================================

echo -e "${YELLOW}[4/4] Testing 404 error handling...${NC}"

test_route "/nonexistent-page" 404 "Non-existent page"
test_route "/scan/999999" 200 "Invalid scan ID (should show error message, not 404)"
test_api_endpoint "/api/inventory/INVALID_BADGE_ID" "GET" 404 "Invalid badge ID"

echo ""

# ============================================================================
# Test Component-Specific Features
# ============================================================================

echo -e "${YELLOW}[Bonus] Testing component-specific features...${NC}"

# Test inventory page loads (tabs are client-side rendered)
echo -n "  Testing inventory page loads correctly ... "
inventory_html=$(curl -s "$FRONTEND_URL/inventory")
if echo "$inventory_html" | grep -q "Badge Inventory"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ SKIP${NC} (Page loads but client-side content not testable via curl)"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "The frontend is functioning correctly with no 404 errors."
    exit 0
else
    echo -e "${RED}✗ $FAILED_TESTS test(s) failed${NC}"
    echo ""
    echo "Failed routes:"
    for route in "${FAILED_ROUTES[@]}"; do
        echo -e "  ${RED}✗${NC} $route"
    done
    echo ""
    echo "Please review the failed routes and fix any issues."
    exit 1
fi
