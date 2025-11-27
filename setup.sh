#!/usr/bin/env zsh
# Scout Badge Inventory System - Automated Setup Script
# This script checks dependencies, installs missing components, and starts the application
#
# Usage:
#   ./setup.sh           - Standard setup (preserves existing database)
#   ./setup.sh --reset-db - Reset and recreate the database
#   ./setup.sh --help    - Show this help message
#
# For more information, see QUICK_START.md

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for help flag
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]]; then
    echo ""
    echo "Scout Badge Inventory System - Automated Setup Script"
    echo ""
    echo "Usage:"
    echo "  ./setup.sh           - Standard setup (preserves existing database)"
    echo "  ./setup.sh --reset-db - Reset and recreate the database"
    echo "  ./setup.sh --help    - Show this help message"
    echo ""
    echo "What this script does:"
    echo "  ✓ Checks system requirements (RAM, OS)"
    echo "  ✓ Verifies dependencies (Python 3.10+, Node.js 18+, Git)"
    echo "  ✓ Installs Ollama if missing (macOS/Linux)"
    echo "  ✓ Starts Ollama service"
    echo "  ✓ Downloads AI model (llava:7b) if not present"
    echo "  ✓ Sets up environment variables"
    echo "  ✓ Initializes/checks database"
    echo "  ✓ Installs Python dependencies (virtual environment)"
    echo "  ✓ Installs Node.js dependencies"
    echo "  ✓ Starts all services (Backend API, Frontend)"
    echo ""
    echo "After setup, access the application at: http://localhost:3000"
    echo ""
    echo "For more information, see:"
    echo "  - QUICK_START.md - Quick setup guide"
    echo "  - SETUP_GUIDE.md - Detailed manual setup"
    echo ""
    echo "To stop services:"
    echo "  ./stop.sh"
    echo ""
    exit 0
fi

echo ""
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo "${BLUE}  Scout Badge Inventory System - Automated Setup${NC}"
echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Track if we need to show manual installation instructions
NEEDS_MANUAL_INSTALL=false
MISSING_DEPS=""

# ============================================================================
# 1. CHECK SYSTEM REQUIREMENTS
# ============================================================================
log_info "Checking system requirements..."
echo ""

# Check OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
    log_success "Operating System: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
    log_success "Operating System: Linux"
else
    OS="Unknown"
    log_warning "Operating System: $OSTYPE (may not be fully supported)"
fi

# Check available RAM
if [[ "$OS" == "macOS" ]]; then
    TOTAL_RAM=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    log_info "Available RAM: ${TOTAL_RAM}GB"
    if [ "$TOTAL_RAM" -lt 8 ]; then
        log_warning "Less than 8GB RAM detected. AI processing may be slow."
    fi
elif [[ "$OS" == "Linux" ]]; then
    TOTAL_RAM=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
    log_info "Available RAM: ${TOTAL_RAM}GB"
    if [ "$TOTAL_RAM" -lt 8 ]; then
        log_warning "Less than 8GB RAM detected. AI processing may be slow."
    fi
fi

echo ""

# ============================================================================
# 2. CHECK AND INSTALL DEPENDENCIES
# ============================================================================
log_info "Checking dependencies..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        log_success "Python $PYTHON_VERSION found"
    else
        log_error "Python 3.10+ required, found $PYTHON_VERSION"
        NEEDS_MANUAL_INSTALL=true
        MISSING_DEPS="${MISSING_DEPS}\n  - Python 3.10+"
    fi
else
    log_error "Python 3 not found"
    NEEDS_MANUAL_INSTALL=true
    MISSING_DEPS="${MISSING_DEPS}\n  - Python 3.10+"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

    if [ "$NODE_MAJOR" -ge 18 ]; then
        log_success "Node.js $NODE_VERSION found"
    else
        log_error "Node.js 18+ required, found $NODE_VERSION"
        NEEDS_MANUAL_INSTALL=true
        MISSING_DEPS="${MISSING_DEPS}\n  - Node.js 18+"
    fi
else
    log_error "Node.js not found"
    NEEDS_MANUAL_INSTALL=true
    MISSING_DEPS="${MISSING_DEPS}\n  - Node.js 18+"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    log_success "npm $NPM_VERSION found"
