#!/bin/bash

# Badge Image Setup Script for Scouts Inventory System
# This script helps set up and download badge images from multiple sources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Function to check if Python package is installed
check_python_package() {
    python3 -c "import $1" 2>/dev/null
}

# Function to install Python dependencies
install_dependencies() {
    log_info "Checking Python dependencies for badge downloading..."
    
    # Check if requirements file exists
    if [ ! -f "scripts/requirements.txt" ]; then
        log_error "Requirements file not found: scripts/requirements.txt"
        return 1
    fi
    
    # Check for required packages
    local missing_packages=()
    
    if ! check_python_package "bs4"; then
        missing_packages+=("beautifulsoup4")
    fi
    
    if ! check_python_package "requests"; then
        missing_packages+=("requests")
    fi
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        log_info "Installing missing packages: ${missing_packages[*]}"
        pip3 install -r scripts/requirements.txt
        log_success "Dependencies installed successfully"
    else
        log_success "All required dependencies are already installed"
    fi
}

# Function to download public badge images
download_public_images() {
    log_info "Downloading publicly available badge images..."
    
    if [ "$1" = "--dry-run" ]; then
        log_info "Running in dry-run mode (no actual downloads)"
        python3 scripts/download_badge_images.py --dry-run
    else
        python3 scripts/download_badge_images.py
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Public image download completed"
    else
        log_error "Public image download failed"
        return 1
    fi
}

# Function to validate existing images
validate_images() {
    log_info "Validating existing badge images..."
    
    python3 scripts/download_badge_images.py --validate-only
    
    if [ $? -eq 0 ]; then
        log_success "Image validation completed"
    else
        log_error "Image validation failed"
        return 1
    fi
}

# Function to show download statistics
show_statistics() {
    log_info "Badge Image Statistics:"
    
    # Count total badges in metadata
    if [ -f "data/badge_images_metadata.json" ]; then
        local total_badges=$(python3 -c "
import json
with open('data/badge_images_metadata.json', 'r') as f:
    data = json.load(f)
    print(len(data.get('images', [])))
" 2>/dev/null || echo "0")
        
        echo "  Total badges in metadata: $total_badges"
    fi
    
    # Count downloaded images
    if [ -d "data/badges" ]; then
        local downloaded_count=$(find data/badges -name "*.png" -type f | wc -l)
        echo "  Downloaded images: $downloaded_count"
        
        if [ "$total_badges" -gt 0 ]; then
            local coverage=$(python3 -c "print(f'{$downloaded_count/$total_badges*100:.1f}')" 2>/dev/null || echo "0.0")
            echo "  Coverage: ${coverage}%"
        fi
    else
        echo "  Downloaded images: 0 (badges directory not found)"
    fi
    
    # Show recent log entries
    if [ -f "badge_download.log" ]; then
        echo ""
        log_info "Recent download activity:"
        tail -5 badge_download.log | sed 's/^/  /'
    fi
}

# Function to setup authenticated downloading
setup_authenticated_download() {
    log_info "Setting up authenticated badge downloading..."
    log_warning "This requires a valid Scout Member account on scoutshop.com.au"
    
    echo ""
    echo "To download login-protected badge images, you need:"
    echo "  1. Valid Scout Member account credentials"
    echo "  2. Permission to access badge inventory"
    echo "  3. Compliance with scoutshop.com.au terms of service"
    echo ""
    
    read -p "Do you have a Scout Member account and want to set up authenticated downloading? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "You can run authenticated downloading with:"
        echo "  python3 scripts/authenticated-badge-downloader.py --username your.email@example.com --prompt-password"
        echo ""
        log_info "For security, always use --prompt-password to enter your password securely"
        
        read -p "Would you like to run authenticated downloading now? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your Scout Member username/email: " username
            if [ -n "$username" ]; then
                log_info "Running authenticated downloader..."
                python3 scripts/authenticated-badge-downloader.py --username "$username" --prompt-password
            else
                log_error "No username provided"
            fi
        fi
    else
        log_info "Skipping authenticated downloading setup"
    fi
}

# Function to show help
show_help() {
    echo "Badge Image Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --install-deps     Install Python dependencies only"
    echo "  --public-only      Download only public images"
    echo "  --with-auth        Setup and run authenticated downloading"
    echo "  --validate         Validate existing images only"
    echo "  --stats            Show download statistics"
    echo "  --dry-run          Show what would be downloaded (no actual downloads)"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Full setup and public download"
    echo "  $0 --public-only   # Download public images only"
    echo "  $0 --with-auth     # Include authenticated downloading"
    echo "  $0 --dry-run       # Preview what would be downloaded"
    echo ""
}

# Main execution
main() {
    log_info "Badge Image Setup for Scouts Inventory System"
    echo ""
    
    case "${1:-}" in
        --help)
            show_help
            exit 0
            ;;
        --install-deps)
            install_dependencies
            exit 0
            ;;
        --validate)
            validate_images
            show_statistics
            exit 0
            ;;
        --stats)
            show_statistics
            exit 0
            ;;
        --public-only)
            install_dependencies
            download_public_images "${2:-}"
            validate_images
            show_statistics
            ;;
        --with-auth)
            install_dependencies
            download_public_images "${2:-}"
            setup_authenticated_download
            validate_images
            show_statistics
            ;;
        --dry-run)
            install_dependencies
            download_public_images --dry-run
            ;;
        "")
            # Default: install deps and download public images
            install_dependencies
            download_public_images
            validate_images
            show_statistics
            
            echo ""
            log_info "Public badge image setup complete!"
            log_info "For login-protected images, run: $0 --with-auth"
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"