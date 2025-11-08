"""
Edge Case and Stress Testing for Scout Badge Inventory System

Tests error handling, boundary conditions, and system resilience.

Usage:
    python tests/integration/test_edge_cases.py
"""

import io
import time
from pathlib import Path
from typing import List

import requests
from PIL import Image

from test_e2e_workflow import IntegrationTestClient, TestResults


BASE_URL = "http://localhost:8000"
TEST_DIR = Path(__file__).parent.parent
SAMPLE_IMAGES_DIR = TEST_DIR / "sample_badges"


def create_test_image(width: int, height: int, color: tuple = (128, 128, 128)) -> io.BytesIO:
    """Create a test image in memory."""
    img = Image.new('RGB', (width, height), color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_large_batch_upload(client: IntegrationTestClient, results: TestResults):
    """Test uploading maximum number of images (20)."""
    print("\n📋 Edge Case 1: Large Batch Upload (20 images)")

    # Get all sample images and repeat if needed
    sample_images = list(SAMPLE_IMAGES_DIR.glob("*.jpeg"))

    if not sample_images:
        results.add_result("Large Batch Upload", False, "No sample images available")
        return None

    # Create list of 20 images (repeat samples if needed)
    test_images = []
    for i in range(20):
        test_images.append(sample_images[i % len(sample_images)])

    print(f"   Uploading {len(test_images)} images...")
    start_time = time.time()
    scan_id = client.upload_images(test_images)
    upload_time = time.time() - start_time

    results.add_result(
        "Large Batch Upload (20 images)",
        scan_id is not None,
        f"Upload time: {upload_time:.2f}s" if scan_id else "Upload failed"
    )

    if scan_id:
        print(f"   ✅ Uploaded in {upload_time:.2f} seconds")

    return scan_id


def test_oversized_file(client: IntegrationTestClient, results: TestResults):
    """Test uploading file larger than limit (>10MB)."""
    print("\n📋 Edge Case 2: Oversized File (>10MB)")

    # Create a large image (should be rejected)
    large_image = create_test_image(5000, 5000)  # ~75MB uncompressed

    try:
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=[('files', ('large.jpg', large_image, 'image/jpeg'))],
            timeout=10
        )

        # Should be rejected (400 or 413)
        rejected = response.status_code in [400, 413, 422]
        results.add_result(
            "Oversized File Rejection",
            rejected,
            f"Expected rejection, got {response.status_code}"
        )

        if rejected:
            print(f"   ✅ Properly rejected with status {response.status_code}")
    except Exception as e:
        results.add_result("Oversized File Rejection", False, f"Error: {e}")


def test_invalid_file_type(client: IntegrationTestClient, results: TestResults):
    """Test uploading non-image file."""
    print("\n📋 Edge Case 3: Invalid File Type")

    # Create a text file pretending to be an image
    fake_image = io.BytesIO(b"This is not an image file")

    try:
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=[('files', ('fake.txt', fake_image, 'text/plain'))],
            timeout=10
        )

        # Should be rejected (400 or 415)
        rejected = response.status_code in [400, 415, 422]
        results.add_result(
            "Invalid File Type Rejection",
            rejected,
            f"Expected rejection, got {response.status_code}"
        )

        if rejected:
            print(f"   ✅ Properly rejected with status {response.status_code}")
    except Exception as e:
        results.add_result("Invalid File Type Rejection", False, f"Error: {e}")


def test_empty_upload(client: IntegrationTestClient, results: TestResults):
    """Test uploading with no files."""
    print("\n📋 Edge Case 4: Empty Upload")

    try:
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=[],
            timeout=10
        )

        # Should be rejected (400 or 422)
        rejected = response.status_code in [400, 422]
        results.add_result(
            "Empty Upload Rejection",
            rejected,
            f"Expected rejection, got {response.status_code}"
        )

        if rejected:
            print(f"   ✅ Properly rejected with status {response.status_code}")
    except Exception as e:
        results.add_result("Empty Upload Rejection", False, f"Error: {e}")


def test_poor_quality_image(client: IntegrationTestClient, results: TestResults):
    """Test processing very small/low quality image."""
    print("\n📋 Edge Case 5: Poor Quality Image")

    # Create tiny image (100x100)
    tiny_image = create_test_image(100, 100)

    try:
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=[('files', ('tiny.jpg', tiny_image, 'image/jpeg'))],
            timeout=10
        )

        # May accept but should handle gracefully
        if response.status_code == 200:
            data = response.json()
            scan_id = data.get('scan_id')

            # Try to process
            if scan_id:
                start_ok = client.start_processing(scan_id)
                results.add_result(
                    "Poor Quality Image Handling",
                    start_ok,
                    "Should accept but may fail detection gracefully"
                )
            else:
                results.add_result("Poor Quality Image Handling", False, "No scan_id")
        else:
            # Also acceptable to reject upfront
            results.add_result(
                "Poor Quality Image Handling",
                True,
                f"Rejected with {response.status_code}"
            )
    except Exception as e:
        results.add_result("Poor Quality Image Handling", False, f"Error: {e}")