else
    log_error "npm not found"
    NEEDS_MANUAL_INSTALL=true
    MISSING_DEPS="${MISSING_DEPS}\n  - npm"
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n1 || echo "unknown")
    log_success "Ollama found ($OLLAMA_VERSION)"
    HAS_OLLAMA=true
else
    log_warning "Ollama not found - will attempt to install"
    HAS_OLLAMA=false
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    log_success "Git $GIT_VERSION found"
else
    log_error "Git not found"
    NEEDS_MANUAL_INSTALL=true
    MISSING_DEPS="${MISSING_DEPS}\n  - Git"
fi

echo ""

# If critical dependencies are missing, show installation instructions and exit
if [ "$NEEDS_MANUAL_INSTALL" = true ]; then
    log_error "Critical dependencies missing. Please install:"
    echo -e "$MISSING_DEPS"
    echo ""
    echo "Installation instructions:"
    if [[ "$OS" == "macOS" ]]; then
        echo "  - Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        if [[ "$MISSING_DEPS" == *"Python"* ]]; then
            echo "  - Install Python: brew install python@3.11"
        fi
        if [[ "$MISSING_DEPS" == *"Node"* ]]; then
            echo "  - Install Node.js: brew install node"
        fi
        if [[ "$MISSING_DEPS" == *"Git"* ]]; then
            echo "  - Install Git: brew install git"
        fi
    elif [[ "$OS" == "Linux" ]]; then
        if [[ "$MISSING_DEPS" == *"Python"* ]]; then
            echo "  - Install Python: sudo apt install python3.11 python3.11-venv python3-pip"
        fi
        if [[ "$MISSING_DEPS" == *"Node"* ]]; then
            echo "  - Install Node.js: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
        fi
        if [[ "$MISSING_DEPS" == *"Git"* ]]; then
            echo "  - Install Git: sudo apt install git"
        fi
    fi
    echo ""
    echo "After installing dependencies, run this script again."
    exit 1
fi

# ============================================================================
# 3. INSTALL OLLAMA IF NEEDED
# ============================================================================
if [ "$HAS_OLLAMA" = false ]; then
    log_info "Installing Ollama..."

    if [[ "$OS" == "macOS" ]] || [[ "$OS" == "Linux" ]]; then
        curl -fsSL https://ollama.com/install.sh | sh

        if command -v ollama &> /dev/null; then
            log_success "Ollama installed successfully"
            HAS_OLLAMA=true
        else
            log_error "Failed to install Ollama automatically"
            echo "Please install manually from: https://ollama.com/download"
            exit 1
        fi
    else
        log_error "Cannot auto-install Ollama on this OS"
        echo "Please download and install from: https://ollama.com/download"
        exit 1
    fi
fi

echo ""

# ============================================================================
# 4. START OLLAMA SERVICE
# ============================================================================
log_info "Starting Ollama service..."

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    log_success "Ollama is already running"
else
    log_info "Starting Ollama in background..."
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!

    # Wait for Ollama to start (max 30 seconds)
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/tags &> /dev/null; then
            log_success "Ollama started successfully (PID: $OLLAMA_PID)"
            break
        fi
        sleep 1
    done

    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        log_error "Failed to start Ollama service"
        exit 1
    fi
fi

echo ""

# ============================================================================
# 5. PULL AI MODEL
# ============================================================================
log_info "Checking for AI model (llava:7b)..."

# Check if model is already installed
if ollama list | grep -q "llava:7b"; then
    log_success "Model llava:7b is already installed"
else
    log_info "Downloading AI model llava:7b (~4.5GB, this may take several minutes)..."
    echo ""
    ollama pull llava:7b
    echo ""
    log_success "Model downloaded successfully"
fi

echo ""

# ============================================================================
# 6. SETUP ENVIRONMENT VARIABLES
# ============================================================================
log_info "Setting up environment variables..."

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        log_success "Created .env file from .env.example"
    else
        log_error ".env.example not found"
        exit 1
    fi
else
    log_success ".env file already exists"
fi

echo ""

# ============================================================================
# 7. INITIALIZE DATABASE
# ============================================================================
log_info "Checking database..."

