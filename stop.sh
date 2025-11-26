#!/usr/bin/env zsh
# Scout Badge Inventory System - Stop Script
# Stops all running services

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo "${GREEN}✓${NC} $1"
}

log_warning() {
    echo "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo "${RED}✗${NC} $1"
}

echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo "${BLUE}  Scout Badge Inventory System - Stopping Services${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .running_services file exists
if [ -f .running_services ]; then
    log_info "Found running services file"

    # Source the PIDs
    source .running_services

    # Stop Ollama
    if [ -n "$OLLAMA_PID" ] && kill -0 "$OLLAMA_PID" 2>/dev/null; then
        log_info "Stopping Ollama (PID: $OLLAMA_PID)..."
        kill "$OLLAMA_PID"
        log_success "Ollama stopped"
    else
        log_warning "Ollama not running (PID: $OLLAMA_PID)"
    fi

    # Stop Backend
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        log_info "Stopping Backend API (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID"
        log_success "Backend API stopped"
    else
        log_warning "Backend API not running (PID: $BACKEND_PID)"
    fi

    # Stop Frontend
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        log_info "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID"
        log_success "Frontend stopped"
    else
        log_warning "Frontend not running (PID: $FRONTEND_PID)"
    fi

    # Clean up PID files
    rm -f .running_services .pids
    log_success "Cleaned up PID files"
else
    log_warning "No .running_services file found"
    log_info "Attempting to find and stop services by port..."

    # Try to stop services by port
    # Backend (port 8000)
    if lsof -ti:8000 &> /dev/null; then
        log_info "Stopping process on port 8000..."
        lsof -ti:8000 | xargs kill -9
        log_success "Stopped process on port 8000"
    fi

    # Frontend (port 3000)
    if lsof -ti:3000 &> /dev/null; then
        log_info "Stopping process on port 3000..."
        lsof -ti:3000 | xargs kill -9
        log_success "Stopped process on port 3000"
    fi

    # Ollama (port 11434)
    if lsof -ti:11434 &> /dev/null; then
        log_info "Stopping process on port 11434..."
        lsof -ti:11434 | xargs kill -9
        log_success "Stopped process on port 11434"
    fi

    # Also try killing by process name
    if pgrep -f "uvicorn main:app" &> /dev/null; then
        log_info "Stopping uvicorn processes..."
        pkill -f "uvicorn main:app"
        log_success "Stopped uvicorn processes"
    fi

    if pgrep -f "next dev" &> /dev/null; then
        log_info "Stopping Next.js dev server..."
        pkill -f "next dev"
        log_success "Stopped Next.js dev server"
    fi

    if pgrep ollama &> /dev/null; then
        log_info "Stopping Ollama..."
        pkill ollama
        log_success "Stopped Ollama"
    fi
fi

echo ""
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo "${GREEN}  All services stopped${NC}"
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "To start services again, run:"
echo "  ${BLUE}./setup.sh${NC}"
echo ""
