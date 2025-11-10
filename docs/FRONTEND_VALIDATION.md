# Frontend Validation Agent

Automated testing agent for validating all frontend routes and API endpoints.

## Overview

The frontend validation script (`scripts/validate-frontend.sh`) automatically tests all application screens and API endpoints to ensure they load correctly without 404 errors.

## Usage

```bash
cd /path/to/Scouts_InventoryOrder
./scripts/validate-frontend.sh
```

## Prerequisites

- Backend must be running on `http://localhost:8000`
- Frontend must be running on `http://localhost:3000`
- Use environment variables to override:
  ```bash
  FRONTEND_URL=http://localhost:3001 BACKEND_URL=http://localhost:8001 ./scripts/validate-frontend.sh
  ```

## What It Tests

### 1. Main Navigation Routes (3 tests)
- **Home page** (`/`) - Main landing page
- **Inventory dashboard** (`/inventory`) - Badge inventory management
- **Reports page** (`/reports`) - Reports and analytics

### 2. Dynamic Routes (2 tests)
- **Scan processing page** (`/scan/{id}`) - Real-time processing status
- **Results review page** (`/results/{id}`) - Badge detection results

These tests require existing scan data. If no scans exist, they are skipped with a warning.

### 3. Critical API Endpoints (4+ tests)
- **Health check** (`/health`) - Backend health status
- **Inventory list** (`/api/inventory`) - All inventory items
- **Inventory statistics** (`/api/inventory/stats`) - Analytics data
- **Specific badge inventory** (`/api/inventory/{badge_id}`) - Badge details (if data exists)

### 4. 404 Error Handling (3 tests)
- **Non-existent page** - Should return 404
- **Invalid scan ID** - Should show error message, not crash
- **Invalid badge ID** - API should return 404

### 5. Bonus Tests (1 test)
- **Inventory page content** - Verifies page title renders correctly

## Test Results

### Success Output
```
================================================
Scout Badge Inventory - Frontend Validation
================================================

Frontend URL: http://localhost:3000
Backend URL: http://localhost:8000

[1/4] Testing main navigation routes...
  Testing: / ... ✓ PASS (200)
  Testing: /inventory ... ✓ PASS (200)
  Testing: /reports ... ✓ PASS (200)

...

================================================
Validation Summary
================================================

Total Tests: 13
Passed: 13
Failed: 0

✓ All tests passed!

The frontend is functioning correctly with no 404 errors.
```

### Failure Output
When tests fail, the script:
1. Shows which routes failed
2. Displays expected vs actual HTTP status codes
3. Exits with error code 1
4. Lists all failed routes at the end

Example:
```
✗ 2 test(s) failed

Failed routes:
  ✗ /inventory (expected 200, got 404)
  ✗ API: /api/inventory/stats (expected 200, got 500)
```

## Exit Codes

- **0** - All tests passed
- **1** - One or more tests failed, or services not running

## Troubleshooting

### Backend Not Running
```
✗ Backend is not accessible

Please start the backend first:
  cd /path/to/Scouts_InventoryOrder
  ./scripts/start-backend.sh
```

### Frontend Not Running
```
✗ Frontend is not accessible

Please start the frontend first:
  cd /path/to/Scouts_InventoryOrder
  ./scripts/start-frontend.sh
```

### Scan Routes Skipped
```
⚠ Skipping scan routes (no scan data available)
    To test these routes, upload images first at http://localhost:3000
```

This is expected on fresh installations. Upload some badge images to create scan data.

### Badge Details Skipped
```
⚠ Skipping badge detail endpoint (no badge data)
```

This happens when inventory is empty. Process some scans to populate the inventory.

## When to Run

### During Development
- After adding new routes or pages
- After modifying API endpoints
- Before committing route-related changes
- When debugging 404 errors

### Before Deployment
- Run as part of pre-deployment checklist
- Verify all routes work after configuration changes
- Test with production-like environment variables

### CI/CD Integration
Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml
- name: Start services
  run: |
    ./scripts/start-backend.sh &
    ./scripts/start-frontend.sh &
    sleep 10

- name: Run frontend validation
  run: ./scripts/validate-frontend.sh
```

## Extending the Tests

### Adding New Routes

Edit `scripts/validate-frontend.sh` and add tests in the appropriate section:

```bash
# For static routes
test_route "/new-page" 200 "New page description"

# For dynamic routes
test_route "/items/$ITEM_ID" 200 "Item detail page"

# For API endpoints
test_api_endpoint "/api/new-endpoint" "GET" 200 "New API endpoint"
```

### Testing POST/PUT Endpoints

The script supports different HTTP methods:

```bash
test_api_endpoint "/api/endpoint" "POST" 201 "Create resource"
test_api_endpoint "/api/endpoint/1" "PUT" 200 "Update resource"
```

### Custom Validation Logic

For complex validation beyond status codes:

```bash
response=$(curl -s "$FRONTEND_URL/page")
if echo "$response" | grep -q "Expected Content"; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${RED}✗ FAIL${NC}"
fi
```

## Related Scripts

- [security-audit.sh](../scripts/security-audit.sh) - Security vulnerability scanning
- [start-backend.sh](../scripts/start-backend.sh) - Start backend server
- [start-frontend.sh](../scripts/start-frontend.sh) - Start frontend server

## Known Limitations

1. **Client-Side Rendering**: Cannot test React component state or client-side interactions
2. **Authentication**: No authentication testing (not yet implemented)
3. **Browser-Specific**: Only tests server responses, not browser rendering
4. **Sequential Testing**: Tests run sequentially, not in parallel

For full end-to-end testing including browser interactions, consider tools like:
- Playwright
- Cypress
- Selenium

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-10 | 1.0 | Initial validation script created |
| | | Tests for main routes, dynamic routes, API endpoints |
| | | 404 error handling validation |
| | | Pre-flight service checks |

---

**Last Updated**: 2025-11-10
**Script Location**: [scripts/validate-frontend.sh](../scripts/validate-frontend.sh)
