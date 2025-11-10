#!/bin/bash
# Scout Badge Inventory - Database Backup Script
# Creates timestamped backups of the SQLite database

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="$PROJECT_ROOT/database/inventory.db"
BACKUP_DIR="$PROJECT_ROOT/backups"
MAX_BACKUPS=10

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Scout Badge Inventory - Database Backup${NC}"
echo "========================================="

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo -e "${RED}Error: Database file not found at $DB_FILE${NC}"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/inventory_backup_$TIMESTAMP.db"

# Create backup
echo -e "\n${YELLOW}Creating backup...${NC}"
cp "$DB_FILE" "$BACKUP_FILE"

# Get file sizes
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo -e "${GREEN}Backup created successfully!${NC}"
echo "Original: $DB_FILE ($DB_SIZE)"
echo "Backup:   $BACKUP_FILE ($BACKUP_SIZE)"

# Clean up old backups (keep only last MAX_BACKUPS)
echo -e "\n${YELLOW}Cleaning up old backups...${NC}"
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/inventory_backup_*.db 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    echo "Found $BACKUP_COUNT backups, keeping last $MAX_BACKUPS"
    ls -1t "$BACKUP_DIR"/inventory_backup_*.db | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
    echo -e "${GREEN}Old backups cleaned up${NC}"
else
    echo "Found $BACKUP_COUNT backups (under limit of $MAX_BACKUPS)"
fi

# List current backups
echo -e "\n${GREEN}Current backups:${NC}"
ls -lht "$BACKUP_DIR"/inventory_backup_*.db 2>/dev/null | head -n "$MAX_BACKUPS" || echo "No backups found"

echo -e "\n${GREEN}Done!${NC}"
