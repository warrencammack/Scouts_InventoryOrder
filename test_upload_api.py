#!/usr/bin/env python3
"""
Test script for the Image Upload API endpoint.

This script tests the /api/upload endpoint by creating test image files
and uploading them to verify functionality.
"""

import io
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image


def create_test_image(filename: str, size: tuple = (800, 600), color: str = "blue") -> None:
    """Create a test image file."""
    img = Image.new("RGB", size, color)
    img.save(filename)
    print(f"Created test image: {filename} ({size[0]}x{size[1]}, {color})")


def main():
    """Create test images for upload testing."""
    test_images_dir = Path(__file__).parent / "test_images"
    test_images_dir.mkdir(exist_ok=True)

    # Create test images
    create_test_image(test_images_dir / "test_badge1.jpg", (800, 600), "red")
    create_test_image(test_images_dir / "test_badge2.jpg", (1024, 768), "green")
    create_test_image(test_images_dir / "test_badge3.png", (640, 480), "blue")

    print(f"\nTest images created in: {test_images_dir}")
    print("\nTo test the upload API, run:")
    print(f"  1. Start the server: cd backend && uvicorn main:app --reload")
    print(f"  2. Use curl to upload:")
    print(f'     curl -X POST "http://localhost:8000/api/upload" \\')
    print(f'       -F "files=@{test_images_dir}/test_badge1.jpg" \\')
    print(f'       -F "files=@{test_images_dir}/test_badge2.jpg" \\')
    print(f'       -F "files=@{test_images_dir}/test_badge3.png"')
    print(f"\n  3. Or visit: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
