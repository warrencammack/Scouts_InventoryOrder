# Scout Badge Inventory - Backend

FastAPI backend for the AI-powered Scout Badge Inventory tracking system.

## Features

- RESTful API for badge inventory management
- SQLAlchemy ORM with SQLite database
- Integration with Ollama AI for badge recognition
- Image upload and processing
- Inventory tracking and reporting
- CORS-enabled for frontend integration

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Ollama installed and running (for badge recognition)

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration (optional - defaults work for local development)
nano .env
```

Environment variables:
- `DATABASE_URL`: SQLite database path (default: `sqlite:///database/inventory.db`)
- `OLLAMA_HOST`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: AI model to use (default: `llava:7b`)
- `UPLOAD_DIR`: Directory for uploaded images (default: `data/uploads`)
- `MAX_FILE_SIZE`: Maximum upload size in bytes (default: `10485760` = 10MB)
- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8000`)

### 4. Initialize Database

```bash
# Run the database initialization script
cd ..
python database/init_db.py
```

This will:
- Create all database tables
- Load badge data from `data/badges_list.json`
- Create inventory records with default thresholds
- Link ScoutShop URLs if available

### 5. Run the Server

```bash
# From the backend directory
cd backend
python main.py

# Or using uvicorn directly
uvicorn backend.main:app --reload

# Or from the project root
cd ..
uvicorn backend.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Documentation

Once the server is running, visit http://localhost:8000/docs for the interactive API documentation powered by Swagger UI.

### Available Endpoints

#### Health Check
- `GET /` - Root endpoint with API information
- `GET /health` - Health check with system status
- `GET /api/health` - API health check

#### Badges (Coming Soon)
- `GET /api/badges` - List all badges
- `GET /api/badges/{badge_id}` - Get specific badge details

#### Inventory (Coming Soon)
- `GET /api/inventory` - Get inventory status
- `PUT /api/inventory/{badge_id}` - Update badge quantity
- `POST /api/inventory/adjust` - Manual inventory adjustment

#### Scans (Coming Soon)
- `POST /api/upload` - Upload images for scanning
- `POST /api/process/{scan_id}` - Process uploaded images
- `GET /api/scans/{scan_id}` - Get scan results

#### Export (Coming Soon)
- `GET /api/export/csv` - Export inventory as CSV
- `GET /api/export/pdf` - Export inventory as PDF
- `GET /api/export/shopping-list` - Generate shopping list

## Database Schema

### Tables

1. **badges** - Badge information
   - Primary key: `id`
   - Unique: `badge_id`
   - Indexes: `name`, `category`

2. **inventory** - Current stock levels
   - Primary key: `id`
   - Foreign key: `badge_id` → badges.id
   - Tracks: quantity, reorder_threshold

3. **scans** - Upload/processing sessions
   - Primary key: `id`
   - Status: pending, processing, completed, failed
   - Tracks: total_images, processed_images

4. **scan_images** - Individual uploaded images
   - Primary key: `id`
   - Foreign key: `scan_id` → scans.id
   - Tracks: image_path, status, timestamps

5. **badge_detections** - AI detection results
   - Primary key: `id`
   - Foreign keys: `scan_image_id`, `badge_id`
   - Tracks: quantity, confidence score

6. **inventory_adjustments** - Audit trail
   - Primary key: `id`
   - Foreign keys: `badge_id`, `scan_id` (optional)
   - Tracks: old_quantity, new_quantity, reason

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── models/
│   ├── __init__.py
│   └── database.py      # SQLAlchemy models
├── api/                 # API routes (to be implemented)
├── services/            # Business logic (to be implemented)
└── scripts/             # Utility scripts (to be implemented)
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

### Code Style

This project uses:
- Type hints throughout
- SQLAlchemy 2.0 style
- Pydantic models for validation
- Comprehensive docstrings
- Error handling best practices

## Troubleshooting

### Database Issues

If you encounter database issues:

```bash
# Delete the database and reinitialize
rm ../database/inventory.db
python ../database/init_db.py
```

### Import Errors

If you get import errors, ensure you're running commands from the correct directory:

```bash
# For running the API
cd backend
python main.py

# For database initialization
cd /path/to/project/root
python database/init_db.py
```

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn backend.main:app --port 8001
```

Or update the `API_PORT` in your `.env` file.

## Next Steps

1. Implement API endpoints (ACTION-203 onwards)
2. Add badge recognition service (ACTION-204)
3. Create processing workflow (ACTION-206)
4. Add export functionality (ACTION-208)
5. Write tests
6. Add authentication (future enhancement)

## Support

For issues or questions:
1. Check the main project README.md
2. Review the ACTION_PLAN.md for development roadmap
3. Check API documentation at /docs endpoint
