
"""
Badge Image Downloader Script

This script reads the `badge_images_metadata.json` file, downloads the badge images
from the specified URLs, and saves them to the `data/badges` directory.

Usage:
    python scripts/download_badge_images.py
"""


import json
import sys
from pathlib import Path
import requests
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import BadgeConfig

def download_image(url: str, dest_path: Path, timeout: int = 10) -> bool:
    """
    Download an image from a URL and save it to a destination path.

    Args:
        url: The URL of the image to download.
        dest_path: The path to save the image to.
        timeout: The timeout for the request in seconds.

    Returns:
        True if the download was successful, False otherwise.
    """
    try:
        # Ensure the destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Some URLs might be for product pages, not direct image links.
        # This is a best-effort attempt to download.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"  Downloading from: {url}")
        response = requests.get(url, stream=True, timeout=timeout, headers=headers)
        response.raise_for_status()

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"  ❌ An unexpected error occurred: {e}")
        return False

def main():
    """Main function to download badge images."""
    print("=" * 60)
    print("Scout Badge Image Downloader")
    print("=" * 60)

    metadata_path = BadgeConfig.BADGE_METADATA_FILE
    if not metadata_path.exists():
        print(f"❌ Error: Metadata file not found at {metadata_path}")
        sys.exit(1)

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    images_to_download = metadata.get("images", [])
    total_images = len(images_to_download)
    
    if total_images == 0:
        print("No images found in metadata file.")
        sys.exit(0)

    print(f"Found {total_images} images to potentially download.")
    print("Note: Some URLs may require a Scout Member login and might fail.")
    print("-" * 60)

    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, image_info in enumerate(images_to_download):
        badge_id = image_info.get("badge_id")
        image_url = image_info.get("image_source_url")
        image_path_str = image_info.get("image_path")

        print(f"Processing {i+1}/{total_images}: {badge_id}")

        if not all([badge_id, image_url, image_path_str]):
            print("  ⏩ Skipping due to missing info.")
            skip_count += 1
            continue

        image_path = project_root / image_path_str

        if image_path.exists():
            print("  ⏩ Image already exists. Skipping.")
            skip_count += 1
            success_count += 1 # Count existing as success
            continue

        if download_image(image_url, image_path):
            print(f"  ✅ Successfully downloaded and saved to {image_path_str}")
            success_count += 1
        else:
            print(f"  ❌ Failed to download badge: {badge_id}")
            fail_count += 1
        
        # Be respectful to the server
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print(f"  - ✅ Successful (including existing): {success_count}")
    print(f"  - ❌ Failed: {fail_count}")
    print(f"  - ⏩ Skipped: {skip_count}")
    print("-" * 60)

    if fail_count > 0:
        print("Some images failed to download. This might be due to:")
        print("  - Needing a scoutshop.com.au member login.")
        print("  - The URL being a product page, not a direct image link.")
        print("  - The URL being incorrect or outdated.")
        print("\nYou may need to download these images manually.")

if __name__ == "__main__":
    # Check for requests library
    try:
        import requests
    except ImportError:
        print("="*60)
        print("❌ Error: The 'requests' library is not installed.")
        print("Please install it by running:")
        print("  pip install requests")
        print("If you are using the backend virtual environment, activate it first:")
        print("  source backend/venv/bin/activate")
        print("  pip install requests")
        print("="*60)
        sys.exit(1)
        
    main()
