# Scout Badge Inventory - Deployment Guide

Complete guide for deploying the Scout Badge Inventory System locally or in production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Methods](#deployment-methods)
  - [Method 1: Local Development (Shell Scripts)](#method-1-local-development-shell-scripts)
  - [Method 2: Docker Compose](#method-2-docker-compose)
- [Configuration](#configuration)
- [Database Management](#database-management)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

---

## Prerequisites

### Required Software

#### For Local Development
- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **Ollama** - [Download](https://ollama.ai/)
- **Git** - [Download](https://git-scm.com/)

#### For Docker Deployment
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (included with Docker Desktop)

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended for AI processing)
- **Storage**: 10GB free space (AI models require ~4GB)
- **OS**: macOS, Linux, or Windows with WSL2

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Scouts_InventoryOrder
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional for local development)
nano .env
```

### 3. Initialize Database

```bash
python3 database/init_db.py
```

### 4. Install Ollama Model

```bash
ollama pull llava:7b
```

### 5. Start the Application

**Option A: Using Shell Scripts (Recommended for Development)**
```bash
# Terminal 1 - Start Backend
./scripts/start-backend.sh

# Terminal 2 - Start Frontend
./scripts/start-frontend.sh
```

**Option B: Using Docker Compose**
```bash
docker-compose up --build
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## Deployment Methods

### Method 1: Local Development (Shell Scripts)

Best for: Development, testing, and single-user local deployments.

#### Step 1: Prepare the Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

#### Step 2: Start Services

```bash
# Start Backend (Terminal 1)
./scripts/start-backend.sh

# Start Frontend (Terminal 2)
./scripts/start-frontend.sh
```

#### Features:
- ✅ Hot reload for development
- ✅ Easy debugging
- ✅ Direct access to logs
- ✅ No Docker overhead

#### Limitations:
- ❌ Manual dependency management
- ❌ Requires separate Ollama installation
- ❌ No automatic restart on failure

---

### Method 2: Docker Compose

Best for: Production deployments, multi-user environments, and isolated testing.

#### Step 1: Build and Start

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

#### Step 2: Initialize Ollama Model (First Time Only)

```bash
# Pull the AI model inside the container
docker exec scouts_ollama ollama pull llava:7b
```

#### Step 3: Monitor Services

```bash
# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f ollama
```

#### Step 4: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

#### Features:
- ✅ Isolated environment
- ✅ Easy deployment across machines
- ✅ Automatic service restart
- ✅ GPU acceleration support (if available)
- ✅ Consistent environment

#### Limitations:
- ❌ Slower startup (initial build)
- ❌ More resource intensive
- ❌ Requires Docker knowledge

---

## Configuration

### Environment Variables

Edit `.env` file to customize configuration:

```bash
# Backend Configuration
DATABASE_URL=sqlite:///./database/inventory.db
UPLOAD_DIR=./uploads
OLLAMA_MODEL=llava:7b
OLLAMA_HOST=http://localhost:11434
API_PORT=8000
LOG_LEVEL=INFO

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Security (IMPORTANT: Change in production!)
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend-Only Configuration

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker-Specific Configuration

For Docker deployment, the `docker-compose.yml` file contains service-specific environment variables. Modify as needed:

```yaml
services:
  backend:
    environment:
      - OLLAMA_HOST=http://ollama:11434  # Points to Ollama container
      - ALLOWED_ORIGINS=http://localhost:3000
```

---

## Database Management

### Backup Database

```bash
# Create timestamped backup
./scripts/backup-database.sh

# Backups are stored in: ./backups/
# Format: inventory_backup_YYYYMMDD_HHMMSS.db
```

### Restore Database

```bash
# Stop the backend first
# Then copy backup over current database
cp backups/inventory_backup_20250109_120000.db database/inventory.db

# Restart backend
```

### Reset Database

```bash
# WARNING: This deletes all data
python3 database/init_db.py
```

### Database Location

- **Local Development**: `./database/inventory.db`
- **Docker**: Persistent volume mapped to `./database/`

---

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
```bash
# Ensure __init__.py files exist
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/models/__init__.py
touch backend/services/__init__.py

# Or reinstall
pip install -r backend/requirements.txt
```

### Ollama Connection Failed

**Error**: `Connection refused to http://localhost:11434`

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not, start Ollama
ollama serve

# Pull the model if needed
ollama pull llava:7b
```

### Frontend Can't Connect to Backend

**Error**: `ECONNREFUSED http://localhost:8000`

**Solutions**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
3. Check CORS settings in backend `.env`

### Docker Build Fails

**Error**: `failed to solve with frontend dockerfile.v0`

**Solution**:
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

### Out of Memory During AI Processing

**Error**: `Killed` or `OOM` when processing images

**Solutions**:
1. Reduce concurrent processing (process one image at a time)
2. Use smaller model: `ollama pull llava:7b` (instead of 13b)
3. Increase Docker memory limit (Docker Desktop → Settings → Resources)

### Port Already in Use

**Error**: `Address already in use: 8000` or `3000`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different ports in .env
```

---

## Production Considerations

### Security

1. **Change Secret Key**:
   ```bash
   # Generate strong secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Configure CORS Properly**:
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Use HTTPS**:
   - Set up reverse proxy (nginx/caddy)
   - Obtain SSL certificate (Let's Encrypt)

4. **Restrict File Uploads**:
   - Limit file sizes
   - Validate file types
   - Scan for malware

### Performance

1. **Use Production Build for Frontend**:
   ```bash
   cd frontend
   npm run build
   npm start
   ```

2. **Increase Uvicorn Workers**:
   ```bash
   uvicorn main:app --workers 4
   ```

3. **Enable GPU Acceleration**:
   - Ensure NVIDIA drivers installed
   - Docker GPU support configured
   - Ollama will auto-detect GPU

### Monitoring

1. **Check Logs Regularly**:
   ```bash
   tail -f logs/backend.log
   tail -f logs/frontend.log
   ```

2. **Set Up Health Checks**:
   - Backend: `http://localhost:8000/health`
   - Frontend: `http://localhost:3000`

3. **Monitor Disk Space**:
   - Uploads directory can grow large
   - Implement periodic cleanup
   - Monitor database size

### Backup Strategy

1. **Automated Backups**:
   ```bash
   # Add to crontab for daily backups
   0 2 * * * /path/to/scripts/backup-database.sh
   ```

2. **Off-site Backups**:
   - Copy backups to cloud storage
   - Use rsync to remote server

3. **Test Restore Process**:
   - Regularly test backup restoration
   - Document restoration steps

### Auto-Start on Boot (Linux/macOS)

**Using systemd (Linux)**:

Create `/etc/systemd/system/scouts-backend.service`:
```ini
[Unit]
Description=Scout Badge Inventory Backend
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Scouts_InventoryOrder
ExecStart=/path/to/scripts/start-backend.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable scouts-backend
sudo systemctl start scouts-backend
```

**Using launchd (macOS)**:

Create `~/Library/LaunchAgents/com.scouts.inventory.backend.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.scouts.inventory.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/scripts/start-backend.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.scouts.inventory.backend.plist
```

---

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs in `./logs/` directory
- Check API documentation at http://localhost:8000/docs
- Review integration tests: `tests/integration/README.md`

## Next Steps

- Review [API Documentation](http://localhost:8000/docs)
- Run integration tests: `python tests/integration/run_all_tests.py`
- Read [Testing Guide](../tests/integration/TESTING_GUIDE.md)
- Configure mobile access (see ACTION-501 in ACTION_PLAN.md)
