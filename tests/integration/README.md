# Integration Tests - Scout Badge Inventory System

Comprehensive end-to-end and edge case testing suite for the Scout Badge Inventory application.

## Overview

This test suite validates the complete workflow from image upload through AI processing to inventory management, ensuring the system works correctly in real-world scenarios.

## Test Coverage

### End-to-End Tests (`test_e2e_workflow.py`)

Tests the complete happy path workflow:

1. **Backend Health Check** - Verify API is running
2. **Image Upload** - Upload badge photos and receive scan_id
3. **AI Processing** - Process images with Ollama, monitor progress
4. **Results Retrieval** - Fetch detection results with confidence scores
5. **Inventory Operations** - Update inventory from scan results
6. **Edge Cases** - Invalid inputs, filtering, error handling

**Expected Duration:** 2-5 minutes per image (Ollama processing time)

### Edge Case Tests (`test_edge_cases.py`)

Tests error handling and boundary conditions:

1. **Large Batch Upload** - 20 images simultaneously
2. **Oversized File** - Files exceeding 10MB limit
3. **Invalid File Type** - Non-image files
4. **Empty Upload** - No files provided
5. **Poor Quality Image** - Very small/low resolution
6. **Concurrent Uploads** - Multiple simultaneous requests
7. **Duplicate Processing** - Starting same scan twice
8. **Invalid Inventory Update** - Non-existent badges, negative quantities
9. **API Rate Limiting** - Rapid successive calls
10. **Database Consistency** - State consistency across requests

**Expected Duration:** 1-2 minutes (no heavy AI processing)

## Prerequisites

### 1. Backend Server Running

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

The backend should be accessible at `http://localhost:8000`

### 2. Ollama Running

```bash
# Check Ollama is running
ollama list

# Should show llava:7b model
# If not, pull it:
ollama pull llava:7b
```

### 3. Database Initialized

```bash
cd database
python init_db.py
```

Should have 64 badges loaded.

### 4. Python Dependencies

```bash
pip install requests pillow
```

### 5. Test Images

Sample badge images should be in `tests/sample_badges/`:
- IMG_9605.jpeg
- IMG_9606.jpeg
- IMG_9607.jpeg

## Running Tests

### Run All Tests

```bash
# From project root
python tests/integration/run_all_tests.py
```

This runs both end-to-end and edge case tests, generating a comprehensive report.

### Run Specific Test Suites

```bash
# End-to-end tests only
python tests/integration/run_all_tests.py --e2e-only

# Edge case tests only
python tests/integration/run_all_tests.py --edge-only

# Quick mode (skips long tests)
python tests/integration/run_all_tests.py --quick
```

### Run Individual Test Files

```bash
# End-to-end workflow
python tests/integration/test_e2e_workflow.py

# Edge cases
python tests/integration/test_edge_cases.py
```

## Test Results

### Console Output

Tests provide real-time progress updates:

```
📋 Test 1: Backend Health Check
✅ PASS: Backend Health Check

📋 Test 2: Image Upload
   Uploading 1 image(s)...
✅ PASS: Image Upload

📋 Test 3: AI Processing Workflow
⏳ Waiting for scan 1 to complete processing...
   Status: processing (0/1 images)
   ETA: 102 seconds
   Status: completed (1/1 images)
✅ Processing completed in 103.5 seconds
✅ PASS: Start Processing
✅ PASS: Processing Completion
```

### JSON Reports

Test reports are saved to `tests/integration/reports/`:

```json
{
  "timestamp": "2025-11-08T22:45:00",
  "duration_seconds": 124.5,
  "test_suites": {
    "end_to_end": {
      "passed": true,
      "description": "Complete workflow from upload to inventory update"
    },
    "edge_cases": {
      "passed": true,
      "description": "Error handling and boundary conditions"
    }
  },
  "overall_result": "PASS",
  "environment": {
    "backend_url": "http://localhost:8000",
    "ollama_model": "llava:7b"
  }
}
```

## Expected Results

### Success Criteria

All tests should pass with the following outcomes:

✅ **Backend Health Check** - Returns 200 OK
✅ **Image Upload** - Returns scan_id
✅ **Processing Start** - Accepts scan_id, starts background task
✅ **Processing Completion** - Completes within timeout (10 minutes)
✅ **Results Retrieval** - Returns detections with confidence scores
✅ **Inventory Operations** - Stats, filtering, updates work correctly
✅ **Invalid Inputs** - Properly rejected with appropriate status codes
✅ **Concurrent Requests** - All succeed with unique IDs
✅ **Database Consistency** - State remains consistent

