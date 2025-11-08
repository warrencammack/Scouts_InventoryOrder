#!/usr/bin/env python3
"""
Master Test Runner for Scout Badge Inventory System

Runs all integration tests and generates a comprehensive report.

Usage:
    # Start backend first
    cd backend && uvicorn main:app --reload

    # In another terminal, run tests
    python tests/integration/run_all_tests.py

    # Or with options
    python tests/integration/run_all_tests.py --quick  # Skip long tests
    python tests/integration/run_all_tests.py --verbose  # More output
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from test_e2e_workflow import run_integration_tests
from test_edge_cases import run_edge_case_tests


def generate_test_report(
    e2e_passed: bool,
    edge_passed: bool,
    start_time: float,
    output_file: Path
):
    """Generate JSON test report."""
    duration = time.time() - start_time

    report = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": round(duration, 2),
        "test_suites": {
            "end_to_end": {
                "passed": e2e_passed,
                "description": "Complete workflow from upload to inventory update"
            },
            "edge_cases": {
                "passed": edge_passed,
                "description": "Error handling and boundary conditions"
            }
        },
        "overall_result": "PASS" if (e2e_passed and edge_passed) else "FAIL",
        "environment": {
            "backend_url": "http://localhost:8000",
            "ollama_model": "llava:7b"
        }
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Test report saved to: {output_file}")


def main():
    """Run all integration tests."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for Scout Badge Inventory"
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Skip long-running tests'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--e2e-only',
        action='store_true',
        help='Run only end-to-end tests'
    )
    parser.add_argument(
        '--edge-only',
        action='store_true',
        help='Run only edge case tests'
    )

    args = parser.parse_args()

    print("="*70)
    print(" "*15 + "SCOUT BADGE INVENTORY")
    print(" "*15 + "INTEGRATION TEST SUITE")
    print("="*70)
    print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Quick mode: {'ON' if args.quick else 'OFF'}")
    print()

    start_time = time.time()

    # Run test suites
    e2e_passed = True
    edge_passed = True

    if not args.edge_only:
        print("\n" + "▶"*35)
        print("RUNNING END-TO-END TESTS")
        print("▶"*35)
        e2e_passed = run_integration_tests()

    if not args.e2e_only:
        print("\n" + "▶"*35)
        print("RUNNING EDGE CASE TESTS")
        print("▶"*35)
        edge_passed = run_edge_case_tests()

    # Generate report
    duration = time.time() - start_time

    print("\n" + "="*70)
    print(" "*25 + "FINAL RESULTS")
    print("="*70)
    print(f"\nEnd-to-End Tests: {'✅ PASS' if e2e_passed else '❌ FAIL'}")
    print(f"Edge Case Tests:  {'✅ PASS' if edge_passed else '❌ FAIL'}")
    print(f"\nTotal Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    overall_pass = e2e_passed and edge_passed

    if overall_pass:
        print("\n" + "🎉 "*15)
        print(" "*20 + "ALL TESTS PASSED!")
        print("🎉 "*15 + "\n")
    else:
        print("\n" + "⚠️ "*15)
        print(" "*20 + "SOME TESTS FAILED")
        print("⚠️ "*15 + "\n")

    # Save report
    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    generate_test_report(e2e_passed, edge_passed, start_time, report_file)

    print("="*70)

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
