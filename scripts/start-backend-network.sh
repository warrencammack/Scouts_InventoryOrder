#!/bin/bash
# Scout Badge Inventory - Backend Network Startup Script
# Starts the FastAPI backend server accessible from local network

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="$PROJECT_ROOT/logs"
VENV_DIR="$PROJECT_ROOT/venv"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}Scout Badge Inventory - Backend Network Startup${NC}"
echo "=================================================="

# Create logs directory
mkdir -p "$LOG_DIR"

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Install/update dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r "$BACKEND_DIR/requirements.txt"

# Check Ollama is running
echo -e "\n${YELLOW}Checking Ollama service...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Warning: Ollama is not installed${NC}"
    echo "Please install Ollama from: https://ollama.ai"
    echo "Then run: ollama pull llava:7b"
else
    OLLAMA_VERSION=$(ollama --version | head -n1)
    echo -e "${GREEN}Found $OLLAMA_VERSION${NC}"

    # Check if llava model is available
    if ! ollama list | grep -q "llava:7b"; then
        echo -e "${YELLOW}Pulling llava:7b model (this may take a while)...${NC}"
        ollama pull llava:7b
    fi
fi

# Check database exists
DB_FILE="$PROJECT_ROOT/database/inventory.db"
if [ ! -f "$DB_FILE" ]; then
    echo -e "\n${YELLOW}Initializing database...${NC}"
    cd "$PROJECT_ROOT" && python3 database/init_db.py
fi

# Get local network IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

# Start the backend server on all interfaces
echo -e "\n${GREEN}Starting backend server on all network interfaces...${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}Local access:   http://127.0.0.1:8000${NC}"
echo -e "${CYAN}Network access: http://${LOCAL_IP}:8000${NC}"
echo -e "${CYAN}API docs:       http://${LOCAL_IP}:8000/docs${NC}"
echo -e "${CYAN}================================================${NC}"
echo -e "Logs: $LOG_DIR/backend.log\n"

echo -e "${YELLOW}Access from mobile devices on same WiFi:${NC}"
echo -e "  Frontend: http://${LOCAL_IP}:3000"
echo -e "  Backend:  http://${LOCAL_IP}:8000"
echo -e ""

cd "$BACKEND_DIR"
python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    2>&1 | tee "$LOG_DIR/backend.log"
