#!/bin/bash
# Scout Badge Inventory - Frontend Startup Script
# Starts the Next.js frontend development server

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOG_DIR="$PROJECT_ROOT/logs"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Scout Badge Inventory - Frontend Startup${NC}"
echo "========================================="

# Create logs directory
mkdir -p "$LOG_DIR"

# Check Node.js version
echo -e "\n${YELLOW}Checking Node.js version...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js from: https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}Found Node.js $NODE_VERSION${NC}"

# Check npm version
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}Found npm $NPM_VERSION${NC}"

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "\n${YELLOW}Installing dependencies (this may take a few minutes)...${NC}"
    npm install
else
    echo -e "\n${YELLOW}Checking for dependency updates...${NC}"
    npm install --prefer-offline
fi

# Check .env.local exists
if [ ! -f ".env.local" ]; then
    echo -e "\n${YELLOW}Creating .env.local from .env.example...${NC}"
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        grep "^NEXT_PUBLIC" "$PROJECT_ROOT/.env.example" > .env.local || echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    else
        echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    fi
fi

# Start the frontend server
echo -e "\n${GREEN}Starting frontend development server...${NC}"
echo "Frontend will run on: http://localhost:3000"
echo -e "Logs: $LOG_DIR/frontend.log\n"

npm run dev 2>&1 | tee "$LOG_DIR/frontend.log"
