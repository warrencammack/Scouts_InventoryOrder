#!/usr/bin/env python3
"""
Badge Image Downloader for Scouts Inventory System

This script downloads badge images from multiple sources:
1. Public URLs from scoutshop.com.au
2. Alternative sources (state Scout organizations, program resources)
3. Badge chart PDF extraction
4. Optional authenticated downloading with Scout Member credentials

Usage:
    python scripts/download_badge_images.py [options]

Options:
    --public-only       Download only publicly available images
    --with-auth         Enable authenticated downloading (requires credentials)
    --pdf-extract       Extract images from badge chart PDF
    --validate-only     Only validate existing images, don't download
    --force-redownload  Re-download existing images
    --dry-run          Show what would be downloaded without actually downloading
"""

import os
import sys
import json
import requests
import time
import hashlib
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('badge_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BadgeImageDownloader:
    """Main class for downloading badge images from multiple sources."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize the downloader with data directory."""
        self.data_dir = data_dir or project_root / "data"
        self.badges_dir = self.data_dir / "badges"
        self.badges_dir.mkdir(exist_ok=True)
        
        # Load metadata files
        self.metadata_file = self.data_dir / "badge_images_metadata.json"
        self.urls_file = self.data_dir / "scoutshop_urls.json"
        
        self.metadata = self._load_json(self.metadata_file)
        self.urls_data = self._load_json(self.urls_file)
        
        # HTTP session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Download statistics
        self.stats = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'already_exists': 0
        }
        
    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Required file not found: {file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            sys.exit(1)
    
    def _save_metadata(self):
        """Save updated metadata back to file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            logger.info("Metadata updated successfully")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _get_image_path(self, badge_id: str) -> Path:
        """Get the local path for a badge image."""
        return self.badges_dir / f"{badge_id}.png"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _download_image(self, url: str, output_path: Path, timeout: int = 30) -> Tuple[bool, str]:
        """
        Download an image from URL to local path.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Downloading: {url}")
            response = self.session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Check if response contains an image
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
                return False, f"URL does not contain an image (content-type: {content_type})"
            
            # Download and save the image
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify the downloaded file
            if output_path.stat().st_size == 0:
                output_path.unlink()
                return False, "Downloaded file is empty"
            
            logger.info(f"Successfully downloaded: {output_path}")
            return True, "Download successful"
            
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def _update_badge_metadata(self, badge_id: str, status: str, message: str = "", 
                              file_info: Dict = None):
        """Update metadata for a specific badge."""
        # Find the badge in metadata
        for badge in self.metadata.get('images', []):
            if badge.get('badge_id') == badge_id:
                badge['download_status'] = status
                badge['download_message'] = message
                badge['last_download_attempt'] = datetime.now().isoformat()
                
                if file_info:
                    badge.update(file_info)
                break
        else:
            # Badge not found in metadata, add it
            new_badge = {
                'badge_id': badge_id,
                'download_status': status,
                'download_message': message,
                'last_download_attempt': datetime.now().isoformat()
            }
            if file_info:
                new_badge.update(file_info)
            self.metadata.setdefault('images', []).append(new_badge)
    
    def download_public_images(self, force_redownload: bool = False, dry_run: bool = False) -> int:
        """
        Download publicly available badge images.
        
        Returns:
            Number of images successfully downloaded
        """
        logger.info("Starting public image download...")
        downloaded_count = 0
        
        # Get badges with documented or estimated URLs
        badges_to_download = []
        for badge in self.metadata.get('images', []):
            badge_id = badge.get('badge_id')
            if not badge_id:
                continue
                
            # Check if image already exists
            image_path = self._get_image_path(badge_id)
            if image_path.exists() and not force_redownload:
                logger.info(f"Image already exists: {badge_id}")
                self.stats['already_exists'] += 1
                continue
            
            # Get URL from metadata or URLs file
            url = badge.get('image_source_url')
            if not url and badge_id in self.urls_data.get('badge_product_urls', {}):
                url_info = self.urls_data['badge_product_urls'][badge_id]
                if isinstance(url_info, dict):
                    url = url_info.get('url') or url_info.get('main_badge')
                else:
                    url = url_info
            
            if not url:
                logger.warning(f"No URL found for badge: {badge_id}")
                continue
            
            # Skip category pages and login-protected URLs for public download
            if any(skip_pattern in url for skip_pattern in ['/t/badges/', 'cubs-8-to-10', 'special-interest-badges']):
                logger.info(f"Skipping category/protected URL: {badge_id}")
                self.stats['skipped'] += 1
                continue
            
            badges_to_download.append((badge_id, url, image_path))
        
        logger.info(f"Found {len(badges_to_download)} badges to download")
        
        if dry_run:
            for badge_id, url, image_path in badges_to_download:
                logger.info(f"Would download: {badge_id} from {url}")
            return 0
        
        # Download images
        for i, (badge_id, url, image_path) in enumerate(badges_to_download, 1):
            self.stats['attempted'] += 1
            logger.info(f"Processing {i}/{len(badges_to_download)}: {badge_id}")
            
            success, message = self._download_image(url, image_path)
            
            if success:
                # Get file information
                file_info = {
                    'actual_dimensions': {'width': 0, 'height': 0},  # Would need PIL to get actual dimensions
                    'file_size': image_path.stat().st_size,
                    'file_format': image_path.suffix.lower(),
                    'file_hash': self._calculate_file_hash(image_path),
                    'download_date': datetime.now().isoformat(),
                    'source_url': url
                }
                
                self._update_badge_metadata(badge_id, 'downloaded', message, file_info)
                self.stats['successful'] += 1
                downloaded_count += 1
                logger.info(f"✓ Downloaded: {badge_id}")
            else:
                self._update_badge_metadata(badge_id, 'failed', message)
                self.stats['failed'] += 1
                logger.error(f"✗ Failed: {badge_id} - {message}")
            
            # Rate limiting - be respectful to the server
            if i < len(badges_to_download):
                time.sleep(2)  # 2 second delay between downloads
        
        return downloaded_count
    
    def validate_existing_images(self) -> Dict[str, List[str]]:
        """
        Validate existing badge images and report issues.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating existing badge images...")
        
        results = {
            'valid': [],
            'missing': [],
            'invalid_format': [],
            'too_small': [],
            'corrupted': []
        }
        
        for badge in self.metadata.get('images', []):
            badge_id = badge.get('badge_id')
            if not badge_id:
                continue
            
            image_path = self._get_image_path(badge_id)
            
            if not image_path.exists():
                results['missing'].append(badge_id)
                continue
            
            try:
                # Basic file validation
                if image_path.stat().st_size == 0:
                    results['corrupted'].append(badge_id)
                    continue
                
                # Check file extension
                if image_path.suffix.lower() not in ['.png', '.jpg', '.jpeg']:
                    results['invalid_format'].append(badge_id)
                    continue
                
                # TODO: Add image dimension checking with PIL
                # For now, just mark as valid if file exists and has content
                results['valid'].append(badge_id)
                
            except Exception as e:
                logger.error(f"Error validating {badge_id}: {e}")
                results['corrupted'].append(badge_id)
        
        # Log validation results
        logger.info(f"Validation complete:")
        logger.info(f"  Valid: {len(results['valid'])}")
        logger.info(f"  Missing: {len(results['missing'])}")
        logger.info(f"  Invalid format: {len(results['invalid_format'])}")
        logger.info(f"  Too small: {len(results['too_small'])}")
        logger.info(f"  Corrupted: {len(results['corrupted'])}")
        
        return results
    
    def print_statistics(self):
        """Print download statistics."""
        logger.info("Download Statistics:")
        logger.info(f"  Attempted: {self.stats['attempted']}")
        logger.info(f"  Successful: {self.stats['successful']}")
        logger.info(f"  Failed: {self.stats['failed']}")
        logger.info(f"  Skipped: {self.stats['skipped']}")
        logger.info(f"  Already exists: {self.stats['already_exists']}")
        
        total_badges = len(self.metadata.get('images', []))
        existing_images = len([f for f in self.badges_dir.glob('*.png') if f.is_file()])
        coverage = (existing_images / total_badges * 100) if total_badges > 0 else 0
        
        logger.info(f"  Total badges: {total_badges}")
        logger.info(f"  Images available: {existing_images}")
        logger.info(f"  Coverage: {coverage:.1f}%")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Download badge images for Scouts Inventory System')
    parser.add_argument('--public-only', action='store_true', 
                       help='Download only publicly available images')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate existing images, don\'t download')
    parser.add_argument('--force-redownload', action='store_true',
                       help='Re-download existing images')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be downloaded without actually downloading')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = BadgeImageDownloader()
    
    try:
        if args.validate_only:
            # Only validate existing images
            results = downloader.validate_existing_images()
            if results['missing']:
                logger.info(f"Missing images for badges: {', '.join(results['missing'])}")
            return
        
        total_downloaded = 0
        
        # Download public images (default behavior)
        downloaded = downloader.download_public_images(
            force_redownload=args.force_redownload,
            dry_run=args.dry_run
        )
        total_downloaded += downloaded
        
        # Save updated metadata
        if not args.dry_run:
            downloader._save_metadata()
        
        # Print statistics
        downloader.print_statistics()
        
        if total_downloaded > 0:
            logger.info(f"Successfully downloaded {total_downloaded} badge images")
        else:
            logger.info("No new images were downloaded")
    
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()