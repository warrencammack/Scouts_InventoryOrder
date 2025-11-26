#!/usr/bin/env python3
"""
Authenticated Badge Image Downloader for Scout Member Protected Content

This script handles downloading badge images that require Scout Member authentication
from scoutshop.com.au. It includes secure credential handling and session management.

IMPORTANT: This script requires valid Scout Member credentials and should only be used
by authorized Scout Members in compliance with scoutshop.com.au terms of service.

Usage:
    python scripts/authenticated-badge-downloader.py [options]

Options:
    --username USER     Scout Member username/email
    --password PASS     Scout Member password (use --prompt-password for secure input)
    --prompt-password   Prompt for password securely (recommended)
    --dry-run          Show what would be downloaded without actually downloading
    --force-redownload  Re-download existing images
    --session-file FILE Save/load session cookies to/from file
"""

import os
import sys
import json
import requests
import time
import getpass
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import pickle

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the base downloader
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from download_badge_images import BadgeImageDownloader
except ImportError:
    logger.error("Could not import BadgeImageDownloader. Make sure download-badge-images.py exists in the scripts directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('authenticated_badge_download.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScoutShopAuthenticator:
    """Handles authentication with scoutshop.com.au"""
    
    def __init__(self, session_file: Optional[Path] = None):
        """Initialize authenticator with optional session persistence."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.base_url = "https://scoutshop.com.au"
        self.login_url = f"{self.base_url}/account/login"
        self.session_file = session_file
        self.logged_in = False
        
        # Load existing session if available
        if self.session_file and self.session_file.exists():
            self._load_session()
    
    def _save_session(self):
        """Save session cookies to file."""
        if not self.session_file:
            return
        
        try:
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.session.cookies, f)
            logger.info(f"Session saved to {self.session_file}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_session(self):
        """Load session cookies from file."""
        try:
            with open(self.session_file, 'rb') as f:
                self.session.cookies.update(pickle.load(f))
            logger.info(f"Session loaded from {self.session_file}")
            
            # Verify session is still valid
            if self._verify_login():
                self.logged_in = True
                logger.info("Existing session is valid")
            else:
                logger.info("Existing session expired")
                self.session.cookies.clear()
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
    
    def _get_csrf_token(self, url: str) -> Optional[str]:
        """Extract CSRF token from a page."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for CSRF token in various common locations
            csrf_token = None
            
            # Check meta tags
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                csrf_token = csrf_meta.get('content')
            
            # Check hidden form inputs
            if not csrf_token:
                csrf_input = soup.find('input', {'name': 'authenticity_token'})
                if csrf_input:
                    csrf_token = csrf_input.get('value')
            
            # Check for other common CSRF field names
            if not csrf_token:
                for field_name in ['_token', 'csrf_token', 'csrfmiddlewaretoken']:
                    csrf_input = soup.find('input', {'name': field_name})
                    if csrf_input:
                        csrf_token = csrf_input.get('value')
                        break
            
            return csrf_token
            
        except Exception as e:
            logger.error(f"Failed to get CSRF token from {url}: {e}")
            return None
    
    def _verify_login(self) -> bool:
        """Verify if current session is logged in."""
        try:
            # Try to access a member-only page
            response = self.session.get(f"{self.base_url}/account")
            
            # If we get redirected to login, we're not logged in
            if 'login' in response.url.lower():
                return False
            
            # Look for indicators of being logged in
            if response.status_code == 200:
                # Check for logout link or account-specific content
                soup = BeautifulSoup(response.text, 'html.parser')
                logout_link = soup.find('a', href=lambda x: x and 'logout' in x.lower())
                account_info = soup.find(class_=lambda x: x and 'account' in x.lower())
                
                return logout_link is not None or account_info is not None
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify login status: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """
        Attempt to log in to scoutshop.com.au
        
        Args:
            username: Scout Member username/email
            password: Scout Member password
            
        Returns:
            True if login successful, False otherwise
        """
        logger.info("Attempting to log in to scoutshop.com.au...")
        
        try:
            # First, get the login page to extract any CSRF tokens
            logger.info("Getting login page...")
            response = self.session.get(self.login_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the login form
            login_form = soup.find('form', {'id': 'customer_login'}) or soup.find('form', action=lambda x: x and 'login' in x)
            
            if not login_form:
                logger.error("Could not find login form on page")
                return False
            
            # Extract form action URL
            form_action = login_form.get('action', '/account/login')
            if not form_action.startswith('http'):
                form_action = urljoin(self.base_url, form_action)
            
            # Get CSRF token
            csrf_token = self._get_csrf_token(self.login_url)
            
            # Prepare login data
            login_data = {
                'customer[email]': username,
                'customer[password]': password,
            }
            
            # Add CSRF token if found
            if csrf_token:
                # Try different common CSRF field names
                for field_name in ['authenticity_token', '_token', 'csrf_token']:
                    csrf_input = soup.find('input', {'name': field_name})
                    if csrf_input:
                        login_data[field_name] = csrf_token
                        break
            
            # Add any other hidden form fields
            for hidden_input in soup.find_all('input', {'type': 'hidden'}):
                name = hidden_input.get('name')
                value = hidden_input.get('value')
                if name and value and name not in login_data:
                    login_data[name] = value
            
            logger.info("Submitting login credentials...")
            
            # Submit login form
            response = self.session.post(
                form_action,
                data=login_data,
                allow_redirects=True
            )
            
            # Check if login was successful
            if self._verify_login():
                self.logged_in = True
                logger.info("Login successful!")
                
                # Save session if file specified
                if self.session_file:
                    self._save_session()
                
                return True
            else:
                logger.error("Login failed - invalid credentials or login process changed")
                
                # Log response for debugging (without sensitive data)
                logger.debug(f"Login response status: {response.status_code}")
                logger.debug(f"Login response URL: {response.url}")
                
                return False
                
        except Exception as e:
            logger.error(f"Login attempt failed: {e}")
            return False
    
    def logout(self):
        """Log out and clear session."""
        try:
            # Try to find and use logout URL
            response = self.session.get(f"{self.base_url}/account")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                logout_link = soup.find('a', href=lambda x: x and 'logout' in x.lower())
                
                if logout_link:
                    logout_url = logout_link.get('href')
                    if not logout_url.startswith('http'):
                        logout_url = urljoin(self.base_url, logout_url)
                    
                    self.session.get(logout_url)
            
            # Clear session
            self.session.cookies.clear()
            self.logged_in = False
            
            # Remove session file
            if self.session_file and self.session_file.exists():
                self.session_file.unlink()
            
            logger.info("Logged out successfully")
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")


class AuthenticatedBadgeDownloader:
    """Downloads badge images requiring Scout Member authentication."""
    
    def __init__(self, base_downloader: BadgeImageDownloader, authenticator: ScoutShopAuthenticator):
        """Initialize with base downloader and authenticator."""
        self.base = base_downloader
        self.auth = authenticator
        
        # Statistics
        self.stats = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'login_required': 0
        }
    
    def _extract_product_image_url(self, product_url: str) -> Optional[str]:
        """
        Extract the main product image URL from a product page.
        
        Args:
            product_url: URL to the product page
            
        Returns:
            Direct URL to the product image, or None if not found
        """
        try:
            response = self.auth.session.get(product_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for product images in various common locations
            image_url = None
            
            # Check for main product image
            main_image = soup.find('img', {'class': lambda x: x and 'product' in x.lower()})
            if main_image:
                image_url = main_image.get('src') or main_image.get('data-src')
            
            # Check for featured image
            if not image_url:
                featured_image = soup.find('img', {'class': lambda x: x and 'featured' in x.lower()})
                if featured_image:
                    image_url = featured_image.get('src') or featured_image.get('data-src')
            
            # Check for any image in product gallery
            if not image_url:
                gallery_images = soup.find_all('img', {'alt': lambda x: x and 'badge' in x.lower()})
                if gallery_images:
                    image_url = gallery_images[0].get('src') or gallery_images[0].get('data-src')
            
            # Make URL absolute if relative
            if image_url and not image_url.startswith('http'):
                image_url = urljoin(self.auth.base_url, image_url)
            
            return image_url
            
        except Exception as e:
            logger.error(f"Failed to extract image URL from {product_url}: {e}")
            return None
    
    def download_protected_badges(self, dry_run: bool = False, force_redownload: bool = False) -> int:
        """
        Download badges that require Scout Member authentication.
        
        Args:
            dry_run: If True, only show what would be downloaded
            force_redownload: Re-download existing images
            
        Returns:
            Number of images successfully downloaded
        """
        if not self.auth.logged_in:
            logger.error("Must be logged in to download protected badges")
            return 0
        
        logger.info("Starting protected badge download...")
        downloaded_count = 0
        
        # Get badges that require authentication
        protected_badges = []
        for badge in self.base.metadata.get('images', []):
            badge_id = badge.get('badge_id')
            if not badge_id:
                continue
            
            # Check if image already exists
            image_path = self.base._get_image_path(badge_id)
            if image_path.exists() and not force_redownload:
                logger.info(f"Image already exists: {badge_id}")
                continue
            
            # Get URL and check if it requires authentication
            url = badge.get('image_source_url')
            if not url:
                continue
            
            # Check if this is a protected URL (category pages or member-only content)
            notes = badge.get('notes', '')
            if ('login' in notes.lower() or 
                '/t/badges/' in url or 
                'cubs-8-to-10' in url or 
                'special-interest-badges' in url):
                
                protected_badges.append((badge_id, url, image_path))
        
        logger.info(f"Found {len(protected_badges)} protected badges to process")
        
        if dry_run:
            for badge_id, url, image_path in protected_badges:
                logger.info(f"Would process: {badge_id} from {url}")
            return 0
        
        # Process protected badges
        for i, (badge_id, category_url, image_path) in enumerate(protected_badges, 1):
            self.stats['attempted'] += 1
            logger.info(f"Processing {i}/{len(protected_badges)}: {badge_id}")
            
            try:
                # If it's a category page, we need to find the specific product
                if '/t/badges/' in category_url:
                    product_url = self._find_product_in_category(category_url, badge_id)
                    if not product_url:
                        logger.warning(f"Could not find product page for {badge_id}")
                        self.stats['failed'] += 1
                        continue
                else:
                    product_url = category_url
                
                # Extract image URL from product page
                image_url = self._extract_product_image_url(product_url)
                if not image_url:
                    logger.error(f"Could not extract image URL for {badge_id}")
                    self.stats['failed'] += 1
                    continue
                
                # Download the image using the authenticated session
                success, message = self._download_authenticated_image(image_url, image_path)
                
                if success:
                    # Update metadata
                    file_info = {
                        'file_size': image_path.stat().st_size,
                        'file_format': image_path.suffix.lower(),
                        'file_hash': self.base._calculate_file_hash(image_path),
                        'download_date': datetime.now().isoformat(),
                        'source_url': product_url,
                        'image_url': image_url,
                        'authentication_required': True
                    }
                    
                    self.base._update_badge_metadata(badge_id, 'downloaded', message, file_info)
                    self.stats['successful'] += 1
                    downloaded_count += 1
                    logger.info(f"✓ Downloaded: {badge_id}")
                else:
                    self.base._update_badge_metadata(badge_id, 'failed', message)
                    self.stats['failed'] += 1
                    logger.error(f"✗ Failed: {badge_id} - {message}")
                
            except Exception as e:
                logger.error(f"Error processing {badge_id}: {e}")
                self.stats['failed'] += 1
            
            # Rate limiting
            if i < len(protected_badges):
                time.sleep(3)  # 3 second delay for authenticated requests
        
        return downloaded_count
    
    def _find_product_in_category(self, category_url: str, badge_id: str) -> Optional[str]:
        """
        Find specific product URL within a category page.
        
        Args:
            category_url: URL to the category page
            badge_id: Badge ID to search for
            
        Returns:
            Direct URL to the product page, or None if not found
        """
        try:
            response = self.auth.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract badge name from badge_id for searching
            badge_name_parts = badge_id.replace('-', ' ').split()
            
            # Look for product links
            product_links = soup.find_all('a', href=lambda x: x and '/products/' in x)
            
            for link in product_links:
                href = link.get('href')
                link_text = link.get_text(strip=True).lower()
                
                # Check if this link matches our badge
                if any(part.lower() in link_text for part in badge_name_parts):
                    if not href.startswith('http'):
                        href = urljoin(self.auth.base_url, href)
                    return href
                
                # Also check the href itself for matches
                if any(part.lower() in href.lower() for part in badge_name_parts):
                    if not href.startswith('http'):
                        href = urljoin(self.auth.base_url, href)
                    return href
            
            logger.warning(f"Could not find product for {badge_id} in category {category_url}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to search category {category_url}: {e}")
            return None
    
    def _download_authenticated_image(self, image_url: str, output_path: Path) -> Tuple[bool, str]:
        """
        Download an image using authenticated session.
        
        Args:
            image_url: URL to the image
            output_path: Local path to save the image
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Downloading authenticated image: {image_url}")
            
            response = self.auth.session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
                return False, f"URL does not contain an image (content-type: {content_type})"
            
            # Download and save
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file
            if output_path.stat().st_size == 0:
                output_path.unlink()
                return False, "Downloaded file is empty"
            
            logger.info(f"Successfully downloaded authenticated image: {output_path}")
            return True, "Authenticated download successful"
            
        except Exception as e:
            return False, f"Authenticated download failed: {str(e)}"
    
    def print_statistics(self):
        """Print download statistics."""
        logger.info("Authenticated Download Statistics:")
        logger.info(f"  Attempted: {self.stats['attempted']}")
        logger.info(f"  Successful: {self.stats['successful']}")
        logger.info(f"  Failed: {self.stats['failed']}")
        logger.info(f"  Skipped: {self.stats['skipped']}")
        logger.info(f"  Login required: {self.stats['login_required']}")


def main():
    """Main entry point for authenticated badge downloading."""
    parser = argparse.ArgumentParser(description='Download protected badge images with Scout Member authentication')
    parser.add_argument('--username', help='Scout Member username/email')
    parser.add_argument('--password', help='Scout Member password (use --prompt-password for secure input)')
    parser.add_argument('--prompt-password', action='store_true', 
                       help='Prompt for password securely (recommended)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be downloaded without actually downloading')
    parser.add_argument('--force-redownload', action='store_true',
                       help='Re-download existing images')
    parser.add_argument('--session-file', type=Path, default=Path('scout_session.pkl'),
                       help='File to save/load session cookies')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.username and not args.session_file.exists():
        logger.error("Username is required for first-time login")
        sys.exit(1)
    
    # Get password securely
    password = None
    if args.prompt_password:
        password = getpass.getpass("Scout Member Password: ")
    elif args.password:
        password = args.password
        logger.warning("Password provided via command line - this is less secure")
    
    try:
        # Initialize components
        base_downloader = BadgeImageDownloader()
        authenticator = ScoutShopAuthenticator(args.session_file)
        auth_downloader = AuthenticatedBadgeDownloader(base_downloader, authenticator)
        
        # Login if not already authenticated
        if not authenticator.logged_in:
            if not args.username or not password:
                logger.error("Username and password required for login")
                sys.exit(1)
            
            logger.info("Logging in to scoutshop.com.au...")
            if not authenticator.login(args.username, password):
                logger.error("Login failed")
                sys.exit(1)
        
        # Download protected badges
        downloaded = auth_downloader.download_protected_badges(
            dry_run=args.dry_run,
            force_redownload=args.force_redownload
        )
        
        # Save updated metadata
        if not args.dry_run:
            base_downloader._save_metadata()
        
        # Print statistics
        auth_downloader.print_statistics()
        
        if downloaded > 0:
            logger.info(f"Successfully downloaded {downloaded} protected badge images")
        else:
            logger.info("No new protected images were downloaded")
        
        # Logout
        authenticator.logout()
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()