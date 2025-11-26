#!/usr/bin/env zsh
# Scout Badge Inventory System - Restart Script
# Stops and restarts all services

# Color codes for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo "${BLUE}  Scout Badge Inventory System - Restarting${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Stop services
if [ -f stop.sh ]; then
    ./stop.sh
else
    echo "stop.sh not found, skipping stop..."
fi

echo ""
echo "${GREEN}Waiting 3 seconds before restart...${NC}"
sleep 3
echo ""

# Start services
if [ -f setup.sh ]; then
    ./setup.sh
else
    echo "setup.sh not found!"
    exit 1
fi
