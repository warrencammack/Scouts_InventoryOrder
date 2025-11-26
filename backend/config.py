"""
Configuration management for Scout Badge Inventory backend.

This module loads environment variables and provides configuration
settings for the application.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
BACKEND_DIR = Path(__file__).parent


class DatabaseConfig:
    """Database configuration settings."""

    URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/database/inventory.db"
    )
    ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"


class OllamaConfig:
    """Ollama AI model configuration settings."""

    HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    MODEL: str = os.getenv("OLLAMA_MODEL", "llava:7b")
    TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "240"))  # Doubled from 120 to 240 seconds


class UploadConfig:
    """File upload configuration settings."""

    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".heic"}

    @classmethod
    def ensure_upload_dir(cls) -> None:
        """Ensure the upload directory exists."""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class APIConfig:
    """API server configuration settings."""

    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    RELOAD: bool = os.getenv("API_RELOAD", "False").lower() == "true"

    # CORS settings
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # API metadata
    TITLE: str = "Scout Badge Inventory API"
    DESCRIPTION: str = "AI-powered badge inventory tracking system for Australian Cub Scouts"
    VERSION: str = "1.0.0"


class BadgeConfig:
    """Badge data configuration settings."""

    BADGE_DATA_PATH: Path = BASE_DIR / "data" / "badges_list.json"
    BADGE_IMAGES_DIR: Path = BASE_DIR / "data" / "badges"
    SCOUTSHOP_URLS_PATH: Path = BASE_DIR / "data" / "scoutshop_urls.json"
    DEFAULT_REORDER_THRESHOLD: int = int(
        os.getenv("DEFAULT_REORDER_THRESHOLD", "5")
    )


# Initialize upload directory on import
UploadConfig.ensure_upload_dir()
