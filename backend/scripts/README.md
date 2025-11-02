# Backend Scripts

This directory contains utility scripts for database management and maintenance.

## Available Scripts

### load_badge_data.py

Loads or updates badge data from JSON files into the database.

**Usage:**
```bash
# Load badge data (skip existing badges)
python backend/scripts/load_badge_data.py

# Clear and reload all badge data
python backend/scripts/load_badge_data.py --clear

# Load with custom reorder threshold
python backend/scripts/load_badge_data.py --threshold 10
```

**Options:**
- `--clear` - Clear existing badge and inventory data before loading
- `--threshold N` - Set default reorder threshold (default: 5)

**Features:**
- Loads badge data from `data/badges_list.json`
- Loads ScoutShop URLs from `data/scoutshop_urls.json`
- Creates inventory records with default thresholds
- Updates existing badges without duplicating
- Comprehensive error handling and progress reporting

**When to use:**
- After updating badge data in JSON files
- To change reorder thresholds for new badges
- To reload badge data without reinitializing entire database

## Related Scripts

### database/init_db.py

Full database initialization script that:
- Creates all database tables
- Loads badge data
- Initializes inventory records

Use this for first-time database setup or complete reset.

```bash
# Initialize database from project root
python database/init_db.py
```
