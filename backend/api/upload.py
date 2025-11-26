"""
Image upload API endpoint for Scout Badge Inventory application.

This module provides the POST /api/upload endpoint for uploading badge images,
with comprehensive validation, error handling, and database integration.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import DatabaseConfig, UploadConfig
from backend.models.database import Scan, ScanImage, ScanStatus

# Initialize router
router = APIRouter()

# Initialize database session
engine = create_engine(DatabaseConfig.URL, echo=DatabaseConfig.ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Pydantic response models
class ImageUploadInfo(BaseModel):
    """Information about an uploaded image."""

    original_filename: str = Field(..., description="Original filename of the uploaded image")
    saved_filename: str = Field(..., description="UUID-based filename saved to disk")
    file_size_bytes: int = Field(..., description="Size of the uploaded file in bytes")
    file_path: str = Field(..., description="Relative path to the saved file")


class UploadResponse(BaseModel):
    """Response model for successful upload."""

    scan_id: int = Field(..., description="Unique identifier for this scan session")
    status: str = Field(..., description="Status of the scan (pending, processing, completed, failed)")
    total_images: int = Field(..., description="Total number of images uploaded")
    images: List[ImageUploadInfo] = Field(..., description="List of uploaded image details")
    created_at: str = Field(..., description="ISO timestamp of scan creation")
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error type/category")
    message: str = Field(..., description="Detailed error message")
    details: dict = Field(default_factory=dict, description="Additional error details")


def validate_file_type(filename: str) -> bool:
    """
    Validate file type based on extension.

    Args:
        filename: Name of the file to validate

    Returns:
        bool: True if file type is valid, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in UploadConfig.ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size is within limits.

    Args:
        file_size: Size of the file in bytes

    Returns:
        bool: True if file size is valid, False otherwise
    """
    return 0 < file_size <= UploadConfig.MAX_FILE_SIZE


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other security issues.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename with only safe characters
    """
    # Get just the filename without any path components
    filename = os.path.basename(filename)

    # Remove any non-alphanumeric characters except dots, hyphens, and underscores
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
    sanitized = "".join(c if c in safe_chars else "_" for c in filename)

    return sanitized


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename using UUID while preserving the file extension.

    Args:
        original_filename: Original filename with extension

    Returns:
        str: UUID-based filename with original extension
    """
    file_ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4()
    return f"{unique_id}{file_ext}"


async def save_uploaded_file(file: UploadFile, save_path: Path) -> int:
    """
    Save uploaded file to disk and return its size.

    Args:
        file: FastAPI UploadFile object
        save_path: Path where the file should be saved

    Returns:
        int: Size of the saved file in bytes

    Raises:
        HTTPException: If file saving fails
    """
    try:
        # Read file contents
        contents = await file.read()
        file_size = len(contents)

        # Write to disk
        with open(save_path, "wb") as f:
            f.write(contents)

        return file_size

    except Exception as e:
        # Clean up partial file if it exists
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload badge images for processing",
    description="Upload one or more badge images to create a new scan session. "
    "Images will be validated, saved securely, and a scan record will be created in the database.",
    responses={
        201: {
            "description": "Images uploaded successfully",
            "model": UploadResponse,
        },
        400: {
            "description": "Bad Request - Invalid file type or no files provided",
            "model": ErrorResponse,
        },
        413: {
            "description": "Payload Too Large - File size exceeds limit",
            "model": ErrorResponse,
        },
        500: {
            "description": "Internal Server Error - Database or file system error",
            "model": ErrorResponse,
        },
    },
)
async def upload_images(
    files: List[UploadFile] = File(
        ...,
        description="List of image files to upload (JPG, JPEG, PNG, HEIC). Max 10MB per file.",
    )
) -> UploadResponse:
    """
    Upload badge images for processing.

    This endpoint accepts multiple image files, validates them, saves them to the
    data/uploads/ directory with unique filenames, and creates corresponding database
    records for tracking the scan and processing.

    Args:
        files: List of uploaded image files

    Returns:
        UploadResponse: Details about the created scan and uploaded images

    Raises:
        HTTPException 400: If no files provided or invalid file types
        HTTPException 413: If any file exceeds size limit
        HTTPException 500: If database or file system operations fail
    """
    # Validate that files were provided
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided. Please upload at least one image.",
        )

    # Ensure upload directory exists
    UploadConfig.ensure_upload_dir()

    # Lists to track processed files and cleanup on error
    uploaded_images: List[ImageUploadInfo] = []
    saved_files: List[Path] = []
    db_session: Session = SessionLocal()

    try:
        # Validate all files first before saving any
        for file in files:
            # Check if file has a filename
            if not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more files have no filename",
                )

            # Validate file type
            if not validate_file_type(file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file type: {file.filename}. "
                    f"Allowed types: {', '.join(UploadConfig.ALLOWED_EXTENSIONS)}",
                )

            # Check file size by reading content length
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Seek back to start

            if not validate_file_size(file_size):
                max_size_mb = UploadConfig.MAX_FILE_SIZE / (1024 * 1024)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large: {file.filename}. "
                    f"Maximum size: {max_size_mb}MB",
                )

        # Create scan record in database
        scan = Scan(
            status=ScanStatus.PENDING,
            total_images=len(files),
            processed_images=0,
            notes=f"Uploaded {len(files)} images",
        )
        db_session.add(scan)
        db_session.flush()  # Get the scan ID without committing

        # Process and save each file
        for file in files:
            # Sanitize and generate unique filename
            sanitized_original = sanitize_filename(file.filename)
            unique_filename = generate_unique_filename(sanitized_original)
            save_path = UploadConfig.UPLOAD_DIR / unique_filename

            # Save file to disk
            file_size = await save_uploaded_file(file, save_path)
            saved_files.append(save_path)

            # Create relative path for database storage (relative to BASE_DIR)
            relative_path = str(save_path.relative_to(UploadConfig.UPLOAD_DIR.parent))

            # Create scan image record
            scan_image = ScanImage(
                scan_id=scan.id,
                image_path=relative_path,
                status=ScanStatus.PENDING,
            )
            db_session.add(scan_image)

            # Add to response list
            uploaded_images.append(
                ImageUploadInfo(
                    original_filename=file.filename,
                    saved_filename=unique_filename,
                    file_size_bytes=file_size,
                    file_path=relative_path,
                )
            )

        # Commit all database changes
        db_session.commit()

        # Return success response
        return UploadResponse(
            scan_id=scan.id,
            status=scan.status.value,
            total_images=scan.total_images,
            images=uploaded_images,
            created_at=scan.created_at.isoformat(),
            message=f"Successfully uploaded {len(files)} image(s). Scan ID: {scan.id}",
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        # Rollback database changes
        db_session.rollback()

        # Clean up any saved files
        for file_path in saved_files:
            if file_path.exists():
                file_path.unlink()

        raise

    except Exception as e:
        # Handle unexpected errors
        db_session.rollback()

        # Clean up any saved files
        for file_path in saved_files:
            if file_path.exists():
                file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during upload: {str(e)}",
        )

    finally:
        # Always close the database session
        db_session.close()


@router.get(
    "/upload/status/{scan_id}",
    summary="Get upload status",
    description="Retrieve the status of a scan by its ID",
    response_model=dict,
)
async def get_upload_status(scan_id: int) -> dict:
    """
    Get the status of a scan by ID.

    Args:
        scan_id: The scan ID to look up

    Returns:
        dict: Scan status information

    Raises:
        HTTPException 404: If scan not found
        HTTPException 500: If database error occurs
    """
    db_session: Session = SessionLocal()

    try:
        scan = db_session.query(Scan).filter(Scan.id == scan_id).first()

        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan with ID {scan_id} not found",
            )

        return {
            "scan_id": scan.id,
            "status": scan.status.value,
            "total_images": scan.total_images,
            "processed_images": scan.processed_images,
            "progress_percentage": scan.progress_percentage,
            "created_at": scan.created_at.isoformat(),
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan status: {str(e)}",
        )

    finally:
        db_session.close()
