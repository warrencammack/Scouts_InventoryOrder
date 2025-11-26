# Scout Badge Inventory System

An AI-powered badge inventory management system for Cub Scout leaders in Australia. Upload photos of badge boxes, and the system automatically identifies and counts badges using local AI vision models.

## Quick Start

Get up and running in minutes with the automated setup:

```zsh
./setup.sh
```

That's it! The script will check dependencies, install what's needed, and start all services.

**For detailed instructions, see:**
- [QUICK_START.md](QUICK_START.md) - One-command setup guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed manual setup instructions

## Features

- 📸 **Image Upload** - Upload photos from phone or camera
- 🤖 **AI Recognition** - Automatic badge detection using local Ollama AI
- 📊 **Inventory Tracking** - Track badge counts over time
- 📈 **Analytics & Charts** - Visual reports and trends
- 🛒 **Shopping Lists** - Generate reorder lists with scoutshop.com.au links
- 📤 **Export** - Export reports to PDF/Excel
- 🏷️ **Badge Images** - Automatic downloading of official badge images from multiple sources

## What's Included

This system includes:
- **Backend API** (Python/FastAPI) - Handles uploads, AI processing, database
- **Frontend Web App** (Next.js/React) - User interface
- **Local AI** (Ollama/LLaVA) - Privacy-focused badge recognition
- **SQLite Database** - Badge data and inventory tracking

## Documentation

- [QUICK_START.md](QUICK_START.md) - Get running in one command
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [BADGE_IMAGE_DOWNLOADING.md](docs/BADGE_IMAGE_DOWNLOADING.md) - Badge image downloading guide
- [Requirements.md](Requirements.md) - Full requirements specification
- [ACTION_PLAN.md](ACTION_PLAN.md) - Development roadmap

## System Requirements

- **OS:** macOS or Linux
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 10GB free space
- **Software:** Python 3.10+, Node.js 18+, Ollama

## Scripts

- `./setup.sh` - Complete automated setup and start
- `./stop.sh` - Stop all services
- `./restart.sh` - Restart all services
- `./scripts/setup-badge-images.sh` - Download badge images from scoutshop.com.au

See [QUICK_START.md](QUICK_START.md) for details.