"""
Inventory API endpoints for Scout Badge Inventory application.

This module provides endpoints for managing badge inventory including
viewing stock levels, updating quantities, manual adjustments, and
batch updates from scan results.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import Session, sessionmaker

from backend.config import DatabaseConfig
from backend.models.database import (
    Badge,
    BadgeDetection,
    Inventory,
    InventoryAdjustment,
    Scan,
    ScanImage,
    ScanStatus,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize database session
engine = create_engine(DatabaseConfig.URL, echo=DatabaseConfig.ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Pydantic request/response models
class BadgeInventoryItem(BaseModel):
    """Inventory information for a single badge."""

    badge_id: str = Field(..., description="Badge identifier")
    name: str = Field(..., description="Badge name")
    category: str = Field(..., description="Badge category")
    quantity: int = Field(..., description="Current quantity in stock")
    reorder_threshold: int = Field(..., description="Reorder threshold")
    is_low_stock: bool = Field(..., description="Whether stock is below threshold")
    image_path: Optional[str] = Field(None, description="Path to badge image")
    scoutshop_url: Optional[str] = Field(None, description="ScoutShop URL")
    last_updated: datetime = Field(..., description="Last inventory update timestamp")
    notes: Optional[str] = Field(None, description="Inventory notes")


class BadgeInventoryDetail(BaseModel):
    """Detailed inventory information for a specific badge."""

    badge_id: str = Field(..., description="Badge identifier")
    name: str = Field(..., description="Badge name")
    category: str = Field(..., description="Badge category")
    description: Optional[str] = Field(None, description="Badge description")
    quantity: int = Field(..., description="Current quantity in stock")
    reorder_threshold: int = Field(..., description="Reorder threshold")
    is_low_stock: bool = Field(..., description="Whether stock is below threshold")
    image_path: Optional[str] = Field(None, description="Path to badge image")
    scoutshop_url: Optional[str] = Field(None, description="ScoutShop URL")
    last_updated: datetime = Field(..., description="Last inventory update timestamp")
    notes: Optional[str] = Field(None, description="Inventory notes")
    recent_adjustments: List["AdjustmentInfo"] = Field(
        default_factory=list,
        description="Recent inventory adjustments (last 10)"
    )


class AdjustmentInfo(BaseModel):
    """Information about an inventory adjustment."""

    id: int = Field(..., description="Adjustment ID")
    old_quantity: int = Field(..., description="Quantity before adjustment")
    new_quantity: int = Field(..., description="Quantity after adjustment")
    adjustment: int = Field(..., description="Change amount (positive or negative)")
    reason: str = Field(..., description="Reason for adjustment")
    timestamp: datetime = Field(..., description="When adjustment was made")
    scan_id: Optional[int] = Field(None, description="Associated scan ID if from scan")


class InventoryListResponse(BaseModel):
    """Response model for inventory list."""

    total_items: int = Field(..., description="Total number of badge types")
    low_stock_count: int = Field(..., description="Number of badges with low stock")
    items: List[BadgeInventoryItem] = Field(..., description="Inventory items")


class UpdateQuantityRequest(BaseModel):
    """Request model for updating inventory quantity."""

    quantity: int = Field(..., ge=0, description="New quantity (must be >= 0)")
    reason: str = Field(
        default="Manual update",
        description="Reason for the update"
    )


class UpdateQuantityResponse(BaseModel):
    """Response model for quantity update."""

    badge_id: str = Field(..., description="Badge identifier")
    name: str = Field(..., description="Badge name")
    old_quantity: int = Field(..., description="Previous quantity")
    new_quantity: int = Field(..., description="New quantity")
    adjustment: int = Field(..., description="Change amount")
    last_updated: datetime = Field(..., description="Update timestamp")


class ManualAdjustmentRequest(BaseModel):
    """Request model for manual inventory adjustment."""

    badge_id: str = Field(..., description="Badge identifier")
    adjustment: int = Field(..., description="Adjustment amount (positive or negative)")
    reason: str = Field(..., min_length=1, description="Reason for adjustment")


class ManualAdjustmentResponse(BaseModel):
    """Response model for manual adjustment."""

    badge_id: str = Field(..., description="Badge identifier")
    name: str = Field(..., description="Badge name")
    old_quantity: int = Field(..., description="Previous quantity")
    new_quantity: int = Field(..., description="New quantity")
    adjustment: int = Field(..., description="Adjustment amount")
    reason: str = Field(..., description="Reason for adjustment")
    timestamp: datetime = Field(..., description="Adjustment timestamp")


class InventoryStatsResponse(BaseModel):
    """Response model for inventory statistics."""

    total_badge_types: int = Field(..., description="Total number of badge types")
    total_quantity: int = Field(..., description="Total quantity across all badges")
    low_stock_count: int = Field(..., description="Number of badges below threshold")
    out_of_stock_count: int = Field(..., description="Number of badges with zero stock")
    by_category: dict = Field(..., description="Breakdown by category")
    last_updated: Optional[datetime] = Field(None, description="Most recent update timestamp")


class UpdateFromScanRequest(BaseModel):
    """Request model for updating inventory from scan results."""

    apply_adjustments: bool = Field(
        default=True,
        description="Whether to actually apply the adjustments (false for preview)"
    )


class ScanInventoryUpdate(BaseModel):
    """Information about a badge update from scan."""

    badge_id: str = Field(..., description="Badge identifier")
    badge_name: str = Field(..., description="Badge name")
    quantity_detected: int = Field(..., description="Quantity detected in scan")
    old_quantity: int = Field(..., description="Current inventory quantity")
    new_quantity: int = Field(..., description="Quantity after update")
    adjustment: int = Field(..., description="Adjustment amount")


class UpdateFromScanResponse(BaseModel):
    """Response model for updating inventory from scan."""

    scan_id: int = Field(..., description="Scan ID")
    updates_applied: bool = Field(..., description="Whether updates were applied")
    total_badges_detected: int = Field(..., description="Total badge types detected")
    total_quantity_added: int = Field(..., description="Total quantity added to inventory")
    updates: List[ScanInventoryUpdate] = Field(..., description="Details of each update")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error type/category")
    message: str = Field(..., description="Detailed error message")
    details: dict = Field(default_factory=dict, description="Additional error details")


@router.get(
    "/inventory",
    response_model=InventoryListResponse,
    summary="Get all inventory",
    description="Retrieve all badge inventory with optional filtering by category and search by name.",
)
async def get_inventory(
    category: Optional[str] = Query(None, description="Filter by badge category"),
    search: Optional[str] = Query(None, description="Search by badge name"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
) -> InventoryListResponse:
    """
    Get all inventory items with optional filtering.

    Args:
        category: Optional category filter
        search: Optional name search
        low_stock_only: If true, only return items below reorder threshold

    Returns:
        InventoryListResponse with all matching inventory items
    """
    db = SessionLocal()

    try:
        # Build query
        query = db.query(Inventory, Badge).join(Badge, Inventory.badge_id == Badge.id)

        # Apply filters
        if category:
            query = query.filter(Badge.category == category)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Badge.name.ilike(search_pattern))

        if low_stock_only:
            query = query.filter(Inventory.quantity <= Inventory.reorder_threshold)

        # Execute query
        results = query.all()

        # Build response items
        items = []
        low_stock_count = 0

        for inventory, badge in results:
            is_low = inventory.is_low_stock
            if is_low:
                low_stock_count += 1

            items.append(BadgeInventoryItem(
                badge_id=badge.badge_id,
                name=badge.name,
                category=badge.category,
                quantity=inventory.quantity,
                reorder_threshold=inventory.reorder_threshold,
                is_low_stock=is_low,
                image_path=badge.image_path,
                scoutshop_url=badge.scoutshop_url,
                last_updated=inventory.last_updated,
                notes=inventory.notes,
            ))

        return InventoryListResponse(
            total_items=len(items),
            low_stock_count=low_stock_count,
            items=items,
        )

    finally:
        db.close()


@router.get(
    "/inventory/{badge_id}",
    response_model=BadgeInventoryDetail,
    summary="Get specific badge inventory",
    description="Retrieve detailed inventory information for a specific badge including recent adjustment history.",
)
async def get_badge_inventory(badge_id: str) -> BadgeInventoryDetail:
    """
    Get detailed inventory information for a specific badge.

    Args:
        badge_id: Badge identifier

    Returns:
        BadgeInventoryDetail with complete badge inventory information

    Raises:
        HTTPException: If badge not found
    """
    db = SessionLocal()

    try:
        # Find badge
        badge = db.query(Badge).filter(Badge.badge_id == badge_id).first()

        if not badge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Badge '{badge_id}' not found",
            )

        # Get inventory
        inventory = db.query(Inventory).filter(Inventory.badge_id == badge.id).first()

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory record not found for badge '{badge_id}'",
            )

        # Get recent adjustments (last 10)
        adjustments = db.query(InventoryAdjustment).filter(
            InventoryAdjustment.badge_id == badge.id
        ).order_by(
            InventoryAdjustment.timestamp.desc()
        ).limit(10).all()

        recent_adjustments = [
            AdjustmentInfo(
                id=adj.id,
                old_quantity=adj.old_quantity,
                new_quantity=adj.new_quantity,
                adjustment=adj.adjustment,
                reason=adj.reason,
                timestamp=adj.timestamp,
                scan_id=adj.scan_id,
            )
            for adj in adjustments
        ]

        return BadgeInventoryDetail(
            badge_id=badge.badge_id,
            name=badge.name,
            category=badge.category,
            description=badge.description,
            quantity=inventory.quantity,
            reorder_threshold=inventory.reorder_threshold,
            is_low_stock=inventory.is_low_stock,
            image_path=badge.image_path,
            scoutshop_url=badge.scoutshop_url,
            last_updated=inventory.last_updated,
            notes=inventory.notes,
            recent_adjustments=recent_adjustments,
        )

    finally:
        db.close()


@router.put(
    "/inventory/{badge_id}",
    response_model=UpdateQuantityResponse,
    summary="Update inventory quantity",
    description="Set a new inventory quantity for a badge and create an adjustment record.",
)
async def update_inventory_quantity(
    badge_id: str,
    request: UpdateQuantityRequest,
) -> UpdateQuantityResponse:
    """
    Update inventory quantity for a badge.

    This endpoint sets the inventory to a specific quantity and creates
    an adjustment record for the change.

    Args:
        badge_id: Badge identifier
        request: Update request with new quantity and reason

    Returns:
        UpdateQuantityResponse with update details

    Raises:
        HTTPException: If badge not found or update fails
    """
    db = SessionLocal()

    try:
        # Start transaction
        # Find badge
        badge = db.query(Badge).filter(Badge.badge_id == badge_id).first()

        if not badge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Badge '{badge_id}' not found",
            )

        # Get inventory
        inventory = db.query(Inventory).filter(Inventory.badge_id == badge.id).first()

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory record not found for badge '{badge_id}'",
            )

        # Store old quantity
        old_quantity = inventory.quantity
        new_quantity = request.quantity
        adjustment = new_quantity - old_quantity

        # Update inventory
        inventory.quantity = new_quantity
        inventory.last_updated = datetime.utcnow()

        # Create adjustment record
        adjustment_record = InventoryAdjustment(
            badge_id=badge.id,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            adjustment=adjustment,
            reason=request.reason,
            timestamp=datetime.utcnow(),
        )
        db.add(adjustment_record)

        # Commit transaction
        db.commit()

        logger.info(
            f"Updated inventory for {badge.name}: {old_quantity} -> {new_quantity} "
            f"({adjustment:+d}), reason: {request.reason}"
        )

        return UpdateQuantityResponse(
            badge_id=badge.badge_id,
            name=badge.name,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            adjustment=adjustment,
            last_updated=inventory.last_updated,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating inventory: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update inventory: {str(e)}",
        )
    finally:
        db.close()


@router.post(
    "/inventory/adjust",
    response_model=ManualAdjustmentResponse,
    summary="Manual inventory adjustment",
    description="Apply a manual adjustment (positive or negative) to badge inventory.",
)
async def manual_inventory_adjustment(
    request: ManualAdjustmentRequest,
) -> ManualAdjustmentResponse:
    """
    Apply a manual inventory adjustment.

    This endpoint adds or subtracts from the current inventory quantity
    and creates an adjustment record.

    Args:
        request: Adjustment request with badge_id, adjustment amount, and reason

    Returns:
        ManualAdjustmentResponse with adjustment details

    Raises:
        HTTPException: If badge not found or adjustment would result in negative quantity
    """
    db = SessionLocal()

    try:
        # Start transaction
        # Find badge
        badge = db.query(Badge).filter(Badge.badge_id == request.badge_id).first()

        if not badge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Badge '{request.badge_id}' not found",
            )

        # Get inventory
        inventory = db.query(Inventory).filter(Inventory.badge_id == badge.id).first()

        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory record not found for badge '{request.badge_id}'",
            )

        # Store old quantity
        old_quantity = inventory.quantity
        new_quantity = old_quantity + request.adjustment

        # Validate new quantity
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Adjustment of {request.adjustment:+d} would result in negative quantity "
                       f"({old_quantity} + {request.adjustment} = {new_quantity})",
            )

        # Update inventory
        inventory.quantity = new_quantity
        inventory.last_updated = datetime.utcnow()

        # Create adjustment record
        adjustment_record = InventoryAdjustment(
            badge_id=badge.id,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            adjustment=request.adjustment,
            reason=request.reason,
            timestamp=datetime.utcnow(),
        )
        db.add(adjustment_record)

        # Commit transaction
        db.commit()

        logger.info(
            f"Manual adjustment for {badge.name}: {old_quantity} -> {new_quantity} "
            f"({request.adjustment:+d}), reason: {request.reason}"
        )

        return ManualAdjustmentResponse(
            badge_id=badge.badge_id,
            name=badge.name,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            adjustment=request.adjustment,
            reason=request.reason,
            timestamp=adjustment_record.timestamp,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error applying manual adjustment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply adjustment: {str(e)}",
        )
    finally:
        db.close()


@router.get(
    "/inventory/stats",
    response_model=InventoryStatsResponse,
    summary="Get inventory statistics",
    description="Retrieve overall inventory statistics including totals and breakdown by category.",
)
async def get_inventory_stats() -> InventoryStatsResponse:
    """
    Get inventory statistics.

    Returns overall inventory metrics including total badge types,
    total quantity, low stock count, and breakdown by category.

    Returns:
        InventoryStatsResponse with statistics
    """
    db = SessionLocal()

    try:
        # Get all inventory items with badges
        items = db.query(Inventory, Badge).join(Badge, Inventory.badge_id == Badge.id).all()

        # Calculate statistics
        total_badge_types = len(items)
        total_quantity = sum(inv.quantity for inv, _ in items)
        low_stock_count = sum(1 for inv, _ in items if inv.is_low_stock)
        out_of_stock_count = sum(1 for inv, _ in items if inv.quantity == 0)

        # Get most recent update timestamp
        last_updated = None
        if items:
            last_updated = max(inv.last_updated for inv, _ in items)

        # Calculate by-category breakdown
        by_category = {}
        for inv, badge in items:
            if badge.category not in by_category:
                by_category[badge.category] = {
                    "badge_types": 0,
                    "total_quantity": 0,
                    "low_stock_count": 0,
                    "out_of_stock_count": 0,
                }

            by_category[badge.category]["badge_types"] += 1
            by_category[badge.category]["total_quantity"] += inv.quantity

            if inv.is_low_stock:
                by_category[badge.category]["low_stock_count"] += 1

            if inv.quantity == 0:
                by_category[badge.category]["out_of_stock_count"] += 1

        return InventoryStatsResponse(
            total_badge_types=total_badge_types,
            total_quantity=total_quantity,
            low_stock_count=low_stock_count,
            out_of_stock_count=out_of_stock_count,
            by_category=by_category,
            last_updated=last_updated,
        )

    finally:
        db.close()


@router.post(
    "/inventory/update-from-scan/{scan_id}",
    response_model=UpdateFromScanResponse,
    summary="Update inventory from scan results",
    description="Update inventory based on badges detected in a completed scan.",
)
async def update_inventory_from_scan(
    scan_id: int,
    request: UpdateFromScanRequest = UpdateFromScanRequest(),
) -> UpdateFromScanResponse:
    """
    Update inventory from scan results.

    This endpoint retrieves all badge detections from a completed scan
    and updates inventory accordingly. Each detected badge quantity is
    added to the current inventory with an adjustment record.

    Args:
        scan_id: ID of the completed scan
        request: Optional request to preview without applying

    Returns:
        UpdateFromScanResponse with update details

    Raises:
        HTTPException: If scan not found or not completed
    """
    db = SessionLocal()

    try:
        # Start transaction
        # Get scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()

        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found",
            )

        # Check scan is completed
        if scan.status != ScanStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scan {scan_id} is not completed (status: {scan.status.value})",
            )

        # Get all scan images
        scan_images = db.query(ScanImage).filter(ScanImage.scan_id == scan_id).all()

        # Get all detections from the scan
        detections_query = db.query(BadgeDetection, Badge, Inventory).join(
            Badge, BadgeDetection.badge_id == Badge.id
        ).join(
            Inventory, Inventory.badge_id == Badge.id
        ).filter(
            BadgeDetection.scan_image_id.in_([img.id for img in scan_images])
        )

        detections = detections_query.all()

        # Aggregate quantities by badge
        badge_quantities = {}
        for detection, badge, inventory in detections:
            if badge.badge_id not in badge_quantities:
                badge_quantities[badge.badge_id] = {
                    "badge": badge,
                    "inventory": inventory,
                    "quantity": 0,
                }
            badge_quantities[badge.badge_id]["quantity"] += detection.quantity

        # Prepare updates
        updates = []
        total_quantity_added = 0

        for badge_id, data in badge_quantities.items():
            badge = data["badge"]
            inventory = data["inventory"]
            quantity_detected = data["quantity"]

            old_quantity = inventory.quantity
            adjustment = quantity_detected
            new_quantity = old_quantity + adjustment

            updates.append(ScanInventoryUpdate(
                badge_id=badge.badge_id,
                badge_name=badge.name,
                quantity_detected=quantity_detected,
                old_quantity=old_quantity,
                new_quantity=new_quantity,
                adjustment=adjustment,
            ))

            total_quantity_added += adjustment

            # Apply updates if requested
            if request.apply_adjustments:
                # Update inventory
                inventory.quantity = new_quantity
                inventory.last_updated = datetime.utcnow()

                # Create adjustment record
                adjustment_record = InventoryAdjustment(
                    badge_id=badge.id,
                    old_quantity=old_quantity,
                    new_quantity=new_quantity,
                    adjustment=adjustment,
                    reason=f"Updated from scan #{scan_id}",
                    timestamp=datetime.utcnow(),
                    scan_id=scan_id,
                )
                db.add(adjustment_record)

                logger.info(
                    f"Scan {scan_id} - Updated {badge.name}: "
                    f"{old_quantity} -> {new_quantity} (+{adjustment})"
                )

        # Commit if applying
        if request.apply_adjustments:
            db.commit()
            logger.info(
                f"Scan {scan_id} - Applied {len(updates)} inventory updates, "
                f"total quantity added: {total_quantity_added}"
            )
        else:
            logger.info(
                f"Scan {scan_id} - Preview mode: {len(updates)} updates would be applied"
            )

        return UpdateFromScanResponse(
            scan_id=scan_id,
            updates_applied=request.apply_adjustments,
            total_badges_detected=len(updates),
            total_quantity_added=total_quantity_added,
            updates=updates,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating inventory from scan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update inventory from scan: {str(e)}",
        )
    finally:
        db.close()
