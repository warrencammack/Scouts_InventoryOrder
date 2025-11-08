"""
Badge Matching Service using fuzzy string matching.

This module provides functionality to match detected badge names from Ollama
against the known badge database using fuzzy string matching algorithms.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from rapidfuzz import fuzz, process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BadgeMatch:
    """
    Represents a matched badge with confidence score.

    Attributes:
        badge_id: Database badge ID (e.g., "oas-bushcraft")
        badge_name: Canonical badge name from database
        detected_name: Original detected name from Ollama
        match_score: Fuzzy match score (0-100)
        confidence_score: Combined confidence (0.0-1.0)
        matched: Whether match exceeded threshold
        category: Badge category
    """
    badge_id: str
    badge_name: str
    detected_name: str
    match_score: float
    confidence_score: float
    matched: bool
    category: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert match to dictionary."""
        return {
            "badge_id": self.badge_id,
            "badge_name": self.badge_name,
            "detected_name": self.detected_name,
            "match_score": self.match_score,
            "confidence_score": self.confidence_score,
            "matched": self.matched,
            "category": self.category,
        }

    @property
    def is_high_confidence(self) -> bool:
        """Check if match is high confidence (>= 0.9)."""
        return self.confidence_score >= 0.9

    @property
    def is_low_confidence(self) -> bool:
        """Check if match is low confidence (< 0.8)."""
        return self.confidence_score < 0.8


