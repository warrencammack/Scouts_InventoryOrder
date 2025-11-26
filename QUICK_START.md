# Quick Start Guide

Get the Scout Badge Inventory System running with a single command!

## One-Command Setup

```zsh
./setup.sh
```

This automated script will:
- ✓ Check all system requirements (Python, Node.js, Ollama, Git)
- ✓ Install Ollama if not present
- ✓ Download the AI model (llava:7b)
- ✓ Set up environment variables
- ✓ Initialize the database
- ✓ Install all dependencies (Python & Node.js)
- ✓ Start all services (Ollama, Backend API, Frontend)

## Available Scripts

### `./setup.sh` - Complete Setup and Start
Performs full setup and starts all services.

**First time setup:**
```zsh
chmod +x setup.sh stop.sh restart.sh
./setup.sh
```

**Usage:**
```zsh
./setup.sh           # Standard setup (preserves existing database)
./setup.sh --reset-db # Reset and recreate the database
./setup.sh --help    # Show help message
```

**Features:**
- Checks for required dependencies (Python 3.10+, Node.js 18+, Git)
- Installs Ollama automatically if missing
- Downloads AI model if not present
- Creates virtual environment for Python
- Installs all dependencies
- Preserves existing database (use --reset-db to recreate)
- Starts all three services (Ollama, Backend, Frontend)
- Shows service URLs and PIDs

### `./stop.sh` - Stop All Services
Gracefully stops all running services.

```zsh
./stop.sh
```

**What it does:**
- Stops Ollama service
- Stops Backend API server
- Stops Frontend dev server
- Cleans up PID files

### `./restart.sh` - Restart All Services
Stops and restarts all services (useful after code changes).

```zsh
./restart.sh
```

**When to use:**
- After making backend code changes
- After updating dependencies
- When services are not responding
- To apply configuration changes

## After Setup

Once `setup.sh` completes, you'll see:

```
═══════════════════════════════════════════════════════════
  Application is Running!
═══════════════════════════════════════════════════════════

Services:
  • Ollama AI:   http://localhost:11434 (PID: 12345)
  • Backend API: http://localhost:8000 (PID: 12346)
  • Frontend:    http://localhost:3000 (PID: 12347)

Access the application:
  ➜ Open your browser to: http://localhost:3000

API Documentation:
  ➜ API Docs: http://localhost:8000/docs
```

### Access Points

- **Main Application:** [http://localhost:3000](http://localhost:3000)
- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

## Troubleshooting

### Script won't run
```zsh
# Make scripts executable
chmod +x setup.sh stop.sh restart.sh
```

### Missing dependencies
The script will tell you what's missing and provide installation commands.

**macOS:**
```zsh
# Install Homebrew first if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install dependencies
brew install python@3.11 node git
```

**Linux (Ubuntu/Debian):**
```zsh
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Port already in use
```zsh
# Stop all services first
./stop.sh

# Or manually kill processes
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:11434 | xargs kill -9 # Ollama

# Then restart
./setup.sh
```

### Services won't start
Check the log files:
```zsh
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Database issues
```zsh
# Recreate database using setup script
./setup.sh --reset-db

# Or manually
rm database/inventory.db
python3 database/init_db.py
```

## Manual Setup

If you prefer manual setup or the automated script doesn't work, see [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed step-by-step instructions.

## What's Running?

After setup, three services are running:

1. **Ollama** (Port 11434)
   - AI model runtime for badge recognition
   - Runs the LLaVA vision model

2. **Backend API** (Port 8000)
   - FastAPI Python server
   - Handles image uploads and AI processing
   - Manages database operations

3. **Frontend** (Port 3000)
   - Next.js React application
   - User interface for badge management
   - Development server with hot reload

## Service Management

### View running services
```zsh
cat .running_services
```

### Check service status
```zsh
# Check if services are responding
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:8000/health     # Backend
curl http://localhost:3000            # Frontend
```

### Stop individual services
```zsh
# If you saved the PIDs from setup output
kill <PID>

# Or by port
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
lsof -ti:11434 | xargs kill # Ollama
```

## Development Workflow

### Making Changes

**Backend changes:**
1. Edit Python files in `backend/`
2. Backend auto-reloads (uvicorn --reload)
3. Or restart: `./restart.sh`

**Frontend changes:**
1. Edit React files in `frontend/src/`
2. Frontend auto-reloads (Next.js dev server)
3. Changes appear immediately in browser

**Database changes:**
```zsh
# After modifying database/init_db.py
./stop.sh
rm database/inventory.db
python3 database/init_db.py
./setup.sh
```

### Environment Variables

Edit `.env` file to change configuration:
```zsh
nano .env  # or use your preferred editor
./restart.sh  # Apply changes
```

## System Requirements

**Minimum:**
- macOS or Linux
- 8GB RAM
- 10GB free disk space
- Internet connection (for initial setup)

**Recommended:**
- 16GB+ RAM
- 4+ CPU cores
- SSD storage

## Getting Help

- **Setup Guide:** [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Full Requirements:** [Requirements.md](Requirements.md)
- **Action Plan:** [ACTION_PLAN.md](ACTION_PLAN.md)

## Quick Commands Cheat Sheet

```zsh
# First time setup
./setup.sh

# Stop everything
./stop.sh

# Restart everything
./restart.sh

# View logs
tail -f logs/backend.log
tail -f logs/frontend.log

# Check what's running
cat .running_services

# Test services
curl http://localhost:8000/health
curl http://localhost:11434/api/tags
open http://localhost:3000
```

---

**Ready to start?** Run `./setup.sh` and you'll be up and running in minutes!
