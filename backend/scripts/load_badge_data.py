"""
Badge database loader script for Scout Badge Inventory application.

This script loads badge data from JSON files into the database.
It can be used to reload/update badge data without reinitializing the entire database.

Usage:
    python backend/scripts/load_badge_data.py [--clear] [--threshold THRESHOLD]

Options:
    --clear         Clear existing badge and inventory data before loading
    --threshold N   Set default reorder threshold (default: 5)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.config import BadgeConfig, DatabaseConfig
from backend.models.database import Badge, Inventory, InventoryAdjustment


def load_scoutshop_urls(scoutshop_urls_path: Path) -> dict:
    """
    Load ScoutShop URLs from JSON file.

    Args:
        scoutshop_urls_path: Path to scoutshop_urls.json file

    Returns:
        Dictionary mapping badge IDs to product URLs
    """
    if not scoutshop_urls_path.exists():
        print(f"Warning: ScoutShop URLs file not found: {scoutshop_urls_path}")
        return {}

    with open(scoutshop_urls_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract product URLs from the nested structure
    url_mapping = {}
    if "products" in data:
        for badge_id, url_info in data["products"].items():
            if isinstance(url_info, dict) and "url" in url_info:
                url_mapping[badge_id] = url_info["url"]
            elif isinstance(url_info, str):
                url_mapping[badge_id] = url_info

    return url_mapping


def load_badge_data(
    database_url: str,
    badge_data_path: Path,
    scoutshop_urls_path: Optional[Path] = None,
    default_threshold: int = 5,
    clear_existing: bool = False,
) -> tuple[int, int]:
    """
    Load badge data from JSON file into the database.

    Args:
        database_url: SQLAlchemy database URL
        badge_data_path: Path to badges_list.json file
        scoutshop_urls_path: Optional path to scoutshop_urls.json file
        default_threshold: Default reorder threshold for inventory
        clear_existing: If True, clear existing badge and inventory data

    Returns:
        Tuple of (badges_loaded, inventory_created)

    Raises:
        FileNotFoundError: If badge data file doesn't exist
        ValueError: If badge data is invalid
    """
    if not badge_data_path.exists():
        raise FileNotFoundError(f"Badge data file not found: {badge_data_path}")

    # Load badge data
    print(f"Loading badge data from: {badge_data_path}")
    with open(badge_data_path, "r", encoding="utf-8") as f:
        badges_data = json.load(f)

    if not isinstance(badges_data, list):
        raise ValueError("Badge data must be a JSON array")

    # Load ScoutShop URLs if available
    scoutshop_urls = {}
    if scoutshop_urls_path and scoutshop_urls_path.exists():
        print(f"Loading ScoutShop URLs from: {scoutshop_urls_path}")
        scoutshop_urls = load_scoutshop_urls(scoutshop_urls_path)
        print(f"Loaded {len(scoutshop_urls)} ScoutShop URL mappings")

    # Connect to database
    engine = create_engine(database_url)

    badges_loaded = 0
    inventory_created = 0

    with Session(engine) as session:
        try:
            # Clear existing data if requested
            if clear_existing:
                print("Clearing existing badge and inventory data...")
                session.query(InventoryAdjustment).delete()
                session.query(Inventory).delete()
                session.query(Badge).delete()
                session.commit()
                print("Existing data cleared")

            # Load each badge
            for badge_data in badges_data:
                badge_id = badge_data.get("id")
                if not badge_id:
                    print(f"Warning: Skipping badge with no ID: {badge_data.get('name', 'Unknown')}")
                    continue

                # Check if badge already exists
                existing_badge = session.scalar(
                    select(Badge).where(Badge.badge_id == badge_id)
                )

                if existing_badge:
                    # Update existing badge
                    existing_badge.name = badge_data.get("name", existing_badge.name)
                    existing_badge.category = badge_data.get("category", existing_badge.category)
                    existing_badge.description = badge_data.get("description", existing_badge.description)
                    existing_badge.size_mm = badge_data.get("estimated_size_mm", existing_badge.size_mm)
                    existing_badge.placement = badge_data.get("placement", existing_badge.placement)

                    # Update ScoutShop URL if available
                    if badge_id in scoutshop_urls:
                        existing_badge.scoutshop_url = scoutshop_urls[badge_id]

                    print(f"Updated badge: {existing_badge.name}")
                else:
                    # Create new badge
                    badge = Badge(
                        badge_id=badge_id,
                        name=badge_data.get("name", "Unknown Badge"),
                        category=badge_data.get("category", "Unknown"),
                        description=badge_data.get("description", ""),
                        image_path=f"data/badges/{badge_id}.png",
                        scoutshop_url=scoutshop_urls.get(badge_id, ""),
                        size_mm=badge_data.get("estimated_size_mm", 40),
                        placement=badge_data.get("placement", ""),
                    )
                    session.add(badge)
                    badges_loaded += 1
                    print(f"Added badge: {badge.name}")

                    # Create inventory record for new badge
                    session.flush()  # Ensure badge.id is available

                    inventory = Inventory(
                        badge_id=badge.id,
                        quantity=0,
                        reorder_threshold=default_threshold,
                        notes=f"Initialized with threshold {default_threshold}",
                    )
                    session.add(inventory)
                    inventory_created += 1

            # Commit all changes
            session.commit()
            print(f"\n✅ Successfully loaded {badges_loaded} badges")
            print(f"✅ Created {inventory_created} inventory records")

        except Exception as e:
            session.rollback()
            print(f"❌ Error loading badge data: {e}")
            raise

    return badges_loaded, inventory_created


def main():
    """Main entry point for the badge loader script."""
    parser = argparse.ArgumentParser(
        description="Load badge data into the Scout Inventory database"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing badge and inventory data before loading",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Default reorder threshold for inventory (default: 5)",
    )

    args = parser.parse_args()

    # Get paths from config
    database_url = DatabaseConfig.DATABASE_URL
    badge_data_path = BadgeConfig.BADGE_DATA_FILE
    scoutshop_urls_path = BadgeConfig.SCOUTSHOP_URLS_FILE

    print("=" * 60)
    print("Badge Database Loader")
    print("=" * 60)
    print(f"Database: {database_url}")
    print(f"Badge data: {badge_data_path}")
    print(f"ScoutShop URLs: {scoutshop_urls_path}")
    print(f"Default threshold: {args.threshold}")
    print(f"Clear existing: {args.clear}")
    print("=" * 60)

    try:
        badges_loaded, inventory_created = load_badge_data(
            database_url=database_url,
            badge_data_path=badge_data_path,
            scoutshop_urls_path=scoutshop_urls_path,
            default_threshold=args.threshold,
            clear_existing=args.clear,
        )

        print("\n" + "=" * 60)
        print("✅ Badge data loaded successfully!")
        print("=" * 60)
        print(f"Badges loaded: {badges_loaded}")
        print(f"Inventory records created: {inventory_created}")

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Failed to load badge data: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