### Known Limitations

⚠️ **Processing Time**: Ollama llava:7b takes ~102 seconds per image
⚠️ **Accuracy**: Detection accuracy depends on image quality and badge visibility
⚠️ **Concurrency**: Very high concurrency may require connection pooling adjustments

## Troubleshooting

### Backend Not Responding

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
cd backend && uvicorn main:app --reload
```

### Ollama Not Responding

```bash
# Check Ollama service
ollama list

# Restart if needed (macOS/Linux)
pkill ollama
ollama serve

# Test Ollama
ollama run llava:7b "describe this" < tests/sample_badges/IMG_9605.jpeg
```

### Tests Timing Out

- Increase `PROCESSING_TIMEOUT` in test files (default: 600 seconds)
- Ensure Ollama is not overloaded
- Check system resources (CPU, RAM)

### Upload Failures

- Check file permissions on `data/uploads/` directory
- Ensure disk space available
- Verify sample images exist in `tests/sample_badges/`

### Database Errors

```bash
# Reinitialize database
cd database
rm scouts_inventory.db  # Warning: deletes all data
python init_db.py
```

## Test Architecture

### IntegrationTestClient

HTTP client with retry logic and convenient methods:

```python
from test_e2e_workflow import IntegrationTestClient

client = IntegrationTestClient()

# Upload images
scan_id = client.upload_images([Path("image.jpg")])

# Start processing
client.start_processing(scan_id)

# Wait for completion
client.wait_for_processing(scan_id)

# Get results
results = client.get_processing_results(scan_id)
```

### TestResults

Tracks test outcomes and generates summaries:

```python
from test_e2e_workflow import TestResults

results = TestResults()
results.add_result("Test Name", passed=True)
results.print_summary()
```

## Extending Tests

### Adding New Tests

1. Create test function in appropriate file:
```python
def test_new_feature(client: IntegrationTestClient, results: TestResults):
    """Test description."""
    print("\n📋 Test N: New Feature")

    # Test logic
    outcome = client.some_method()

    results.add_result(
        "New Feature Test",
        outcome is not None,
        "Details" if outcome else "Failed"
    )
```

2. Add to test runner in `run_all_tests.py` or run standalone

### Custom Test Configuration

Modify constants at top of test files:

```python
BASE_URL = "http://localhost:8000"  # API endpoint
API_TIMEOUT = 30  # HTTP timeout
PROCESSING_TIMEOUT = 600  # Max wait for Ollama
POLL_INTERVAL = 2  # Status check frequency
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install requests pillow

      - name: Start Ollama
        run: |
          curl -fsSL https://ollama.com/install.sh | sh
          ollama pull llava:7b

      - name: Initialize database
        run: python database/init_db.py

      - name: Start backend
        run: |
          cd backend
          uvicorn main:app &
          sleep 10

      - name: Run tests
        run: python tests/integration/run_all_tests.py
```

## Performance Benchmarks

### Expected Timings

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| Image Upload (1 file) | < 1s | Local filesystem |
| Image Upload (20 files) | 1-3s | Depends on file sizes |
| Processing Start | < 1s | Returns immediately |
| Ollama Detection (1 image) | 90-120s | llava:7b model |
| Results Retrieval | < 1s | Database query |
| Inventory Update | < 1s | Database transaction |
| Full E2E (1 image) | 2-5 min | Dominated by Ollama |

### Optimization Tips

- Use `llava:13b` for better accuracy (slower)
- Use smaller model for faster testing
- Process images in parallel (if multiple GPUs)
- Cache Ollama responses for repeated tests

## References

- **Backend API Docs**: See `backend/api/` for endpoint specifications
- **Ollama Docs**: https://ollama.com/
- **Test Images**: `tests/sample_badges/` contains real badge photos
- **ACTION_PLAN.md**: Complete project roadmap

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review test output and JSON reports
3. Verify prerequisites are met
4. Check backend logs for errors

---

**Last Updated**: 2025-11-08
**Test Suite Version**: 1.0.0
**Compatible with**: ACTION-400 Integration Testing
