"""
Badge Recognition Service using Ollama LLaVA model.

This module provides badge detection functionality using the Ollama llava:7b
vision model with context-rich prompts optimized through testing (ACTION-103).
"""

import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BadgeDetection:
    """
    Represents a single badge detection result.

    Attributes:
        badge_name: Name of the detected badge
        count: Number of badges detected
        confidence: Detection confidence level (high/medium/low)
        confidence_score: Numeric confidence score (0.0-1.0)
    """
    badge_name: str
    count: int
    confidence: str
    confidence_score: float

    def to_dict(self) -> dict:
        """Convert detection to dictionary."""
        return {
            "badge_name": self.badge_name,
            "count": self.count,
            "confidence": self.confidence,
            "confidence_score": self.confidence_score,
        }


@dataclass
class DetectionResult:
    """
    Complete detection result for an image.

    Attributes:
        image_path: Path to the analyzed image
        detections: List of badge detections
        raw_response: Raw response from Ollama
        processing_time: Time taken to process (seconds)
        success: Whether detection was successful
        error: Error message if detection failed
    """
    image_path: str
    detections: list[BadgeDetection]
    raw_response: str
    processing_time: float
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "image_path": self.image_path,
            "detections": [d.to_dict() for d in self.detections],
            "raw_response": self.raw_response,
            "processing_time": self.processing_time,
            "success": self.success,
            "error": self.error,
        }


class BadgeRecognitionService:
    """
    Service for detecting and counting badges in images using Ollama.

    Uses the llava:7b vision model with optimized prompts based on
    ACTION-103 testing results.
    """

    def __init__(
        self,
        model: str = "llava:7b",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        badge_names: Optional[list[str]] = None,
    ):
        """
        Initialize the badge recognition service.

        Args:
            model: Ollama model to use (default: llava:7b)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            badge_names: List of known badge names for context
        """
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.badge_names = badge_names or []

        logger.info(f"Initialized BadgeRecognitionService with model: {model}")

    def _build_prompt(self) -> str:
        """
        Build the optimized prompt for badge detection.

        Based on ACTION-103 testing, uses context-rich prompt with:
        - Description of badge context (Australian Cub Scout badges)
        - Badge categories and types
        - Known badge names from database
        - Clear output format specification

        Returns:
            Formatted prompt string
        """
        # Convert badge names list to formatted string
        badge_list = ", ".join(self.badge_names) if self.badge_names else "various Australian Cub Scout badges"

        prompt = f"""This is a photo of Australian Cub Scout badges stored in an organizer box.

Australian Cub Scout badges include:
- OAS (Outdoor Adventure Skills) badges with stages 1-4 (Core: Bushcraft, Bushwalking, Pioneering; Specialist: Alpine, Aquatic, Boating, Cycling, Paddling, Vertical)
- Special Interest Area (SIA) badges (hexagonal, purple border): Adventure & Sport, Arts & Literature, Creating a Better World, Environment, Growth & Development, STEM & Innovation
- Milestone badges (circular): Milestone 1, 2, 3
- Achievement badges (various shapes): Art & Design, Entertainer, Handcraft, Musician, Athlete, Swimmer, etc.
- Peak Award: Grey Wolf Award
- Participation badges: Landcare, Local History, Waterwise, Their Service Our Heritage, etc.

Known badge types in our database: {badge_list}

Please carefully identify each type of badge you see in the image and count how many of each type are present.

IMPORTANT: Provide your response in the following format, one badge per line:
Badge Name | Count | Confidence (high/medium/low)

Example:
OAS Bushcraft | 3 | high
Milestone 1 | 2 | medium
Arts & Literature SIA | 1 | high

If you cannot identify any badges clearly, respond with:
No badges detected | 0 | low
"""
        return prompt

    def _parse_response(self, response: str) -> list[BadgeDetection]:
        """
        Parse Ollama response into structured badge detections.

        Handles multiple response formats:
        - Format 1: "Badge Name | Count | Confidence"
        - Format 2: "Badge Name: Count (confidence)"
        - Format 3: Natural language descriptions

        Args:
            response: Raw response from Ollama

        Returns:
            List of BadgeDetection objects
        """
        detections = []

        # Split response into lines
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Try Format 1: Badge Name | Count | Confidence
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    try:
                        badge_name = parts[0]
                        count = int(parts[1])
                        confidence = parts[2].lower()

                        # Convert confidence string to score
                        confidence_score = self._confidence_to_score(confidence)

                        detections.append(BadgeDetection(
                            badge_name=badge_name,
                            count=count,
                            confidence=confidence,
                            confidence_score=confidence_score,
                        ))
                        logger.debug(f"Parsed detection: {badge_name} x{count} ({confidence})")
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Failed to parse line: {line} - {e}")
                        continue

            # Try Format 2: Badge Name: Count (confidence)
            elif ':' in line:
                match = re.search(r'(.+?):\s*(\d+)\s*\((\w+)\)', line)
                if match:
                    badge_name = match.group(1).strip()
                    count = int(match.group(2))
                    confidence = match.group(3).lower()
                    confidence_score = self._confidence_to_score(confidence)

                    detections.append(BadgeDetection(
                        badge_name=badge_name,
                        count=count,
                        confidence=confidence,
                        confidence_score=confidence_score,
                    ))
                    logger.debug(f"Parsed detection: {badge_name} x{count} ({confidence})")

            # Try Format 3: Natural language with numbers
            else:
                # Look for patterns like "3 OAS Bushcraft badges" or "2x Milestone 1"
                number_match = re.search(r'(\d+)\s*x?\s+(.+?)(?:\s+badge)?(?:s)?(?:\s|$)', line, re.IGNORECASE)
                if number_match:
                    count = int(number_match.group(1))
                    badge_name = number_match.group(2).strip()

                    # Assign medium confidence for natural language parsing
                    detections.append(BadgeDetection(
                        badge_name=badge_name,
                        count=count,
                        confidence="medium",
                        confidence_score=0.75,
                    ))
                    logger.debug(f"Parsed detection from natural language: {badge_name} x{count}")

        return detections

    def _confidence_to_score(self, confidence: str) -> float:
        """
        Convert confidence string to numeric score.

        Args:
            confidence: Confidence level (high/medium/low)

        Returns:
            Numeric score between 0.0 and 1.0
        """
        confidence_map = {
            "high": 0.9,
            "medium": 0.75,
            "low": 0.5,
        }
        return confidence_map.get(confidence.lower(), 0.6)

    def detect_badges(self, image_path: str) -> DetectionResult:
        """
        Detect badges in a single image.

        Args:
            image_path: Path to the image file

        Returns:
            DetectionResult containing all detections and metadata
        """
        start_time = time.time()
        image_path_obj = Path(image_path)

        # Validate image exists
        if not image_path_obj.exists():
            logger.error(f"Image not found: {image_path}")
            return DetectionResult(
                image_path=image_path,
                detections=[],
                raw_response="",
                processing_time=0.0,
                success=False,
                error=f"Image not found: {image_path}",
            )

        # Build prompt
        prompt = self._build_prompt()

        # Try detection with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} - Processing: {image_path_obj.name}")

                # Call Ollama
                response = ollama.chat(
                    model=self.model,
                    messages=[{
                        'role': 'user',
                        'content': prompt,
                        'images': [str(image_path_obj.absolute())]
                    }]
                )

                # Extract response text
                response_text = response['message']['content']
                logger.info(f"Received response from Ollama ({len(response_text)} chars)")
                logger.debug(f"Response: {response_text[:200]}...")

                # Parse response
                detections = self._parse_response(response_text)

                processing_time = time.time() - start_time

                logger.info(f"Detected {len(detections)} badge types in {processing_time:.2f}s")

                return DetectionResult(
                    image_path=image_path,
                    detections=detections,
                    raw_response=response_text,
                    processing_time=processing_time,
                    success=True,
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)

        # All retries failed
        processing_time = time.time() - start_time
        logger.error(f"All {self.max_retries} attempts failed for {image_path}")

        return DetectionResult(
            image_path=image_path,
            detections=[],
            raw_response="",
            processing_time=processing_time,
            success=False,
            error=f"Failed after {self.max_retries} attempts: {last_error}",
        )

    async def detect_badges_batch(
        self,
        image_paths: list[str],
        progress_callback: Optional[callable] = None,
    ) -> list[DetectionResult]:
        """
        Detect badges in multiple images with progress tracking.

        Args:
            image_paths: List of image file paths
            progress_callback: Optional callback function(current, total, result)

        Returns:
            List of DetectionResult objects
        """
        results = []
        total = len(image_paths)

        logger.info(f"Starting batch processing of {total} images")

        for idx, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {idx}/{total}")

            result = self.detect_badges(image_path)
            results.append(result)

            # Call progress callback if provided
            if progress_callback:
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(idx, total, result)
                    else:
                        progress_callback(idx, total, result)
                except Exception as e:
                    logger.warning(f"Progress callback failed: {e}")

        logger.info(f"Batch processing complete: {total} images processed")
        return results


