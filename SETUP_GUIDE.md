# Scout Badge Inventory System - Local Development Setup Guide

This guide provides step-by-step instructions for setting up and running the Scout Badge Inventory System on your local machine.

## Table of Contents
- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Additional Configuration](#additional-configuration)

---

## System Requirements

### Minimum Requirements
- **OS**: macOS, Linux, or Windows 10/11
- **RAM**: 8GB (16GB recommended for Ollama AI models)
- **Disk Space**: 10GB free space (AI models require ~5GB)
- **Internet**: Required for initial setup and package downloads

### Recommended for Best Performance
- **RAM**: 16GB or more
- **CPU**: 4+ cores
- **GPU**: NVIDIA GPU with CUDA support (optional, speeds up AI processing)

---

## Prerequisites

You'll need to install the following software before setting up the application:

> **Note**: This guide assumes you're using **zsh** (default on macOS) or **bash** (common on Linux). Commands are provided for both Unix-like systems (macOS/Linux) and Windows where they differ.

### 1. Python 3.10+

Check if Python is installed:
```sh
python3 --version
```

If not installed:
- **macOS**:
  ```sh
  brew install python@3.11
  ```
- **Ubuntu/Debian**:
  ```sh
  sudo apt update
  sudo apt install python3.11 python3.11-venv python3-pip
  ```
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 2. Node.js 18+ and npm

Check if Node.js is installed:
```sh
node --version
npm --version
```

If not installed:
- **macOS**:
  ```sh
  brew install node
  ```
- **Ubuntu/Debian**:
  ```sh
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
  ```
- **Windows**: Download from [nodejs.org](https://nodejs.org/)

### 3. Ollama (AI Model Runtime)

Ollama runs the local AI vision models for badge recognition.

**Installation:**
- **macOS/Linux**:
  ```sh
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Windows**: Download from [ollama.com](https://ollama.com/download)

**Verify installation:**
```sh
ollama --version
```

**Pull the AI model:**
```sh
ollama pull llava:7b
```

This downloads the LLaVA 7B vision model (~4.5GB). Wait for it to complete.

**Start Ollama service:**
```zsh
# On macOS/Linux, Ollama usually starts automatically
# Check if it's running:
ollama list

# If not running, start it:
ollama serve
```

### 4. Git

Check if Git is installed:
```sh
git --version
```

If not installed:
- **macOS**: `brew install git`
- **Ubuntu/Debian**: `sudo apt install git`
- **Windows**: Download from [git-scm.com](https://git-scm.com/)

---

## Quick Start

For those who want to get running quickly:

```zsh
# 1. Clone the repository (if you haven't already)
cd /path/to/project/Scouts_InventoryOrder/Scouts_InventoryOrder

# 2. Set up environment variables
cp .env.example .env

# 3. Start Ollama (if not already running)
ollama serve &

# 4. Pull the AI model
ollama pull llava:7b

# 5. Set up and start the backend
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux (zsh/bash) | Windows: venv\Scripts\activate
pip install -r requirements.txt
python ../database/init_db.py
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# 6. In a new terminal, set up and start the frontend
cd frontend
npm install
npm run dev
```

> **Note**: On Windows, use Command Prompt or PowerShell and adjust commands accordingly (e.g., `copy` instead of `cp`, `venv\Scripts\activate` instead of `source venv/bin/activate`).

Open your browser to [http://localhost:3000](http://localhost:3000)

---

## Detailed Setup

### Step 1: Clone or Navigate to the Project

```zsh
# If you haven't cloned the repository yet:
git clone <repository-url>
cd Scouts_InventoryOrder/Scouts_InventoryOrder

# If you already have it:
cd /path/to/Scouts_InventoryOrder/Scouts_InventoryOrder
```

### Step 2: Configure Environment Variables

The application uses environment variables for configuration.

```zsh
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file if needed (the defaults should work for local development):

```sh
# Key configuration options:
DATABASE_URL=sqlite:///./database/inventory.db
UPLOAD_DIR=./uploads
OLLAMA_MODEL=llava:7b
OLLAMA_HOST=http://localhost:11434
API_HOST=127.0.0.1
API_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3: Initialize the Database

The application uses SQLite for data storage.

```zsh
# Create the database and seed it with badge data
python3 database/init_db.py
```

You should see output like:
```
Creating database at ./database/inventory.db
✓ Database created successfully
✓ Added 45 Australian Cub Scout badges
✓ Database initialization complete
```

### Step 4: Set Up the Backend (Python/FastAPI)

```zsh
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux (zsh/bash):
source venv/bin/activate

# On Windows (Command Prompt):
# venv\Scripts\activate

# On Windows (PowerShell):
# venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

**Verify installation:**
```zsh
pip list | grep fastapi
# Should show: fastapi==0.104.1
```

### Step 5: Set Up the Frontend (Next.js/React)

Open a new terminal window:

```zsh
cd frontend

# Install Node.js dependencies
npm install
```

This will install all required packages including React, Next.js, and Tailwind CSS.

**Verify installation:**
```zsh
npm list --depth=0
# Should show next, react, typescript, etc.
```

---

## Running the Application

You need to run three services: Ollama, Backend, and Frontend.

### Terminal 1: Ollama (AI Service)

```zsh
# Start Ollama service (if not already running)
ollama serve
```

Keep this terminal running. You should see:
```
Ollama is running on http://localhost:11434
```

### Terminal 2: Backend API

```zsh
# Run from the project root directory (Scouts_InventoryOrder/Scouts_InventoryOrder)
# NOT from inside the backend/ directory

# Activate virtual environment if not already active
# macOS/Linux (zsh/bash):
source backend/venv/bin/activate
# Windows: backend\venv\Scripts\activate

# Start the FastAPI server (from parent directory)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
Starting Scout Badge Inventory API...
Database: sqlite:///./database/inventory.db
Upload directory: ./uploads
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test the backend:**
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to see the API documentation.

### Terminal 3: Frontend

```zsh
cd frontend

# Start the Next.js development server
npm run dev
```

You should see:
```
▲ Next.js 14.2.0
- Local:        http://localhost:3000
- Ready in 2.3s
```

**Access the application:**
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Using the Application

### Basic Workflow

1. **Upload Badge Images**
   - Click "Upload Images" or drag and drop photos
   - Supported formats: JPG, PNG, HEIC
   - Maximum size: 10MB per image

2. **AI Processing**
   - The system will analyze images using the Ollama AI model
   - Processing takes ~10-30 seconds per image
   - You'll see progress indicators

3. **Review Results**
   - Verify detected badges and counts
   - Correct any misidentifications
   - Add manual adjustments if needed

4. **View Inventory**
   - See current stock levels
   - View charts and analytics
   - Export reports (PDF, Excel)

5. **Generate Shopping List**
   - Identify badges that need reordering
   - Get direct links to scoutshop.com.au

---

## Troubleshooting

### Ollama Issues

**Problem: "Connection refused to Ollama"**
```zsh
# Check if Ollama is running:
curl http://localhost:11434

# If not, start it:
ollama serve
```

**Problem: "Model not found"**
```zsh
# List installed models:
ollama list

# If llava:7b is missing, pull it:
ollama pull llava:7b
```

**Problem: "Ollama is slow"**
- Ensure you have at least 8GB RAM available
- Close other memory-intensive applications
- Consider using a smaller model: `ollama pull llava:7b` (default) or `ollama pull moondream2` (lighter)

### Backend Issues

**Problem: "Port 8000 already in use"**
```zsh
# Find and kill the process using port 8000:
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Problem: "Module not found" errors**
```zsh
# Ensure virtual environment is activated:
# macOS/Linux (zsh/bash):
source backend/venv/bin/activate
# Windows: backend\venv\Scripts\activate

# Reinstall dependencies:
pip install -r backend/requirements.txt
```

**Problem: "Database locked"**
```zsh
# Stop all backend instances and restart:
pkill -f uvicorn
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Issues

**Problem: "Port 3000 already in use"**
```zsh
# Kill the process using port 3000:
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Or use a different port:
PORT=3001 npm run dev
```

**Problem: "Failed to fetch from API"**
- Ensure backend is running on port 8000
- Check `.env` file has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Verify CORS settings in backend allow localhost:3000

**Problem: "Module not found" in frontend**
```zsh
# Delete node_modules and reinstall:
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Issues

**Problem: "Database doesn't exist"**
```zsh
# Reinitialize the database:
python3 database/init_db.py
```

**Problem: "Database is corrupted"**
```zsh
# Backup and recreate:
cp database/inventory.db database/inventory.db.backup
rm database/inventory.db
python3 database/init_db.py
```

---

## Additional Configuration

### Using Different AI Models

You can try different Ollama models for badge recognition:

```zsh
# List available vision models:
ollama list

# Try other models:
ollama pull bakllava        # Alternative vision model
ollama pull moondream2      # Lighter, faster model
ollama pull llava:13b       # Larger, more accurate (requires more RAM)

# Update .env file:
OLLAMA_MODEL=bakllava
```

### Production Deployment

For production deployment, see:
- [docker-compose.yml](docker-compose.yml) for containerized deployment
- [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) for deployment guide
- Use environment variable `ENVIRONMENT=production` in `.env`

### Running with Docker (Alternative)

If you prefer Docker:

```zsh
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This starts:
- Ollama on port 11434
- Backend on port 8000
- Frontend on port 3000

### Development Scripts

Convenience scripts are available in the `scripts/` directory:

```zsh
# Start backend (creates venv, installs deps, runs server)
./scripts/start-backend.sh

# Start frontend (installs deps, runs dev server)
./scripts/start-frontend.sh

# Backup database
./scripts/backup-database.sh

# Security audit
./scripts/security-audit.sh

# Validate frontend code
./scripts/validate-frontend.sh
```

Make scripts executable if needed:
```zsh
chmod +x scripts/*.sh
```

---

## Project Structure

```
Scouts_InventoryOrder/
├── backend/              # FastAPI Python backend
│   ├── api/             # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── main.py          # FastAPI app entry point
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js React frontend
│   ├── src/
│   │   ├── app/        # Next.js pages
│   │   └── components/ # React components
│   ├── package.json    # Node.js dependencies
│   └── tailwind.config.js
├── database/            # SQLite database
│   ├── init_db.py      # Database initialization
│   └── inventory.db    # SQLite database file
├── scripts/            # Utility scripts
├── .env.example        # Environment template
└── docker-compose.yml  # Docker configuration
```

---

## Environment Variables Reference

### Backend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database path | `sqlite:///./database/inventory.db` |
| `UPLOAD_DIR` | Image upload directory | `./uploads` |
| `OLLAMA_MODEL` | AI model to use | `llava:7b` |
| `OLLAMA_HOST` | Ollama service URL | `http://localhost:11434` |
| `API_HOST` | Backend host | `127.0.0.1` |
| `API_PORT` | Backend port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |

### Frontend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

---

## Testing the Setup

### 1. Test Ollama
```zsh
curl http://localhost:11434/api/tags
# Should return JSON with installed models
```

### 2. Test Backend API
```zsh
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

curl http://localhost:8000/api/badges
# Should return JSON array of badges
```

### 3. Test Frontend
Open [http://localhost:3000](http://localhost:3000) - you should see the Scout Badge Inventory interface.

### 4. Test Full Workflow
1. Navigate to the Upload page
2. Upload a test image (any image will work for testing)
3. Verify the image appears in the preview
4. Click "Process Images"
5. Check the Processing Status page for progress

---

## Performance Tips

1. **Faster AI Processing**
   - Use a GPU if available (Ollama will automatically detect)
   - Use smaller models for faster processing: `ollama pull moondream2`
   - Process images one at a time for lower memory usage

2. **Reduce Memory Usage**
   - Close unnecessary applications
   - Use `llava:7b` instead of `llava:13b`
   - Limit concurrent image processing

3. **Speed Up Development**
   - Use `--reload` flag for backend auto-restart on code changes
   - Frontend dev server has hot reload by default
   - Keep Ollama running in the background

---

## Getting Help

- **Issues**: Check [Troubleshooting](#troubleshooting) section
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Project Requirements**: See [Requirements.md](Requirements.md)
- **Action Plan**: See [ACTION_PLAN.md](ACTION_PLAN.md)

---

## Next Steps

Once you have the application running:

1. **Add Badge Images**: Populate the badge database with actual reference images
2. **Test Recognition**: Upload photos of real scout badges to test AI accuracy
3. **Customize**: Adjust minimum stock thresholds and categories
4. **Export Data**: Try the export functionality for inventory reports
5. **Explore API**: Use the interactive API docs at `/docs` endpoint

---

## License

See [LICENSE](LICENSE) file for details.

---

**Last Updated**: November 2025
**Version**: 0.1.0 (MVP Development)
