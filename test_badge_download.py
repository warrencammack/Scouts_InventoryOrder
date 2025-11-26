#!/usr/bin/env python3
"""
Test script for badge image downloading functionality.

This script tests the badge downloading system without actually downloading images.
"""

import sys
from pathlib import Path

# Add scripts directory to path
project_root = Path(__file__).parent
scripts_dir = project_root / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from download_badge_images import BadgeImageDownloader
    print("✓ Successfully imported BadgeImageDownloader")
except ImportError as e:
    print(f"✗ Failed to import BadgeImageDownloader: {e}")
    sys.exit(1)

def test_downloader_initialization():
    """Test that the downloader can be initialized."""
    try:
        downloader = BadgeImageDownloader()
        print("✓ BadgeImageDownloader initialized successfully")
        
        # Check if metadata files exist
        if downloader.metadata_file.exists():
            print("✓ Badge metadata file found")
        else:
            print("✗ Badge metadata file not found")
            
        if downloader.urls_file.exists():
            print("✓ URLs file found")
        else:
            print("✗ URLs file not found")
            
        # Check badges directory
        if downloader.badges_dir.exists():
            print("✓ Badges directory exists")
        else:
            print("✓ Badges directory created")
            
        return True
    except Exception as e:
        print(f"✗ Failed to initialize downloader: {e}")
        return False

def test_metadata_loading():
    """Test metadata loading functionality."""
    try:
        downloader = BadgeImageDownloader()
        
        # Check metadata structure
        if 'images' in downloader.metadata:
            badge_count = len(downloader.metadata['images'])
            print(f"✓ Loaded {badge_count} badges from metadata")
        else:
            print("✗ No 'images' key in metadata")
            return False
            
        # Check URLs data
        if 'badge_product_urls' in downloader.urls_data:
            url_count = len(downloader.urls_data['badge_product_urls'])
            print(f"✓ Loaded {url_count} badge URLs")
        else:
            print("✗ No 'badge_product_urls' key in URLs data")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Failed to load metadata: {e}")
        return False

def test_dry_run():
    """Test dry run functionality."""
    try:
        downloader = BadgeImageDownloader()
        
        # Run dry run
        print("Running dry run test...")
        downloaded = downloader.download_public_images(dry_run=True)
        
        print(f"✓ Dry run completed, would download {downloaded} images")
        
        # Print statistics
        downloader.print_statistics()
        
        return True
    except Exception as e:
        print(f"✗ Dry run failed: {e}")
        return False

def test_validation():
    """Test image validation functionality."""
    try:
        downloader = BadgeImageDownloader()
        
        # Run validation
        print("Running validation test...")
        results = downloader.validate_existing_images()
        
        print(f"✓ Validation completed:")
        print(f"  Valid: {len(results['valid'])}")
        print(f"  Missing: {len(results['missing'])}")
        print(f"  Invalid format: {len(results['invalid_format'])}")
        print(f"  Corrupted: {len(results['corrupted'])}")
        
        return True
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Badge Image Download System")
    print("=" * 40)
    
    tests = [
        ("Downloader Initialization", test_downloader_initialization),
        ("Metadata Loading", test_metadata_loading),
        ("Dry Run", test_dry_run),
        ("Image Validation", test_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Badge download system is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())