# Convenience function for simple usage
def detect_badges(
    image_path: str,
    badge_names: Optional[list[str]] = None,
    model: str = "llava:7b",
) -> DetectionResult:
    """
    Convenience function to detect badges in a single image.

    Args:
        image_path: Path to the image file
        badge_names: Optional list of known badge names
        model: Ollama model to use

    Returns:
        DetectionResult with all detections

    Example:
        >>> result = detect_badges("path/to/image.jpg")
        >>> for detection in result.detections:
        ...     print(f"{detection.badge_name}: {detection.count}")
    """
    service = BadgeRecognitionService(model=model, badge_names=badge_names)
    return service.detect_badges(image_path)


# For async batch processing
import asyncio


async def detect_badges_batch(
    image_paths: list[str],
    badge_names: Optional[list[str]] = None,
    model: str = "llava:7b",
    progress_callback: Optional[callable] = None,
) -> list[DetectionResult]:
    """
    Convenience function to detect badges in multiple images.

    Args:
        image_paths: List of image file paths
        badge_names: Optional list of known badge names
        model: Ollama model to use
        progress_callback: Optional callback for progress updates

    Returns:
        List of DetectionResult objects

    Example:
        >>> results = await detect_badges_batch([
        ...     "image1.jpg",
        ...     "image2.jpg",
        ... ])
    """
    service = BadgeRecognitionService(model=model, badge_names=badge_names)
    return await service.detect_badges_batch(image_paths, progress_callback)
