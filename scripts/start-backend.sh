#!/bin/bash
# Scout Badge Inventory - Backend Startup Script
# Starts the FastAPI backend server with uvicorn

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
NC='\033[0m' # No Color

echo -e "${GREEN}Scout Badge Inventory - Backend Startup${NC}"
echo "========================================"

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

# Start the backend server
echo -e "\n${GREEN}Starting backend server...${NC}"
echo "Backend will run on: http://127.0.0.1:8000"
echo "API docs available at: http://127.0.0.1:8000/docs"
echo -e "Logs: $LOG_DIR/backend.log\n"

cd "$BACKEND_DIR"
python3 -m uvicorn main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload \
    --log-level info \
    2>&1 | tee "$LOG_DIR/backend.log"
