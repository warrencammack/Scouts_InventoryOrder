"""
Database initialization script for Scout Badge Inventory application.

This script creates all database tables and optionally loads initial badge data.
"""

import json
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import BadgeConfig, DatabaseConfig
from backend.models.database import Badge, Base, Inventory


def create_tables(database_url: str, echo: bool = False) -> None:
    """
    Create all database tables.

    Args:
        database_url: SQLAlchemy database URL
        echo: If True, log all SQL statements
    """
    print(f"Creating database tables at: {database_url}")
    engine = create_engine(database_url, echo=echo)
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")


def load_badge_data(
    database_url: str,
    badge_data_path: Path,
    scoutshop_urls_path: Optional[Path] = None,
    default_threshold: int = 5,
) -> None:
    """
    Load badge data from JSON file into the database.

    Args:
        database_url: SQLAlchemy database URL
        badge_data_path: Path to badges_list.json file
        scoutshop_urls_path: Optional path to scoutshop_urls.json file
        default_threshold: Default reorder threshold for inventory
    """
    print(f"\nLoading badge data from: {badge_data_path}")

    # Load badge data
    if not badge_data_path.exists():
        print(f"Error: Badge data file not found at {badge_data_path}")
        return

    with open(badge_data_path, "r") as f:
        badges_data = json.load(f)

    print(f"Found {len(badges_data)} badges to load")

    # Load ScoutShop URLs if available
    scoutshop_urls = {}
    if scoutshop_urls_path and scoutshop_urls_path.exists():
        print(f"Loading ScoutShop URLs from: {scoutshop_urls_path}")
        with open(scoutshop_urls_path, "r") as f:
            scoutshop_data = json.load(f)
            # Extract badge URLs from the nested structure
            badge_urls = scoutshop_data.get("badge_product_urls", {})
            for badge_id, url_data in badge_urls.items():
                if isinstance(url_data, dict):
                    # Get the main URL (could be 'url' or 'main_badge')
                    scoutshop_urls[badge_id] = url_data.get("url") or url_data.get("main_badge")
                else:
                    scoutshop_urls[badge_id] = url_data
        print(f"Loaded {len(scoutshop_urls)} ScoutShop URLs")

    # Create database session
    engine = create_engine(database_url)
    session = Session(engine)

    try:
        badges_created = 0
        inventory_created = 0

        for badge_data in badges_data:
            badge_id = badge_data.get("id")

            # Check if badge already exists
            existing_badge = (
                session.query(Badge).filter(Badge.badge_id == badge_id).first()
            )

            if existing_badge:
                print(f"Badge '{badge_id}' already exists, skipping...")
                continue

            # Create badge record
            badge = Badge(
                badge_id=badge_id,
                name=badge_data.get("name"),
                category=badge_data.get("category"),
                description=badge_data.get("description"),
                image_path=f"data/badges/{badge_id}.png",
                scoutshop_url=scoutshop_urls.get(badge_id),
                size_mm=badge_data.get("estimated_size_mm"),
                placement=badge_data.get("placement"),
            )
            session.add(badge)
            session.flush()  # Get the badge.id
            badges_created += 1

            # Create inventory record with default threshold
            inventory = Inventory(
                badge_id=badge.id,
                quantity=0,
                reorder_threshold=default_threshold,
                notes="Initial inventory record",
            )
            session.add(inventory)
            inventory_created += 1

        # Commit all changes
        session.commit()

        print(f"\nSuccessfully created:")
        print(f"  - {badges_created} badge records")
        print(f"  - {inventory_created} inventory records")
        print(f"  - Default reorder threshold: {default_threshold}")

    except Exception as e:
        session.rollback()
        print(f"\nError loading badge data: {e}")
        raise
    finally:
        session.close()


def main() -> None:
    """Main function to initialize the database."""
    print("=" * 60)
    print("Scout Badge Inventory - Database Initialization")
    print("=" * 60)

    # Get database URL from config
    database_url = DatabaseConfig.URL

    # Ensure database directory exists
    db_path = Path(database_url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create tables
    create_tables(database_url, echo=False)

    # Load badge data
    load_badge_data(
        database_url=database_url,
        badge_data_path=BadgeConfig.BADGE_DATA_PATH,
        scoutshop_urls_path=BadgeConfig.SCOUTSHOP_URLS_PATH,
        default_threshold=BadgeConfig.DEFAULT_REORDER_THRESHOLD,
    )

    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print(f"\nDatabase location: {db_path}")
    print(f"Total badges loaded: {len(json.load(open(BadgeConfig.BADGE_DATA_PATH)))}")
    print("\nYou can now start the API server:")
    print("  cd backend")
    print("  python main.py")
    print("\nOr with uvicorn:")
    print("  uvicorn backend.main:app --reload")


if __name__ == "__main__":
    main()
