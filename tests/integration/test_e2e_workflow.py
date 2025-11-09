"""
End-to-End Integration Test for Scout Badge Inventory System

Tests the complete workflow from image upload through processing to inventory update.

Requirements:
    - Backend server running on localhost:8000
    - Ollama running with llava:7b model
    - Database initialized with badge data

Usage:
    # Start backend first
    cd backend && uvicorn main:app --reload

    # Run tests
    python tests/integration/test_e2e_workflow.py

    # Or run with pytest
    pytest tests/integration/test_e2e_workflow.py -v
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configuration
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30  # seconds
PROCESSING_TIMEOUT = 600  # 10 minutes for Ollama processing
POLL_INTERVAL = 2  # seconds

# Test data paths
TEST_DIR = Path(__file__).parent.parent
SAMPLE_IMAGES_DIR = TEST_DIR / "sample_badges"


class IntegrationTestClient:
    """HTTP client for integration testing with retry logic."""

    def __init__(self, base_url: str = BASE_URL, timeout: int = API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def health_check(self) -> bool:
        """Check if backend is running."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

    def upload_images(self, image_paths: List[Path]) -> Optional[int]:
        """Upload images and return scan_id."""
        files = []
        try:
            for path in image_paths:
                files.append(
                    ('files', (path.name, open(path, 'rb'), 'image/jpeg'))
                )

            response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files,
                timeout=self.timeout
            )

            if response.status_code in [200, 201]:  # Accept both 200 OK and 201 Created
                data = response.json()
                return data.get('scan_id')
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()

    def start_processing(self, scan_id: int) -> bool:
        """Start processing a scan."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/process/{scan_id}",
                timeout=self.timeout
            )
            return response.status_code in [200, 202]  # Accept 200 OK and 202 Accepted
        except Exception as e:
            print(f"❌ Processing start failed: {e}")
            return False

    def get_processing_status(self, scan_id: int) -> Optional[Dict[str, Any]]:
        """Get processing status."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/process/{scan_id}/status",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return None

    def get_processing_results(self, scan_id: int) -> Optional[Dict[str, Any]]:
        """Get processing results."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/process/{scan_id}/results",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Results fetch failed: {e}")
            return None

    def get_inventory(self, **filters) -> Optional[List[Dict[str, Any]]]:
        """Get inventory with optional filters."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/inventory",
                params=filters,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                # API returns {items: [...], total_items: N, ...}, extract items array
                return data.get('items', []) if isinstance(data, dict) else data
            return None
        except Exception as e:
            print(f"❌ Inventory fetch failed: {e}")
            return None

    def update_inventory_from_scan(
        self,
        scan_id: int,
        badge_updates: Dict[str, int],
        preview: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update inventory from scan results."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/inventory/update-from-scan/{scan_id}",
                json={
                    "badge_updates": badge_updates,
                    "preview": preview
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Inventory update failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Inventory update error: {e}")
            return None

    def get_inventory_stats(self) -> Optional[Dict[str, Any]]:
        """Get inventory statistics."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/inventory/stats",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Stats fetch failed: {e}")
            return None

    def wait_for_processing(
        self,
        scan_id: int,
        timeout: int = PROCESSING_TIMEOUT,
        poll_interval: int = POLL_INTERVAL
    ) -> bool:
        """Wait for processing to complete, polling for status."""
        print(f"⏳ Waiting for scan {scan_id} to complete processing...")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            status_data = self.get_processing_status(scan_id)

            if status_data:
                status = status_data.get('status')
                processed = status_data.get('processed_images', 0)
                total = status_data.get('total_images', 0)
                eta_seconds = status_data.get('estimated_time_remaining_seconds', 0)

                # Print status update if changed
                if status != last_status:
                    print(f"   Status: {status} ({processed}/{total} images)")
                    if eta_seconds:
                        print(f"   ETA: {eta_seconds:.0f} seconds")
                    last_status = status

                # Check completion
                if status == 'completed':
                    elapsed = time.time() - start_time
                    print(f"✅ Processing completed in {elapsed:.1f} seconds")
                    return True
                elif status == 'failed':
                    print(f"❌ Processing failed")
                    return False

            time.sleep(poll_interval)

        print(f"❌ Processing timeout after {timeout} seconds")
        return False


class TestResults:
    """Track test results."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def add_result(self, test_name: str, passed: bool, message: str = ""):
        """Record a test result."""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ PASS: {test_name}")
        else:
            self.tests_failed += 1
            self.failures.append((test_name, message))
            print(f"❌ FAIL: {test_name}")
            if message:
                print(f"   {message}")

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")

        if self.failures:
            print("\nFAILURES:")
            for test_name, message in self.failures:
                print(f"  - {test_name}")
                if message:
                    print(f"    {message}")

        print("="*60)

        return self.tests_failed == 0


def test_backend_health(client: IntegrationTestClient, results: TestResults):
    """Test 1: Backend health check."""
    print("\n📋 Test 1: Backend Health Check")
    is_healthy = client.health_check()
    results.add_result(
        "Backend Health Check",
        is_healthy,
        "Backend is not responding" if not is_healthy else ""
    )
    return is_healthy


def test_image_upload(client: IntegrationTestClient, results: TestResults) -> Optional[int]:
    """Test 2: Image upload workflow."""
    print("\n📋 Test 2: Image Upload")

    # Get sample images
    sample_images = list(SAMPLE_IMAGES_DIR.glob("*.jpeg"))[:1]  # Start with 1 image

    if not sample_images:
        results.add_result("Image Upload", False, "No sample images found")
        return None

    print(f"   Uploading {len(sample_images)} image(s)...")
    scan_id = client.upload_images(sample_images)

    results.add_result(
        "Image Upload",
        scan_id is not None,
        f"Upload returned scan_id: {scan_id}" if scan_id else "Upload failed"
    )

    return scan_id


def test_processing_workflow(
    client: IntegrationTestClient,
    results: TestResults,
    scan_id: int
) -> bool:
    """Test 3: AI processing workflow."""
    print("\n📋 Test 3: AI Processing Workflow")

    # Start processing
    started = client.start_processing(scan_id)
    if not started:
        results.add_result("Start Processing", False, "Failed to start processing")
        return False

    results.add_result("Start Processing", True)

    # Wait for completion
    completed = client.wait_for_processing(scan_id)
    results.add_result(
        "Processing Completion",
        completed,
        "Processing did not complete" if not completed else ""
    )

    return completed


def test_results_retrieval(
    client: IntegrationTestClient,
    results: TestResults,
    scan_id: int
) -> Optional[Dict[str, Any]]:
    """Test 4: Results retrieval."""
    print("\n📋 Test 4: Results Retrieval")

    processing_results = client.get_processing_results(scan_id)

    if processing_results:
        # Validate result structure (API returns 'results' array, not 'detections')
        has_results = 'results' in processing_results
        has_summary = 'summary' in processing_results

        results.add_result(
            "Results Structure",
            has_results and has_summary,
            f"Results: {has_results}, Summary: {has_summary}"
        )

        # Print summary
        if has_summary:
            summary = processing_results['summary']
            print(f"   Total badges detected: {summary.get('total_badges', 0)}")
            print(f"   Unique badge types: {summary.get('unique_badges', 0)}")
            print(f"   High confidence: {summary.get('high_confidence_count', 0)}")
    else:
        results.add_result("Results Retrieval", False, "Failed to retrieve results")

    return processing_results


def test_inventory_operations(
    client: IntegrationTestClient,
    results: TestResults,
    scan_id: int,
    processing_results: Dict[str, Any]
):
    """Test 5: Inventory operations."""
    print("\n📋 Test 5: Inventory Operations")

    # Get initial inventory - stats endpoint may not be implemented yet
    inventory_list = client.get_inventory()
    results.add_result(
        "Get Inventory",
        inventory_list is not None,
        "Failed to retrieve inventory" if not inventory_list else ""
    )

    if not inventory_list:
        return

    initial_stats = {'total_badge_types': len(inventory_list), 'total_quantity': sum(item.get('quantity', 0) for item in inventory_list)}

    print(f"   Initial inventory: {initial_stats.get('total_badge_types', 0)} types, "
          f"{initial_stats.get('total_quantity', 0)} badges")

    # Preview inventory update - extract detections from results array
    all_detections = []
    for result in processing_results.get('results', []):
        all_detections.extend(result.get('detections', []))

    if all_detections:
        # Create badge updates from detections
        badge_updates = {}
        for detection in all_detections:
            badge_id = detection.get('badge_id')
            quantity = detection.get('quantity', 1)
            if badge_id:
                badge_updates[badge_id] = badge_updates.get(badge_id, 0) + quantity

        print(f"   Badge updates to apply: {len(badge_updates)} unique badges")

        # Preview update
        preview_result = client.update_inventory_from_scan(
            scan_id,
            badge_updates,
            preview=True
        )

        results.add_result(
            "Inventory Update Preview",
            preview_result is not None,
            "Preview failed" if not preview_result else ""
        )

        # Actually update (optional - comment out to avoid modifying inventory)
        # update_result = client.update_inventory_from_scan(
        #     scan_id,
        #     badge_updates,
        #     preview=False
        # )
        # results.add_result(
        #     "Inventory Update Apply",
        #     update_result is not None
        # )


def test_edge_cases(client: IntegrationTestClient, results: TestResults):
    """Test 6: Edge cases and error handling."""
    print("\n📋 Test 6: Edge Cases")

    # Test invalid scan_id
    invalid_results = client.get_processing_results(999999)
    results.add_result(
        "Invalid Scan ID Handling",
        invalid_results is None,  # Should return None or error
        "Should return None for invalid scan_id"
    )

    # Test inventory filtering
    low_stock = client.get_inventory(low_stock_only=True)
    results.add_result(
        "Low Stock Filter",
        low_stock is not None,
        "Failed to filter low stock items" if low_stock is None else ""
    )

    if low_stock is not None:
        print(f"   Low stock items: {len(low_stock)}")

    # Test category filtering
    oas_badges = client.get_inventory(category="OAS")
    results.add_result(
        "Category Filter",
        oas_badges is not None,
        "Failed to filter by category" if oas_badges is None else ""
    )

    if oas_badges is not None:
        print(f"   OAS badges: {len(oas_badges)}")


def run_integration_tests():
    """Run all integration tests."""
    print("="*60)
    print("SCOUT BADGE INVENTORY - INTEGRATION TESTS")
    print("="*60)

    # Initialize
    client = IntegrationTestClient()
    results = TestResults()

    # Test 1: Health check
    if not test_backend_health(client, results):
        print("\n❌ Backend is not running. Please start the backend:")
        print("   cd backend && uvicorn main:app --reload")
        return False

    # Test 2: Upload
    scan_id = test_image_upload(client, results)
    if not scan_id:
        print("\n❌ Cannot proceed without successful upload")
        results.print_summary()
        return False

    # Test 3: Processing
    processing_completed = test_processing_workflow(client, results, scan_id)
    if not processing_completed:
        print("\n❌ Processing failed or timed out")
        results.print_summary()
        return False

    # Test 4: Results
    processing_results = test_results_retrieval(client, results, scan_id)

    # Test 5: Inventory
    if processing_results:
        test_inventory_operations(client, results, scan_id, processing_results)

    # Test 6: Edge cases
    test_edge_cases(client, results)

    # Summary
    return results.print_summary()


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
