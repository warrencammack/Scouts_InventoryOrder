"""
API routers for Scout Badge Inventory application.

This package contains all API endpoint routers.
"""

from backend.api.inventory import router as inventory_router
from backend.api.processing import router as processing_router
from backend.api.upload import router as upload_router

__all__ = ["upload_router", "processing_router", "inventory_router"]