class BadgeMatcherService:
    """
    Service for matching detected badge names to database entries.

    Uses fuzzy string matching (rapidfuzz) to handle variations in badge names
    detected by the vision model.
    """

    def __init__(
        self,
        badges: dict[str, dict],
        min_match_score: float = 80.0,
        category_boost: float = 5.0,
    ):
        """
        Initialize the badge matcher service.

        Args:
            badges: Dictionary of badges {badge_id: {name, category, ...}}
            min_match_score: Minimum fuzzy match score (0-100) to consider valid
            category_boost: Score boost for matches within same category
        """
        self.badges = badges
        self.min_match_score = min_match_score
        self.category_boost = category_boost

        # Build search index
        self.badge_names = {
            badge_id: badge_data["name"]
            for badge_id, badge_data in badges.items()
        }

        # Build normalized names for better matching
        self.normalized_names = {
            badge_id: self._normalize_name(name)
            for badge_id, name in self.badge_names.items()
        }

        # Build abbreviation mappings
        self.abbreviations = self._build_abbreviation_map()

        logger.info(f"Initialized BadgeMatcherService with {len(badges)} badges")

    def _normalize_name(self, name: str) -> str:
        """
        Normalize badge name for matching.

        - Convert to lowercase
        - Remove special characters
        - Standardize spacing
        - Handle common variations

        Args:
            name: Badge name to normalize

        Returns:
            Normalized name string
        """
        # Convert to lowercase
        normalized = name.lower()

        # Handle common abbreviations and variations
        replacements = {
            "oas": "outdoor adventure skills",
            "sia": "special interest area",
            "&": "and",
            "stage 1": "1",
            "stage 2": "2",
            "stage 3": "3",
            "stage 4": "4",
            "level 1": "1",
            "level 2": "2",
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        # Remove special characters except spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)

        # Standardize spacing
        normalized = ' '.join(normalized.split())

        return normalized

    def _build_abbreviation_map(self) -> dict[str, list[str]]:
        """
        Build mapping of common abbreviations to full badge IDs.

        Returns:
            Dictionary mapping abbreviations to badge IDs
        """
        abbrev_map = {}

        for badge_id, badge_data in self.badges.items():
            name = badge_data["name"]

            # OAS badges
            if "OAS" in name:
                # Extract discipline (e.g., "Bushcraft" from "OAS Bushcraft")
                parts = name.split()
                if len(parts) >= 2:
                    discipline = parts[1].lower()
                    abbrev_map[f"oas{discipline}"] = badge_id
                    abbrev_map[f"oas {discipline}"] = badge_id

            # SIA badges
            if "SIA" in name:
                abbrev_map[name.lower()] = badge_id
                # Also map without "SIA"
                name_without_sia = name.replace("SIA", "").strip().lower()
                abbrev_map[name_without_sia] = badge_id

            # Milestone badges
            if "Milestone" in name:
                # Map "milestone 1", "m1", etc.
                if "1" in name:
                    abbrev_map["milestone1"] = badge_id
                    abbrev_map["m1"] = badge_id
                elif "2" in name:
                    abbrev_map["milestone2"] = badge_id
                    abbrev_map["m2"] = badge_id
                elif "3" in name:
                    abbrev_map["milestone3"] = badge_id
                    abbrev_map["m3"] = badge_id

        return abbrev_map

    def _check_abbreviation(self, detected_name: str) -> Optional[str]:
        """
        Check if detected name matches a known abbreviation.

        Args:
            detected_name: Name detected by Ollama

        Returns:
            Badge ID if abbreviation found, None otherwise
        """
        normalized = detected_name.lower().replace(" ", "")

        # Check exact abbreviation matches
        for abbrev, badge_id in self.abbreviations.items():
            if normalized == abbrev.replace(" ", ""):
                logger.debug(f"Found abbreviation match: {detected_name} -> {badge_id}")
                return badge_id

        return None

    def match_badge_name(
        self,
        detected_name: str,
        ollama_confidence: float = 0.75,
        category_hint: Optional[str] = None,
    ) -> BadgeMatch:
        """
        Match a detected badge name to the database.

        Uses fuzzy string matching with the following strategy:
        1. Check for exact abbreviation matches
        2. Normalize both detected and database names
        3. Use fuzzy matching to find best match
        4. Boost score if category matches
        5. Combine Ollama confidence with match score

        Args:
            detected_name: Badge name from Ollama detection
            ollama_confidence: Confidence from Ollama (0.0-1.0)
            category_hint: Optional category hint for boosting

        Returns:
            BadgeMatch object with match details
        """
        logger.info(f"Matching: '{detected_name}'")

        # Check for abbreviation match first
        abbrev_match = self._check_abbreviation(detected_name)
        if abbrev_match:
            badge_data = self.badges[abbrev_match]
            return BadgeMatch(
                badge_id=abbrev_match,
                badge_name=badge_data["name"],
                detected_name=detected_name,
                match_score=100.0,
                confidence_score=min(ollama_confidence * 1.1, 1.0),  # Boost for exact match
                matched=True,
                category=badge_data.get("category"),
            )

        # Normalize detected name
        normalized_detected = self._normalize_name(detected_name)

        # Perform fuzzy matching against all badges
        best_match = None
        best_score = 0.0

        for badge_id, normalized_name in self.normalized_names.items():
            # Calculate fuzzy match score using multiple algorithms
            token_sort_score = fuzz.token_sort_ratio(normalized_detected, normalized_name)
            token_set_score = fuzz.token_set_ratio(normalized_detected, normalized_name)
            partial_score = fuzz.partial_ratio(normalized_detected, normalized_name)

            # Use weighted average of scores
            score = (token_sort_score * 0.5 + token_set_score * 0.3 + partial_score * 0.2)

            # Apply category boost if applicable
            if category_hint:
                badge_category = self.badges[badge_id].get("category", "")
                if category_hint.lower() in badge_category.lower():
                    score += self.category_boost
                    logger.debug(f"Applied category boost to {badge_id}: {score}")

            if score > best_score:
                best_score = score
                best_match = badge_id

        # Check if match meets minimum threshold
        matched = best_score >= self.min_match_score

        # Combine Ollama confidence with match score
        # Match score is 0-100, normalize to 0-1
        match_confidence = best_score / 100.0
        combined_confidence = (ollama_confidence * 0.4 + match_confidence * 0.6)

        badge_data = self.badges[best_match] if best_match else None

        if matched and badge_data:
            logger.info(
                f"Matched '{detected_name}' -> '{badge_data['name']}' "
                f"(score: {best_score:.1f}, confidence: {combined_confidence:.2f})"
            )

            return BadgeMatch(
                badge_id=best_match,
                badge_name=badge_data["name"],
                detected_name=detected_name,
                match_score=best_score,
                confidence_score=combined_confidence,
                matched=True,
                category=badge_data.get("category"),
            )
        else:
            logger.warning(
                f"No match found for '{detected_name}' "
                f"(best score: {best_score:.1f}, threshold: {self.min_match_score})"
            )

            return BadgeMatch(
                badge_id="",
                badge_name="",
                detected_name=detected_name,
                match_score=best_score,
                confidence_score=combined_confidence,
                matched=False,
                category=None,
            )

    def match_batch(
        self,
        detections: list[tuple[str, float]],
        category_hint: Optional[str] = None,
    ) -> list[BadgeMatch]:
        """
        Match multiple detected badge names.

        Args:
            detections: List of (name, confidence) tuples
            category_hint: Optional category hint for all matches

        Returns:
            List of BadgeMatch objects
        """
        matches = []
        for name, confidence in detections:
            match = self.match_badge_name(name, confidence, category_hint)
            matches.append(match)

        return matches

    def get_badge_suggestions(
        self,
        partial_name: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Get badge name suggestions for partial input.

        Useful for autocomplete/search functionality.

        Args:
            partial_name: Partial badge name
            limit: Maximum number of suggestions

        Returns:
            List of badge suggestions with scores
        """
        normalized_partial = self._normalize_name(partial_name)

        # Use rapidfuzz to find top matches
        results = process.extract(
            normalized_partial,
            self.normalized_names,
            scorer=fuzz.token_sort_ratio,
            limit=limit,
        )

        suggestions = []
        for normalized_name, score, badge_id in results:
            badge_data = self.badges[badge_id]
            suggestions.append({
                "badge_id": badge_id,
                "name": badge_data["name"],
                "category": badge_data.get("category"),
                "score": score,
            })

        return suggestions


# Convenience function
def match_badge_name(
    detected_name: str,
    badges: dict[str, dict],
    ollama_confidence: float = 0.75,
    min_score: float = 80.0,
) -> BadgeMatch:
    """
    Convenience function to match a single badge name.

    Args:
        detected_name: Badge name from detection
        badges: Badge database dictionary
        ollama_confidence: Confidence from Ollama
        min_score: Minimum match score threshold

    Returns:
        BadgeMatch object

    Example:
        >>> badges = load_badges_from_database()
        >>> match = match_badge_name("OAS Bush", badges)
        >>> if match.matched:
        ...     print(f"Matched to: {match.badge_name}")
    """
    matcher = BadgeMatcherService(badges, min_match_score=min_score)
    return matcher.match_badge_name(detected_name, ollama_confidence)
