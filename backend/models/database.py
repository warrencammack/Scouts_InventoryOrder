"""
SQLAlchemy database models for Scout Badge Inventory application.

This module defines all database tables using SQLAlchemy 2.0 declarative style.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class ScanStatus(PyEnum):
    """Enumeration of possible scan statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Badge(Base):
    """
    Badge model representing a Cub Scout badge.

    Stores information about each badge type including name, category,
    description, and links to reference images and purchase URLs.
    """

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    scoutshop_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    size_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    placement: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    inventory: Mapped[Optional["Inventory"]] = relationship(
        "Inventory", back_populates="badge", uselist=False, cascade="all, delete-orphan"
    )
    detections: Mapped[list["BadgeDetection"]] = relationship(
        "BadgeDetection", back_populates="badge", cascade="all, delete-orphan"
    )
    adjustments: Mapped[list["InventoryAdjustment"]] = relationship(
        "InventoryAdjustment", back_populates="badge", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_badge_category", "category"),
        Index("idx_badge_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<Badge(id={self.id}, badge_id='{self.badge_id}', name='{self.name}', category='{self.category}')>"


class Inventory(Base):
    """
    Inventory model tracking current stock levels for each badge.

    Maintains quantity counts and reorder thresholds for inventory management.
    """

    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_threshold: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    badge: Mapped["Badge"] = relationship("Badge", back_populates="inventory")

    # Indexes
    __table_args__ = (
        Index("idx_inventory_badge", "badge_id"),
        Index("idx_inventory_quantity", "quantity"),
    )

    @property
    def is_low_stock(self) -> bool:
        """Check if inventory is below reorder threshold."""
        return self.quantity <= self.reorder_threshold

    def __repr__(self) -> str:
        return f"<Inventory(id={self.id}, badge_id={self.badge_id}, quantity={self.quantity}, threshold={self.reorder_threshold})>"


class Scan(Base):
    """
    Scan model representing a batch upload and processing session.

    Tracks the overall status and metadata for a set of images being processed.
    """

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False, index=True
    )
    total_images: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_images: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    progress_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    images: Mapped[list["ScanImage"]] = relationship(
        "ScanImage", back_populates="scan", cascade="all, delete-orphan"
    )
    adjustments: Mapped[list["InventoryAdjustment"]] = relationship(
        "InventoryAdjustment", back_populates="scan", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_scan_status", "status"),
        Index("idx_scan_created", "created_at"),
    )

    @property
    def progress_percentage(self) -> float:
        """Calculate processing progress as a percentage."""
        if self.total_images == 0:
            return 0.0
        return (self.processed_images / self.total_images) * 100

    def __repr__(self) -> str:
        return f"<Scan(id={self.id}, status='{self.status.value}', progress={self.progress_percentage:.1f}%)>"


class ScanImage(Base):
    """
    ScanImage model representing an individual uploaded image in a scan.

    Tracks the image file path and processing status for each uploaded image.
    """

    __tablename__ = "scan_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False, index=True
    )

    # Relationships
    scan: Mapped["Scan"] = relationship("Scan", back_populates="images")
    detections: Mapped[list["BadgeDetection"]] = relationship(
        "BadgeDetection", back_populates="scan_image", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_scan_image_scan", "scan_id"),
        Index("idx_scan_image_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<ScanImage(id={self.id}, scan_id={self.scan_id}, status='{self.status.value}')>"


class BadgeDetection(Base):
    """
    BadgeDetection model representing a detected badge in an image.

    Stores the AI detection results including badge identification,
    quantity, and confidence score.
    """

    __tablename__ = "badge_detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("scan_images.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    detected_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    scan_image: Mapped["ScanImage"] = relationship("ScanImage", back_populates="detections")
    badge: Mapped["Badge"] = relationship("Badge", back_populates="detections")

    # Indexes
    __table_args__ = (
        Index("idx_detection_scan_image", "scan_image_id"),
        Index("idx_detection_badge", "badge_id"),
        Index("idx_detection_confidence", "confidence"),
    )

    @property
    def is_high_confidence(self) -> bool:
        """Check if detection confidence is above 90%."""
        return self.confidence >= 0.9

    @property
    def is_low_confidence(self) -> bool:
        """Check if detection confidence is below 70%."""
        return self.confidence < 0.7

    def __repr__(self) -> str:
        return f"<BadgeDetection(id={self.id}, badge_id={self.badge_id}, quantity={self.quantity}, confidence={self.confidence:.2f})>"


class InventoryAdjustment(Base):
    """
    InventoryAdjustment model tracking all inventory changes.

    Maintains an audit trail of inventory modifications including
    the old quantity, new quantity, adjustment amount, and reason.
    """

    __tablename__ = "inventory_adjustments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    badge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    old_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    new_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    adjustment: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    scan_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    badge: Mapped["Badge"] = relationship("Badge", back_populates="adjustments")
    scan: Mapped[Optional["Scan"]] = relationship("Scan", back_populates="adjustments")

    # Indexes
    __table_args__ = (
        Index("idx_adjustment_badge", "badge_id"),
        Index("idx_adjustment_timestamp", "timestamp"),
        Index("idx_adjustment_scan", "scan_id"),
    )

    def __repr__(self) -> str:
        return f"<InventoryAdjustment(id={self.id}, badge_id={self.badge_id}, adjustment={self.adjustment:+d}, reason='{self.reason}')>"


def create_database(database_url: str, echo: bool = False) -> None:
    """
    Create all database tables.

    Args:
        database_url: SQLAlchemy database URL
        echo: If True, log all SQL statements

    Example:
        >>> create_database("sqlite:///database/inventory.db")
    """
    engine = create_engine(database_url, echo=echo)
    Base.metadata.create_all(engine)
    print(f"Database tables created successfully at: {database_url}")
