"""
Timer and score extraction from table region screenshots.

Coordinates extraction of game state values using template matching
with OCR fallback.
"""

from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from PIL import Image

from .template_matcher import TemplateMatcher
from .ocr_fallback import OCRFallback
from ..utils.logger import get_logger

logger = get_logger("image_extractor")


@dataclass
class ExtractionResult:
    """Result of a value extraction attempt."""

    value: Optional[int]
    confidence: float
    method: str  # "template" or "ocr"
    success: bool


@dataclass
class GameState:
    """Extracted game state from a table region."""

    timer: Optional[int]
    blue_score: Optional[int]
    red_score: Optional[int]
    timer_confidence: float
    blue_score_confidence: float
    red_score_confidence: float
    extraction_method: str  # "template", "ocr", or "mixed"


class ImageExtractor:
    """
    Extracts timer and score values from table region screenshots.

    Uses OpenCV template matching as primary method with
    OCR fallback after 3 consecutive failures.
    """

    # Failure threshold for OCR fallback
    OCR_FALLBACK_THRESHOLD = 3

    def __init__(
        self,
        template_matcher: Optional[TemplateMatcher] = None,
        ocr_fallback: Optional[OCRFallback] = None,
    ):
        """
        Initialize image extractor.

        Args:
            template_matcher: Template matcher instance
            ocr_fallback: OCR fallback instance
        """
        self.template_matcher = template_matcher or TemplateMatcher()
        self.ocr_fallback = ocr_fallback or OCRFallback()

        # Track consecutive failures per table for OCR fallback
        self._timer_failures: Dict[int, int] = {}
        self._blue_score_failures: Dict[int, int] = {}
        self._red_score_failures: Dict[int, int] = {}

    def _get_failure_count(
        self,
        failures_dict: Dict[int, int],
        table_id: int,
    ) -> int:
        """Get failure count for a table."""
        return failures_dict.get(table_id, 0)

    def _increment_failure(
        self,
        failures_dict: Dict[int, int],
        table_id: int,
    ) -> int:
        """Increment and return failure count."""
        failures_dict[table_id] = failures_dict.get(table_id, 0) + 1
        return failures_dict[table_id]

    def _reset_failure(
        self,
        failures_dict: Dict[int, int],
        table_id: int,
    ) -> None:
        """Reset failure count for a table."""
        failures_dict[table_id] = 0

    def _should_use_ocr(
        self,
        failures_dict: Dict[int, int],
        table_id: int,
    ) -> bool:
        """Check if OCR should be used based on failure count."""
        return self._get_failure_count(failures_dict, table_id) >= self.OCR_FALLBACK_THRESHOLD

    def extract_timer(
        self,
        timer_image: Image.Image,
        table_id: int,
    ) -> ExtractionResult:
        """
        Extract timer value from timer region image.

        Uses template matching first, falls back to OCR after
        3 consecutive failures.

        Args:
            timer_image: PIL Image of timer region
            table_id: Table ID for tracking failures

        Returns:
            ExtractionResult with value and metadata
        """
        use_ocr = self._should_use_ocr(self._timer_failures, table_id)

        if not use_ocr:
            # Try template matching first
            value, confidence = self.template_matcher.extract_timer(
                timer_image,
                table_id=table_id,
            )

            if value is not None:
                self._reset_failure(self._timer_failures, table_id)
                return ExtractionResult(
                    value=value,
                    confidence=confidence,
                    method="template",
                    success=True,
                )

            # Template matching failed
            failures = self._increment_failure(self._timer_failures, table_id)
            logger.warning(
                f"Timer template matching failed (attempt {failures}/{self.OCR_FALLBACK_THRESHOLD})",
                extra={"table_id": table_id},
            )

            # Check if we should fallback to OCR now
            use_ocr = failures >= self.OCR_FALLBACK_THRESHOLD

        if use_ocr:
            # Use OCR fallback
            logger.info(
                f"Using OCR fallback for timer extraction",
                extra={"table_id": table_id},
            )

            value, confidence = self.ocr_fallback.extract_number(
                timer_image,
                table_id=table_id,
                value_type="timer",
            )

            if value is not None:
                # Validate timer range
                if 0 <= value <= 25:
                    self._reset_failure(self._timer_failures, table_id)
                    return ExtractionResult(
                        value=value,
                        confidence=confidence,
                        method="ocr",
                        success=True,
                    )

        return ExtractionResult(
            value=None,
            confidence=0.0,
            method="ocr" if use_ocr else "template",
            success=False,
        )

    def extract_blue_score(
        self,
        score_image: Image.Image,
        table_id: int,
    ) -> ExtractionResult:
        """
        Extract blue team score from score region image.

        Args:
            score_image: PIL Image of blue score region
            table_id: Table ID for tracking failures

        Returns:
            ExtractionResult with value and metadata
        """
        return self._extract_score(
            score_image=score_image,
            table_id=table_id,
            team="blue",
            failures_dict=self._blue_score_failures,
        )

    def extract_red_score(
        self,
        score_image: Image.Image,
        table_id: int,
    ) -> ExtractionResult:
        """
        Extract red team score from score region image.

        Args:
            score_image: PIL Image of red score region
            table_id: Table ID for tracking failures

        Returns:
            ExtractionResult with value and metadata
        """
        return self._extract_score(
            score_image=score_image,
            table_id=table_id,
            team="red",
            failures_dict=self._red_score_failures,
        )

    def _extract_score(
        self,
        score_image: Image.Image,
        table_id: int,
        team: str,
        failures_dict: Dict[int, int],
    ) -> ExtractionResult:
        """
        Internal method to extract score with fallback logic.

        Args:
            score_image: PIL Image of score region
            table_id: Table ID
            team: "blue" or "red"
            failures_dict: Failure tracking dictionary

        Returns:
            ExtractionResult with value and metadata
        """
        use_ocr = self._should_use_ocr(failures_dict, table_id)

        if not use_ocr:
            # Try template matching first
            value, confidence = self.template_matcher.extract_score(
                score_image,
                table_id=table_id,
                team=team,
            )

            if value is not None:
                self._reset_failure(failures_dict, table_id)
                return ExtractionResult(
                    value=value,
                    confidence=confidence,
                    method="template",
                    success=True,
                )

            # Template matching failed
            failures = self._increment_failure(failures_dict, table_id)
            logger.warning(
                f"{team.capitalize()} score template matching failed "
                f"(attempt {failures}/{self.OCR_FALLBACK_THRESHOLD})",
                extra={"table_id": table_id},
            )

            use_ocr = failures >= self.OCR_FALLBACK_THRESHOLD

        if use_ocr:
            # Use OCR fallback
            logger.info(
                f"Using OCR fallback for {team} score extraction",
                extra={"table_id": table_id},
            )

            value, confidence = self.ocr_fallback.extract_number(
                score_image,
                table_id=table_id,
                value_type=f"{team}_score",
            )

            if value is not None and value >= 0:
                self._reset_failure(failures_dict, table_id)
                return ExtractionResult(
                    value=value,
                    confidence=confidence,
                    method="ocr",
                    success=True,
                )

        return ExtractionResult(
            value=None,
            confidence=0.0,
            method="ocr" if use_ocr else "template",
            success=False,
        )

    def extract_game_state(
        self,
        table_image: Image.Image,
        table_id: int,
        timer_region: Dict[str, int],
        blue_score_region: Dict[str, int],
        red_score_region: Dict[str, int],
    ) -> GameState:
        """
        Extract complete game state from a table region image.

        Args:
            table_image: PIL Image of full table region
            table_id: Table ID
            timer_region: Timer region coordinates {'x', 'y', 'width', 'height'}
            blue_score_region: Blue score region coordinates
            red_score_region: Red score region coordinates

        Returns:
            GameState with all extracted values
        """
        # Crop regions from table image
        timer_image = table_image.crop((
            timer_region["x"],
            timer_region["y"],
            timer_region["x"] + timer_region["width"],
            timer_region["y"] + timer_region["height"],
        ))

        blue_score_image = table_image.crop((
            blue_score_region["x"],
            blue_score_region["y"],
            blue_score_region["x"] + blue_score_region["width"],
            blue_score_region["y"] + blue_score_region["height"],
        ))

        red_score_image = table_image.crop((
            red_score_region["x"],
            red_score_region["y"],
            red_score_region["x"] + red_score_region["width"],
            red_score_region["y"] + red_score_region["height"],
        ))

        # Extract values
        timer_result = self.extract_timer(timer_image, table_id)
        blue_result = self.extract_blue_score(blue_score_image, table_id)
        red_result = self.extract_red_score(red_score_image, table_id)

        # Determine extraction method
        methods = {timer_result.method, blue_result.method, red_result.method}
        if len(methods) == 1:
            extraction_method = methods.pop()
        else:
            extraction_method = "mixed"

        return GameState(
            timer=timer_result.value,
            blue_score=blue_result.value,
            red_score=red_result.value,
            timer_confidence=timer_result.confidence,
            blue_score_confidence=blue_result.confidence,
            red_score_confidence=red_result.confidence,
            extraction_method=extraction_method,
        )

    def reset_failure_counts(self, table_id: int) -> None:
        """
        Reset all failure counts for a table.

        Args:
            table_id: Table ID to reset
        """
        self._reset_failure(self._timer_failures, table_id)
        self._reset_failure(self._blue_score_failures, table_id)
        self._reset_failure(self._red_score_failures, table_id)

    def get_failure_counts(self, table_id: int) -> Dict[str, int]:
        """
        Get current failure counts for a table.

        Args:
            table_id: Table ID

        Returns:
            Dictionary with failure counts per extraction type
        """
        return {
            "timer": self._get_failure_count(self._timer_failures, table_id),
            "blue_score": self._get_failure_count(self._blue_score_failures, table_id),
            "red_score": self._get_failure_count(self._red_score_failures, table_id),
        }