if [ -f database/inventory.db ]; then
    log_success "Database already exists"

    # Check if --reset-db flag was passed
    if [[ "$*" == *"--reset-db"* ]]; then
        log_info "Resetting database (--reset-db flag detected)..."
        BACKUP_NAME="database/inventory.db.backup.$(date +%Y%m%d_%H%M%S)"
        cp database/inventory.db "$BACKUP_NAME"
        log_success "Backup created: $BACKUP_NAME"

        log_info "Recreating database..."
        if ! python3 database/init_db.py 2>&1 | tee /tmp/db_init.log; then
            log_error "Failed to recreate database"
            echo ""
            echo "Error details:"
            cat /tmp/db_init.log
            echo ""
            exit 1
        fi
        log_success "Database recreated"
    else
        log_info "Ensuring badge data is up-to-date..."
        if ! python3 database/init_db.py 2>&1 | tee /tmp/db_init.log; then
            log_error "Failed to update badge data"
            echo ""
            echo "Error details:"
            cat /tmp/db_init.log
            echo ""
            exit 1
        fi
        log_success "Badge data is up-to-date"
    fi
else
    log_info "Creating database..."
    if ! python3 database/init_db.py 2>&1 | tee /tmp/db_init.log; then
        log_error "Failed to initialize database"
        echo ""
        echo "Error details:"
        cat /tmp/db_init.log
        echo ""
        echo "Check that:"
        echo "  - Python 3 is installed: python3 --version"
        echo "  - database/init_db.py exists"
        echo "  - database/ directory is writable"
        echo ""
        exit 1
    fi
    log_success "Database initialized"
fi

echo ""

# ============================================================================
# 8. SETUP BACKEND
# ============================================================================
log_info "Setting up backend..."

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
else
    log_success "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
log_info "Installing Python dependencies..."
pip install -q --upgrade pip

if ! pip install -r requirements.txt 2>&1 | tee /tmp/pip_install.log; then
    log_error "Failed to install Python dependencies"
    echo ""
    echo "Error details:"
    grep -i "error" /tmp/pip_install.log | tail -10
    echo ""
    echo "This is often caused by:"
    echo "  - Python version incompatibility (you have Python $PYTHON_VERSION)"
    echo "  - Missing system libraries"
    echo "  - Network issues"
    echo ""
    echo "To diagnose:"
    echo "  1. Check full error log: cat /tmp/pip_install.log"
    echo "  2. Try manual installation: cd backend && source venv/bin/activate && pip install -r requirements.txt"
    echo "  3. Check requirements.txt for version conflicts"
    echo ""
    exit 1
fi

log_success "Python dependencies installed"

cd ..

echo ""

# ============================================================================
# 9. SETUP FRONTEND
# ============================================================================
log_info "Setting up frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    log_info "Installing Node.js dependencies (this may take a few minutes)..."
    if ! npm install 2>&1 | tee /tmp/npm_install.log; then
        log_error "Failed to install Node.js dependencies"
        echo ""
        echo "Error details:"
        grep -i "error" /tmp/npm_install.log | tail -10
        echo ""
        echo "To diagnose:"
        echo "  1. Check full error log: cat /tmp/npm_install.log"
        echo "  2. Try manual installation: cd frontend && npm install"
        echo "  3. Delete node_modules and try again: rm -rf frontend/node_modules && npm install"
        echo ""
        exit 1
    fi
    log_success "Node.js dependencies installed"
else
    log_info "Checking for dependency updates..."
    if ! npm install 2>&1 | tee /tmp/npm_install.log; then
        log_error "Failed to update Node.js dependencies"
        echo ""
        echo "Error details:"
        grep -i "error" /tmp/npm_install.log | tail -10
        echo ""
        echo "To diagnose:"
        echo "  1. Check full error log: cat /tmp/npm_install.log"
        echo "  2. Try deleting node_modules: rm -rf node_modules package-lock.json && npm install"
        echo ""
        exit 1
    fi
    log_success "Dependencies up to date"
fi

cd ..

echo ""