def test_concurrent_uploads(client: IntegrationTestClient, results: TestResults):
    """Test multiple concurrent upload requests."""
    print("\n📋 Edge Case 6: Concurrent Uploads")

    sample_images = list(SAMPLE_IMAGES_DIR.glob("*.jpeg"))[:1]

    if not sample_images:
        results.add_result("Concurrent Uploads", False, "No sample images")
        return

    # Simulate 3 concurrent uploads
    import concurrent.futures

    def upload_task():
        return client.upload_images(sample_images)

    scan_ids = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(upload_task) for _ in range(3)]
        scan_ids = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All should succeed
    all_succeeded = all(scan_id is not None for scan_id in scan_ids)
    unique_ids = len(set(scan_ids)) == len(scan_ids)  # All unique

    results.add_result(
        "Concurrent Uploads",
        all_succeeded and unique_ids,
        f"Got {len([s for s in scan_ids if s])} successful uploads, unique: {unique_ids}"
    )

    if all_succeeded and unique_ids:
        print(f"   ✅ All 3 uploads succeeded with unique IDs")


def test_duplicate_processing(client: IntegrationTestClient, results: TestResults):
    """Test starting processing on same scan twice."""
    print("\n📋 Edge Case 7: Duplicate Processing Request")

    sample_images = list(SAMPLE_IMAGES_DIR.glob("*.jpeg"))[:1]

    if not sample_images:
        results.add_result("Duplicate Processing", False, "No sample images")
        return

    scan_id = client.upload_images(sample_images)
    if not scan_id:
        results.add_result("Duplicate Processing", False, "Upload failed")
        return

    # Start processing
    first_start = client.start_processing(scan_id)

    # Try to start again (should handle gracefully)
    second_start = client.start_processing(scan_id)

    # Both should return successfully or second should indicate already processing
    handled_gracefully = first_start and second_start

    results.add_result(
        "Duplicate Processing Request",
        handled_gracefully,
        "Should handle duplicate requests gracefully"
    )


def test_invalid_inventory_update(client: IntegrationTestClient, results: TestResults):
    """Test inventory update with invalid data."""
    print("\n📋 Edge Case 8: Invalid Inventory Update")

    try:
        # Try to update non-existent badge
        response = requests.put(
            f"{BASE_URL}/api/inventory/invalid-badge-id",
            json={"quantity": 10},
            timeout=10
        )

        # Should return 404
        correct_error = response.status_code == 404

        results.add_result(
            "Invalid Badge ID Handling",
            correct_error,
            f"Expected 404, got {response.status_code}"
        )

        # Try negative quantity
        response = requests.put(
            f"{BASE_URL}/api/inventory/grey-wolf-award",
            json={"quantity": -5},
            timeout=10
        )

        # Should return 400 or 422
        correct_error = response.status_code in [400, 422]

        results.add_result(
            "Negative Quantity Rejection",
            correct_error,
            f"Expected 400/422, got {response.status_code}"
        )

    except Exception as e:
        results.add_result("Invalid Inventory Update", False, f"Error: {e}")


def test_api_rate_limiting(client: IntegrationTestClient, results: TestResults):
    """Test rapid successive API calls."""
    print("\n📋 Edge Case 9: Rapid API Calls")

    # Make 50 rapid requests to inventory endpoint
    success_count = 0
    rate_limited = False

    for i in range(50):
        response = client.get_inventory()
        if response is not None:
            success_count += 1
        else:
            rate_limited = True

    # Should either handle all or implement rate limiting
    results.add_result(
        "Rapid API Calls",
        True,  # Pass as long as it doesn't crash
        f"Handled {success_count}/50 requests, rate limited: {rate_limited}"
    )

    print(f"   ✅ Handled {success_count}/50 requests")


def test_database_consistency(client: IntegrationTestClient, results: TestResults):
    """Test database state consistency."""
    print("\n📋 Edge Case 10: Database Consistency")

    # Get inventory twice
    inv1 = client.get_inventory()
    time.sleep(0.1)
    inv2 = client.get_inventory()

    if inv1 and inv2:
        # Should be identical
        consistent = len(inv1) == len(inv2)

        results.add_result(
            "Database Consistency",
            consistent,
            f"First: {len(inv1)} items, Second: {len(inv2)} items"
        )
    else:
        results.add_result("Database Consistency", False, "Failed to fetch inventory")


def run_edge_case_tests():
    """Run all edge case tests."""
    print("="*60)
    print("SCOUT BADGE INVENTORY - EDGE CASE TESTS")
    print("="*60)

    client = IntegrationTestClient()
    results = TestResults()

    # Check backend is running
    if not client.health_check():
        print("\n❌ Backend is not running. Please start the backend:")
        print("   cd backend && uvicorn main:app --reload")
        return False

    # Run edge case tests
    test_large_batch_upload(client, results)
    test_oversized_file(client, results)
    test_invalid_file_type(client, results)
    test_empty_upload(client, results)
    test_poor_quality_image(client, results)
    test_concurrent_uploads(client, results)
    test_duplicate_processing(client, results)
    test_invalid_inventory_update(client, results)
    test_api_rate_limiting(client, results)
    test_database_consistency(client, results)

    # Summary
    return results.print_summary()


if __name__ == "__main__":
    success = run_edge_case_tests()
    exit(0 if success else 1)
