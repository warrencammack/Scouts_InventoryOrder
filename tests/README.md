# Tests Directory

This directory contains test scripts and test data for the Scout Badge Inventory application.

## Test Files

### test_ollama_vision.py
Comprehensive test script for Ollama vision model badge recognition.

**Features:**
- Tests 5 different prompt strategies
- Supports multiple images
- Measures response time and accuracy
- Generates JSON results file

**Usage:**
```bash
# Quick test with first image
python tests/test_ollama_vision.py --quick

# Full comprehensive test (all images, all prompts)
python tests/test_ollama_vision.py
```

**Requirements:**
- Python 3.10+
- ollama package (`pip install ollama`)
- Ollama running with llava:7b model

## Test Data

### sample_badges/
Contains real-world Scout badge inventory photos for testing.

**Images:**
- **IMG_9605.jpeg** (2.3 MB) - Mixed badges in storage containers
- **IMG_9606.jpeg** (2.3 MB) - Organized storage with multiple badge types
- **IMG_9607.jpeg** (2.2 MB) - OAS badges organized by levels

## Test Results

### ollama_test_results.md
Comprehensive analysis of Ollama badge recognition testing including:
- Test methodology
- Results and findings
- Accuracy assessment
- Recommendations for production use
- Next steps

**Key Findings:**
- ✅ llava:7b successfully identifies Scout badge categories
- ✅ Response time: ~102 seconds per image
- ✅ Works well with context-rich prompts
- ✅ Suitable for inventory management with manual review workflow

### ollama_test_results.json
Machine-readable test results (generated when running full test suite).

## Adding More Tests

To add additional test images:
1. Place images in `tests/sample_badges/`
2. Supported formats: JPEG, JPG, PNG
3. Run test script to evaluate

## Test Strategy

The test suite evaluates:
1. **Badge Category Recognition** - Can it identify OAS, SIA, Milestone badges?
2. **Counting Accuracy** - How accurately can it count badges?
3. **Detail Recognition** - Can it identify specific badge features?
4. **Response Time** - How fast is the processing?
5. **Prompt Effectiveness** - Which prompts work best?

## Integration Tests

### integration/
Complete end-to-end and edge case testing suite (ACTION-400).

**Test Suites:**
- **test_e2e_workflow.py** - Complete workflow from upload to inventory update
- **test_edge_cases.py** - Error handling, boundary conditions, stress tests
- **run_all_tests.py** - Master test runner with comprehensive reporting

**Features:**
- ✅ End-to-end workflow validation
- ✅ Error handling and edge cases
- ✅ Concurrent request testing
- ✅ Performance benchmarking
- ✅ Automated test reports (JSON)

**Quick Start:**
```bash
# Start backend first
cd backend && uvicorn main:app --reload

# Run all integration tests
python tests/integration/run_all_tests.py

# See integration/README.md for full documentation
```

**Documentation:**
- **integration/README.md** - Complete test documentation
- **integration/TESTING_GUIDE.md** - Testing scenarios and best practices

## Next Steps

- [x] ~~Run full comprehensive test suite~~ (ACTION-103 completed)
- [x] ~~Test with additional badge images~~ (3 real-world images tested)
- [x] ~~Implement automated accuracy metrics~~ (ACTION-400 completed)
- [ ] Test llava:13b model for accuracy comparison
- [ ] Create ground truth dataset for validation
- [ ] Run performance optimization tests (ACTION-401)
