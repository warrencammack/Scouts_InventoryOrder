# Scout Badge Inventory - Quick Start Guide

Get the Scout Badge Inventory System running in under 5 minutes!

## Prerequisites

Before you begin, install:
- [Python 3.13+](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/)
- [Ollama](https://ollama.ai/)

## Installation Steps

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd Scouts_InventoryOrder
```

### 2. Set Up Environment

```bash
# Copy environment configuration
cp .env.example .env

# No changes needed for local development!
```

### 3. Initialize Database

```bash
# This creates the database with all 64 Scout badges
python3 database/init_db.py
```

Expected output:
```
✓ Database initialized successfully
✓ 64 badges loaded
✓ Ready to use!
```

### 4. Install AI Model

```bash
# Download the AI vision model (~4GB, one-time only)
ollama pull llava:7b
```

This will take 5-10 minutes depending on your internet speed.

### 5. Start the Application

Open two terminal windows:

**Terminal 1 - Backend**:
```bash
./scripts/start-backend.sh
```

Wait for: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 - Frontend**:
```bash
./scripts/start-frontend.sh
```

Wait for: `Local: http://localhost:3000`

### 6. Open and Use

1. Open browser to: **http://localhost:3000**
2. Upload badge images (drag & drop or click)
3. Click "Process Images" to identify badges
4. Review results and update inventory
5. View dashboard and generate shopping lists

## First Upload Test

Try the system with test images:

```bash
# The system includes test images in tests/integration/test_images/
# Use these to verify everything works
```

Expected workflow:
1. Upload → Takes ~2 seconds
2. Processing → Takes ~40 seconds per image (Ollama AI)
3. Results → Shows detected badges with quantities
4. Inventory → Updates automatically

## Verify Everything Works

Run the integration tests:

```bash
# Start backend first (Terminal 1)
./scripts/start-backend.sh

# Run tests (Terminal 2)
python tests/integration/run_all_tests.py
```

Expected output:
```
✓ E2E Tests: 9/9 PASS (100%)
✓ Edge Cases: 9/11 PASS (82%)
✓ Overall: 18/20 tests (90% pass rate)
```

## Common Issues

### "Ollama not found"
```bash
# Install Ollama
# macOS: brew install ollama
# Or download from: https://ollama.ai

# Start Ollama service
ollama serve
```

### "Port 8000 already in use"
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

### "Database not found"
```bash
# Reinitialize database
python3 database/init_db.py
```

### "Module not found"
```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

## What's Next?

- **View API Docs**: http://localhost:8000/docs
- **Create Backups**: `./scripts/backup-database.sh`
- **Read Full Guide**: `docs/DEPLOYMENT.md`
- **Run Performance Tests**: `tests/integration/TESTING_GUIDE.md`

## Daily Usage

### Starting the System
```bash
# Terminal 1
./scripts/start-backend.sh

# Terminal 2
./scripts/start-frontend.sh

# Open browser to http://localhost:3000
```

### Backing Up
```bash
# Before major changes
./scripts/backup-database.sh

# Backups saved to: ./backups/
```

### Stopping the System
```bash
# Press Ctrl+C in both terminal windows
```

## Mobile Access (Same Network)

To access from phone/tablet on the same WiFi:

1. Find your computer's IP address:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "
   # Look for something like: 192.168.1.100
   ```

2. Update frontend environment:
   ```bash
   # Edit frontend/.env.local
   NEXT_PUBLIC_API_URL=http://192.168.1.100:8000
   ```

3. Access from mobile browser:
   - Frontend: `http://192.168.1.100:3000`

## Support

- **Full Documentation**: `docs/DEPLOYMENT.md`
- **Testing Guide**: `tests/integration/TESTING_GUIDE.md`
- **Action Plan**: `ACTION_PLAN.md`

---

**You're ready to go!** 🎉
