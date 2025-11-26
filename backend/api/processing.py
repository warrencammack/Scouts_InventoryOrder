"""
Badge processing API endpoints for Scout Badge Inventory application.

This module provides endpoints for processing uploaded images with AI badge detection,
including progress tracking and status monitoring.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import DatabaseConfig, UploadConfig
from backend.models.database import (
    Badge,
    BadgeDetection,
    Scan,
    ScanImage,
    ScanStatus,
)
from backend.services.badge_matcher import BadgeMatcherService
from backend.services.badge_recognition import BadgeRecognitionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize database session
engine = create_engine(DatabaseConfig.URL, echo=DatabaseConfig.ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Pydantic response models
class BadgeDetectionInfo(BaseModel):
    """Information about a detected badge."""

    badge_id: str = Field(..., description="Database badge ID")
    badge_name: str = Field(..., description="Badge name")
    detected_name: str = Field(..., description="Name as detected by AI")
    quantity: int = Field(..., description="Number of badges detected")
    confidence: float = Field(..., description="Detection confidence (0.0-1.0)")
    match_score: float = Field(..., description="Fuzzy match score (0-100)")
    is_low_confidence: bool = Field(..., description="Whether confidence is below 80%")


class ImageProcessingResult(BaseModel):
    """Result of processing a single image."""

    image_id: int = Field(..., description="Database image ID")
    image_path: str = Field(..., description="Path to the image")
    status: str = Field(..., description="Processing status")
    detections: list[BadgeDetectionInfo] = Field(default_factory=list)
    processing_time: float = Field(..., description="Time taken to process (seconds)")
    error: Optional[str] = Field(None, description="Error message if failed")


class ProcessingStatusResponse(BaseModel):
    """Response for processing status check."""

    scan_id: int = Field(..., description="Scan ID")
    status: str = Field(..., description="Overall scan status")
    total_images: int = Field(..., description="Total number of images")
    processed_images: int = Field(..., description="Number of images processed")
    progress_percentage: float = Field(..., description="Processing progress (0-100)")
    progress_message: Optional[str] = Field(None, description="Current progress status message")
    current_image: Optional[str] = Field(None, description="Currently processing image")
    estimated_time_remaining: Optional[float] = Field(None, description="Estimated seconds remaining")
    total_detections: int = Field(..., description="Total badges detected so far")
    results: list[ImageProcessingResult] = Field(default_factory=list)


class ProcessingCompleteResponse(BaseModel):
    """Response when processing is complete."""

    scan_id: int = Field(..., description="Scan ID")
    status: str = Field(..., description="Final scan status")
    total_images: int = Field(..., description="Total images processed")
    total_detections: int = Field(..., description="Total badges detected")
    processing_time: float = Field(..., description="Total processing time (seconds)")
    results: list[ImageProcessingResult] = Field(..., description="All processing results")
    summary: dict = Field(..., description="Summary statistics")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error type/category")
    message: str = Field(..., description="Detailed error message")
    details: dict = Field(default_factory=dict, description="Additional error details")


def load_badges_from_db(db: Session) -> dict[str, dict]:
    """
    Load all badges from database into dictionary format.

    Args:
        db: Database session

    Returns:
        Dictionary mapping badge_id to badge data
    """
    badges = db.query(Badge).all()
    badge_dict = {}

    for badge in badges:
        badge_dict[badge.badge_id] = {
            "id": badge.id,
            "name": badge.name,
            "category": badge.category,
            "description": badge.description,
        }

    return badge_dict


def calculate_estimated_time(
    total_images: int,
    processed_images: int,
    elapsed_time: float,
) -> Optional[float]:
    """
    Calculate estimated time remaining for processing.

    Args:
        total_images: Total number of images to process
        processed_images: Number of images already processed
        elapsed_time: Time elapsed so far (seconds)

    Returns:
        Estimated time remaining in seconds, or None if cannot estimate
    """
    if processed_images == 0:
        return None

    avg_time_per_image = elapsed_time / processed_images
    remaining_images = total_images - processed_images
    return avg_time_per_image * remaining_images


async def process_scan_background(scan_id: int):
    """
    Background task to process all images in a scan.

    Args:
        scan_id: ID of the scan to process
    """
    db = SessionLocal()
    start_time = datetime.utcnow()

    try:
        # Get scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return

        # Update status to processing
        scan.status = ScanStatus.PROCESSING
        scan.progress_message = "Initializing AI badge recognition..."
        db.commit()

        logger.info(f"Starting background processing for scan {scan_id}")

        # Load badges from database
        badges = load_badges_from_db(db)
        badge_names = [b["name"] for b in badges.values()]

        # Initialize services
        recognition_service = BadgeRecognitionService(
            model="llava:7b",
            badge_names=badge_names,
        )
        matcher_service = BadgeMatcherService(badges)

        # Get all images for this scan
        images = db.query(ScanImage).filter(ScanImage.scan_id == scan_id).all()

        total_detections = 0
        successful_images = 0
        failed_images = 0

        for idx, image in enumerate(images, 1):
            try:
                logger.info(f"Processing image {idx}/{len(images)}: {image.image_path}")

                # Update progress message with current image
                scan.progress_message = f"Processing image {idx} of {len(images)}: Analyzing with AI..."
                scan.processed_images = idx - 1  # Update before processing
                db.commit()

                # Update image status
                image.status = ScanStatus.PROCESSING
                db.commit()

                # Detect badges in image
                scan.progress_message = f"Processing image {idx} of {len(images)}: AI analyzing badges..."
                db.commit()

                detection_result = recognition_service.detect_badges(image.image_path)

                if not detection_result.success:
                    logger.error(f"Detection failed for {image.image_path}: {detection_result.error}")
                    scan.progress_message = f"Image {idx} of {len(images)}: Detection failed - {detection_result.error}"
                    image.status = ScanStatus.FAILED
                    failed_images += 1
                    db.commit()
                    continue

                # Process each detection
                scan.progress_message = f"Processing image {idx} of {len(images)}: Matching detected badges..."
                db.commit()
                for detection in detection_result.detections:
                    # Match badge name to database
                    match = matcher_service.match_badge_name(
                        detected_name=detection.badge_name,
                        ollama_confidence=detection.confidence_score,
                    )

                    if match.matched:
                        # Get database badge ID
                        badge = db.query(Badge).filter(
                            Badge.badge_id == match.badge_id
                        ).first()

                        if badge:
                            # Store detection in database
                            badge_detection = BadgeDetection(
                                scan_image_id=image.id,
                                badge_id=badge.id,
                                detected_name=detection.badge_name,
                                quantity=detection.count,
                                confidence=match.confidence_score,
                            )
                            db.add(badge_detection)
                            total_detections += 1

                            logger.info(
                                f"Detected: {badge.name} x{detection.count} "
                                f"(confidence: {match.confidence_score:.2f})"
                            )
                        else:
                            logger.warning(f"Badge {match.badge_id} not found in database")
                    else:
                        logger.warning(
                            f"No match found for '{detection.badge_name}' "
                            f"(score: {match.match_score:.1f})"
                        )

                # Update image status
                image.status = ScanStatus.COMPLETED
                image.processed_at = datetime.utcnow()
                successful_images += 1

                # Update scan progress
                scan.processed_images = idx
                scan.progress_message = f"Completed image {idx} of {len(images)} ({total_detections} badges detected so far)"
                db.commit()

            except Exception as e:
                logger.error(f"Error processing image {image.image_path}: {e}", exc_info=True)
                scan.progress_message = f"Error processing image {idx} of {len(images)}: {str(e)[:100]}"
                image.status = ScanStatus.FAILED
                failed_images += 1
                db.commit()
                # Continue with next image

        # Update final scan status
        if failed_images == len(images):
            scan.status = ScanStatus.FAILED
        elif failed_images > 0:
            scan.status = ScanStatus.COMPLETED  # Partial success
        else:
            scan.status = ScanStatus.COMPLETED

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        logger.info(
            f"Scan {scan_id} processing complete: "
            f"{successful_images} successful, {failed_images} failed, "
            f"{total_detections} total detections, "
            f"{processing_time:.2f}s"
        )

        db.commit()

    except Exception as e:
        logger.error(f"Fatal error processing scan {scan_id}: {e}", exc_info=True)
        scan.status = ScanStatus.FAILED
        db.commit()

    finally:
        db.close()


@router.post(
    "/process/{scan_id}",
    response_model=ProcessingStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start processing a scan",
    description="Initiate badge detection processing for all images in a scan. Processing runs in the background.",
)
async def start_processing(
    scan_id: int,
    background_tasks: BackgroundTasks,
) -> ProcessingStatusResponse:
    """
    Start processing all images in a scan.

    This endpoint initiates background processing of all uploaded images
    using the Ollama vision model for badge detection and fuzzy matching
    to identify badges in the database.

    Args:
        scan_id: ID of the scan to process
        background_tasks: FastAPI background tasks

    Returns:
        ProcessingStatusResponse with initial status

    Raises:
        HTTPException: If scan not found or already processing
    """
    db = SessionLocal()

    try:
        # Get scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()

        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found",
            )

        # Check if already processing or completed
        if scan.status == ScanStatus.PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Scan {scan_id} is already being processed",
            )

        if scan.status == ScanStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Scan {scan_id} has already been processed",
            )

        # Check if scan has images
        if scan.total_images == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scan {scan_id} has no images to process",
            )

        # Schedule background processing
        background_tasks.add_task(process_scan_background, scan_id)

        logger.info(f"Scheduled background processing for scan {scan_id}")

        return ProcessingStatusResponse(
            scan_id=scan.id,
            status=scan.status.value,
            total_images=scan.total_images,
            processed_images=0,
            progress_percentage=0.0,
            progress_message="Starting processing...",
            total_detections=0,
            results=[],
        )

    finally:
        db.close()


@router.get(
    "/process/{scan_id}/status",
    response_model=ProcessingStatusResponse,
    summary="Get processing status",
    description="Get the current processing status and progress for a scan.",
)
async def get_processing_status(scan_id: int) -> ProcessingStatusResponse:
    """
    Get the current processing status for a scan.

    Returns detailed progress information including number of images processed,
    progress percentage, and all detection results so far.

    Args:
        scan_id: ID of the scan to check

    Returns:
        ProcessingStatusResponse with current status

    Raises:
        HTTPException: If scan not found
    """
    db = SessionLocal()

    try:
        # Get scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()

        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found",
            )

        # Get all images and their processing results
        images = db.query(ScanImage).filter(ScanImage.scan_id == scan_id).all()

        results = []
        total_detections = 0
        current_image = None

        for image in images:
            # Get detections for this image
            detections = db.query(BadgeDetection).filter(
                BadgeDetection.scan_image_id == image.id
            ).all()

            detection_infos = []
            for det in detections:
                badge = db.query(Badge).filter(Badge.id == det.badge_id).first()
                if badge:
                    detection_infos.append(BadgeDetectionInfo(
                        badge_id=badge.badge_id,
                        badge_name=badge.name,
                        detected_name=badge.name,  # Could store original detected name
                        quantity=det.quantity,
                        confidence=det.confidence,
                        match_score=det.confidence * 100,
                        is_low_confidence=det.confidence < 0.8,
                    ))
                    total_detections += 1

            # Calculate processing time
            processing_time = 0.0
            if image.processed_at and image.uploaded_at:
                processing_time = (image.processed_at - image.uploaded_at).total_seconds()

            results.append(ImageProcessingResult(
                image_id=image.id,
                image_path=image.image_path,
                status=image.status.value,
                detections=detection_infos,
                processing_time=processing_time,
            ))

            # Track currently processing image
            if image.status == ScanStatus.PROCESSING:
                current_image = Path(image.image_path).name

        # Calculate estimated time remaining
        elapsed_time = (datetime.utcnow() - scan.created_at).total_seconds()
        estimated_time = calculate_estimated_time(
            scan.total_images,
            scan.processed_images,
            elapsed_time,
        )

        return ProcessingStatusResponse(
            scan_id=scan.id,
            status=scan.status.value,
            total_images=scan.total_images,
            processed_images=scan.processed_images,
            progress_percentage=scan.progress_percentage,
            progress_message=scan.progress_message,
            current_image=current_image,
            estimated_time_remaining=estimated_time,
            total_detections=total_detections,
            results=results,
        )

    finally:
        db.close()


@router.get(
    "/process/{scan_id}/results",
    response_model=ProcessingCompleteResponse,
    summary="Get processing results",
    description="Get complete processing results for a finished scan.",
)
async def get_processing_results(scan_id: int) -> ProcessingCompleteResponse:
    """
    Get complete processing results for a scan.

    This endpoint returns all detection results and summary statistics
    for a completed scan. Use this after processing is complete to get
    the final results.

    Args:
        scan_id: ID of the scan

    Returns:
        ProcessingCompleteResponse with all results

    Raises:
        HTTPException: If scan not found or not yet completed
    """
    db = SessionLocal()

    try:
        # Get scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()

        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found",
            )

        # Get all images and their processing results
        images = db.query(ScanImage).filter(ScanImage.scan_id == scan_id).all()

        results = []
        total_detections = 0
        badge_summary = {}
        total_processing_time = 0.0

        for image in images:
            # Get detections for this image
            detections = db.query(BadgeDetection).filter(
                BadgeDetection.scan_image_id == image.id
            ).all()

            detection_infos = []
            for det in detections:
                badge = db.query(Badge).filter(Badge.id == det.badge_id).first()
                if badge:
                    detection_infos.append(BadgeDetectionInfo(
                        badge_id=badge.badge_id,
                        badge_name=badge.name,
                        detected_name=badge.name,
                        quantity=det.quantity,
                        confidence=det.confidence,
                        match_score=det.confidence * 100,
                        is_low_confidence=det.confidence < 0.8,
                    ))
                    total_detections += 1

                    # Update summary
                    if badge.name not in badge_summary:
                        badge_summary[badge.name] = {
                            "badge_id": badge.badge_id,
                            "category": badge.category,
                            "total_quantity": 0,
                            "occurrences": 0,
                        }
                    badge_summary[badge.name]["total_quantity"] += det.quantity
                    badge_summary[badge.name]["occurrences"] += 1

            # Calculate processing time
            processing_time = 0.0
            if image.processed_at and image.uploaded_at:
                processing_time = (image.processed_at - image.uploaded_at).total_seconds()
                total_processing_time += processing_time

            results.append(ImageProcessingResult(
                image_id=image.id,
                image_path=image.image_path,
                status=image.status.value,
                detections=detection_infos,
                processing_time=processing_time,
            ))

        # Build summary
        summary = {
            "total_badge_types": len(badge_summary),
            "total_badges": sum(b["total_quantity"] for b in badge_summary.values()),
            "by_badge": badge_summary,
            "successful_images": len([r for r in results if r.status == "completed"]),
            "failed_images": len([r for r in results if r.status == "failed"]),
        }

        return ProcessingCompleteResponse(
            scan_id=scan.id,
            status=scan.status.value,
            total_images=scan.total_images,
            total_detections=total_detections,
            processing_time=total_processing_time,
            results=results,
            summary=summary,
        )

    finally:
        db.close()


@router.get(
    "/scans/{scan_id}",
    summary="Get scan details",
    description="Retrieve full scan details including images",
)
def getScan(scan_id: int):
    """Get scan details with images."""
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan {scan_id} not found"
            )

        images = db.query(ScanImage).filter(ScanImage.scan_id == scan_id).all()

        return {
            "id": scan.id,
            "status": scan.status.value,
            "total_images": scan.total_images,
            "processed_images": scan.processed_images,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "images": [
                {
                    "id": img.id,
                    "image_path": img.image_path,
                    "status": img.status.value,
                    "uploaded_at": img.uploaded_at.isoformat() if img.uploaded_at else None,
                }
                for img in images
            ]
        }
    finally:
        db.close()


@router.get(
    "/scans/{scan_id}/detections",
    summary="Get scan detections",
    description="Retrieve all badge detections for a scan",
)
def getScanDetections(scan_id: int):
    """Get all detections for a scan."""
    db = SessionLocal()
    try:
        # Get all images for this scan
        images = db.query(ScanImage).filter(ScanImage.scan_id == scan_id).all()

        if not images:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No images found for scan {scan_id}"
            )

        # Get all detections for these images
        all_detections = []
        for image in images:
            detections = db.query(BadgeDetection).filter(
                BadgeDetection.scan_image_id == image.id
            ).all()

            for det in detections:
                badge = db.query(Badge).filter(Badge.id == det.badge_id).first()
                all_detections.append({
                    "id": det.id,
                    "badge_id": badge.id if badge else None,
                    "badge_name": badge.name if badge else det.detected_name,
                    "detected_name": det.detected_name,
                    "quantity": det.quantity,
                    "confidence": det.confidence,
                    "image_id": image.id,
                })

        return all_detections
    finally:
        db.close()
