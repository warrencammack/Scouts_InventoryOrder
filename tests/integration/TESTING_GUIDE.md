# Integration Testing Guide - ACTION-400

Complete guide for running integration tests on the Scout Badge Inventory System.

## Quick Start

```bash
# 1. Start backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# 2. In new terminal, run tests
cd Scouts_InventoryOrder
python tests/integration/run_all_tests.py
```

## Test Scenarios

### Scenario 1: New Installation Testing

**Goal**: Verify fresh installation works end-to-end

**Steps**:
1. Initialize database with badges
2. Start backend and Ollama
3. Run full test suite
4. Verify all tests pass

**Expected Outcome**: All systems operational, ready for production

**Command**:
```bash
python tests/integration/run_all_tests.py
```

### Scenario 2: Regression Testing

**Goal**: Verify changes haven't broken existing functionality

**Steps**:
1. Make code changes
2. Run test suite
3. Compare results with baseline

**Expected Outcome**: All previously passing tests still pass

**Command**:
```bash
python tests/integration/run_all_tests.py > test_output.txt
# Compare with previous test_output.txt
```

### Scenario 3: Performance Testing

**Goal**: Measure system performance under load

**Steps**:
1. Run large batch upload test
2. Measure processing time per image
3. Monitor system resources

**Expected Outcome**:
- Upload: < 3s for 20 images
- Processing: 90-120s per image
- Memory: Stable, no leaks

**Command**:
```bash
python tests/integration/test_edge_cases.py
# Monitor with: top, htop, or Activity Monitor
```

### Scenario 4: Error Recovery Testing

**Goal**: Verify system handles errors gracefully

**Steps**:
1. Run edge case tests
2. Verify proper error responses
3. Confirm system remains stable

**Expected Outcome**:
- Invalid inputs rejected with appropriate status codes
- No crashes or data corruption
- Clear error messages

**Command**:
```bash
python tests/integration/test_edge_cases.py
```

## Test Checklist

Before deploying or releasing, verify:

- [ ] Backend starts without errors
- [ ] Ollama responds to queries
- [ ] Database has 64 badges loaded
- [ ] All end-to-end tests pass
- [ ] All edge case tests pass
- [ ] Processing time is within expected range
- [ ] No memory leaks during extended runs
- [ ] Error messages are helpful
- [ ] Test report generated successfully

## Interpreting Results

### ✅ All Tests Pass

```
============================================================
TEST SUMMARY
============================================================
Total Tests: 16
Passed: 16
Failed: 0
============================================================
```

**Action**: System is ready for next phase

### ⚠️ Some Tests Fail

```
============================================================
TEST SUMMARY
============================================================
Total Tests: 16
Passed: 14
Failed: 2

FAILURES:
  - Processing Completion
    Processing did not complete
  - Results Retrieval
    Failed to retrieve results
============================================================
```

**Action**:
1. Check which tests failed
2. Review error messages
3. Check backend logs
4. Verify Ollama is running
5. Fix issues and re-run

### ❌ Cannot Connect to Backend

```
❌ Backend is not running. Please start the backend:
   cd backend && uvicorn main:app --reload
```

**Action**:
1. Start backend server
2. Verify it's on port 8000
3. Re-run tests

## Common Issues and Solutions

### Issue: Tests timeout during processing

**Symptoms**: Tests hang at "Waiting for processing..."

**Solutions**:
1. Check Ollama is running: `ollama list`
2. Test Ollama manually: `ollama run llava:7b "test"`
3. Increase timeout in test file
4. Check system resources (CPU, RAM)

### Issue: Upload fails with file size error

**Symptoms**: "File too large" error

**Solutions**:
1. Check sample image sizes: `ls -lh tests/sample_badges/`
2. Reduce image sizes if > 10MB
3. Verify upload limit in backend config

### Issue: Database errors

**Symptoms**: "Badge not found" or "No badges in database"

**Solutions**:
```bash
cd database
python init_db.py
# Verify: sqlite3 scouts_inventory.db "SELECT COUNT(*) FROM badges;"
```

### Issue: Concurrent test failures

**Symptoms**: Tests pass individually but fail when run together

**Solutions**:
1. Check for database locking issues
2. Ensure proper cleanup between tests
3. Run tests sequentially instead of parallel

### Issue: Inconsistent results

**Symptoms**: Tests pass sometimes, fail other times

**Solutions**:
1. Check Ollama response consistency
2. Verify network stability
3. Monitor system resource usage
4. Add delays between tests if needed

## Advanced Testing

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Upload image
curl -X POST http://localhost:8000/api/upload \
  -F "files=@tests/sample_badges/IMG_9605.jpeg"

# Get inventory
curl http://localhost:8000/api/inventory

# Get stats
curl http://localhost:8000/api/inventory/stats
```

### Testing with Different Models

Modify test files to use different Ollama models:

```python
# In test files, update:
OLLAMA_MODEL = "llava:13b"  # Slower but more accurate
# or
OLLAMA_MODEL = "llava:7b"   # Faster but less accurate
```

### Load Testing

For stress testing, use tools like Apache Bench:

```bash
# Test upload endpoint
ab -n 100 -c 10 -p image.jpg -T image/jpeg \
  http://localhost:8000/api/upload
```

### Memory Profiling

```bash
# Install memory_profiler
pip install memory_profiler

# Profile test
python -m memory_profiler tests/integration/test_e2e_workflow.py
```

## Continuous Integration

### Pre-commit Testing

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running integration tests..."
python tests/integration/run_all_tests.py --quick
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### Automated Nightly Tests

Schedule full test suite to run nightly:

```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/project && python tests/integration/run_all_tests.py > nightly_test.log 2>&1
```

## Test Metrics

### Coverage Goals

- **API Endpoints**: 100% (all endpoints tested)
- **Workflows**: 100% (upload → process → inventory)
- **Error Cases**: 90%+ (common errors handled)
- **Edge Cases**: 80%+ (boundary conditions tested)

### Performance Goals

| Metric | Target | Current |
|--------|--------|---------|
| Upload (1 img) | < 1s | ~0.5s |
| Upload (20 imgs) | < 3s | ~2s |
| Processing (1 img) | 90-120s | ~102s |
| Inventory Query | < 100ms | ~50ms |
| Database Write | < 100ms | ~30ms |

## Best Practices

1. **Run tests before committing**: Catch issues early
2. **Keep test images realistic**: Use actual badge photos
3. **Monitor Ollama performance**: Processing time can vary
4. **Clean up test data**: Don't pollute production database
5. **Document failures**: Record unexpected behaviors
6. **Update tests with code**: Keep tests in sync with features
7. **Review reports**: Check JSON reports for trends

## Next Steps After Testing

Once all tests pass:

1. **ACTION-401**: Performance Optimization
2. **ACTION-402**: User Documentation
3. **ACTION-403**: Developer Documentation
4. **ACTION-500**: Deployment Preparation

## Resources

- **Test Files**: `tests/integration/`
- **Sample Data**: `tests/sample_badges/`
- **Backend Logs**: Check uvicorn output
- **Ollama Logs**: Check ollama service logs
- **Test Reports**: `tests/integration/reports/`

---

**Document Version**: 1.0
**Last Updated**: 2025-11-08
**Related**: ACTION-400 Integration Testing