# ============================================================================
# 10. START SERVICES
# ============================================================================
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo "${GREEN}  Setup Complete! Starting Services...${NC}"
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    log_info "Creating logs directory..."
    mkdir -p logs
fi

log_info "Starting backend API server..."
# Activate backend virtual environment and start server from parent directory
source backend/venv/bin/activate

# Start backend in background (run from parent directory so imports work)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
log_info "Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        log_success "Backend API started (PID: $BACKEND_PID)"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:8000/health &> /dev/null; then
    log_error "Failed to start backend API"
    echo ""
    echo "Backend server did not start within 30 seconds."
    echo ""
    echo "Check the error log:"
    echo "  ${YELLOW}tail -50 logs/backend.log${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Port 8000 already in use: lsof -ti:8000 | xargs kill"
    echo "  - Missing dependencies: cd backend && source venv/bin/activate && pip install -r requirements.txt"
    echo "  - Database issues: python3 database/init_db.py"
    echo ""
    echo "Last 10 lines of backend log:"
    tail -10 logs/backend.log 2>/dev/null || echo "  (log file not found)"
    echo ""
    exit 1
fi

echo ""

log_info "Starting frontend development server..."
cd frontend

# Start frontend in background
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
log_info "Waiting for frontend to start..."
for i in {1..60}; do
    if curl -s http://localhost:3000 &> /dev/null; then
        log_success "Frontend started (PID: $FRONTEND_PID)"
        break
    fi
    sleep 1
done

# Check if frontend actually started
if ! curl -s http://localhost:3000 &> /dev/null; then
    log_warning "Frontend did not start within 60 seconds"
    echo ""
    echo "The frontend may still be starting. Check:"
    echo "  ${YELLOW}tail -50 logs/frontend.log${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Port 3000 already in use: lsof -ti:3000 | xargs kill"
    echo "  - Missing dependencies: cd frontend && npm install"
    echo "  - Build errors: Check logs/frontend.log"
    echo ""
    echo "Last 10 lines of frontend log:"
    tail -10 ../logs/frontend.log 2>/dev/null || echo "  (log file not found)"
    echo ""
    echo "Note: Backend and Ollama are running. You can:"
    echo "  - Wait a bit longer and check http://localhost:3000"
    echo "  - View logs: tail -f logs/frontend.log"
    echo "  - Stop services: ./stop.sh"
    echo ""
fi

cd ..

echo ""

# ============================================================================
# 11. SUMMARY
# ============================================================================
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo "${GREEN}  Application is Running!${NC}"
echo "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Services:"
echo "  ${BLUE}•${NC} Ollama AI:   http://localhost:11434 (PID: $OLLAMA_PID)"
echo "  ${BLUE}•${NC} Backend API: http://localhost:8000 (PID: $BACKEND_PID)"
echo "  ${BLUE}•${NC} Frontend:    http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "Access the application:"
echo "  ${GREEN}➜${NC} Open your browser to: ${BLUE}http://localhost:3000${NC}"
echo ""
echo "API Documentation:"
echo "  ${GREEN}➜${NC} API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "Logs:"
echo "  ${BLUE}•${NC} Backend: logs/backend.log"
echo "  ${BLUE}•${NC} Frontend: logs/frontend.log"
echo ""
echo "To stop all services:"
echo "  ${YELLOW}kill $OLLAMA_PID $BACKEND_PID $FRONTEND_PID${NC}"
echo ""
echo "Or use the stop script:"
echo "  ${YELLOW}./stop.sh${NC}"
echo ""
echo "${GREEN}Happy badge inventory management!${NC}"
echo ""

# Create a PID file for easy cleanup
echo "$OLLAMA_PID" > .pids
echo "$BACKEND_PID" >> .pids
echo "$FRONTEND_PID" >> .pids

# Save PIDs to a more structured file
cat > .running_services << EOF
# Scout Badge Inventory System - Running Services
# Generated: $(date)

OLLAMA_PID=$OLLAMA_PID
BACKEND_PID=$BACKEND_PID
FRONTEND_PID=$FRONTEND_PID

# To stop all services, run: ./stop.sh
# Or manually: kill $OLLAMA_PID $BACKEND_PID $FRONTEND_PID
EOF

log_success "Service PIDs saved to .running_services"
