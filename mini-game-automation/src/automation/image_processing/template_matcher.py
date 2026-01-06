"""
OpenCV template matching for number extraction.

Uses template matching to identify numbers 0-9 from timer and score regions.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from PIL import Image

from ..utils.logger import get_logger

logger = get_logger("template_matcher")


class TemplateMatcher:
    """
    OpenCV template matching for number recognition.

    Uses pre-loaded templates (0-9) to match numbers in
    timer and score regions.
    """

    # Template matching settings
    DEFAULT_THRESHOLD = 0.8
    TEMPLATE_DIR = Path(__file__).parent / "templates"

    def __init__(
        self,
        template_dir: Optional[Path] = None,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        """
        Initialize template matcher.

        Args:
            template_dir: Directory containing number templates
            threshold: Minimum match confidence (0-1)
        """
        self.template_dir = template_dir or self.TEMPLATE_DIR
        self.threshold = threshold
        self._templates: Dict[str, np.ndarray] = {}
        self._templates_loaded = False

    def load_templates(self) -> bool:
        """
        Load number templates (0-9) from template directory.

        Returns:
            True if templates loaded successfully, False otherwise
        """
        if self._templates_loaded:
            return True

        template_dir = Path(self.template_dir)
        if not template_dir.exists():
            logger.warning(f"Template directory not found: {template_dir}")
            # Create empty directory for future use
            template_dir.mkdir(parents=True, exist_ok=True)
            return False

        loaded_count = 0
        for digit in range(10):
            template_path = template_dir / f"{digit}.png"
            if template_path.exists():
                template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
                if template is not None:
                    self._templates[str(digit)] = template
                    loaded_count += 1
                else:
                    logger.warning(f"Failed to load template: {template_path}")
            else:
                logger.debug(f"Template not found: {template_path}")

        self._templates_loaded = loaded_count > 0
        logger.info(f"Loaded {loaded_count} number templates")
        return self._templates_loaded

    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to OpenCV format.

        Args:
            pil_image: PIL Image

        Returns:
            OpenCV image (numpy array)
        """
        # Convert to RGB if needed
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Convert to numpy array
        cv2_image = np.array(pil_image)

        # Convert RGB to BGR (OpenCV format)
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2BGR)

        return cv2_image

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for template matching.

        Converts to grayscale and applies thresholding.

        Args:
            image: OpenCV image (BGR)

        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply binary thresholding to enhance contrast
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        return binary

    def match_single_digit(
        self,
        image: np.ndarray,
        region: Optional[Tuple[int, int, int, int]] = None,
    ) -> Tuple[Optional[int], float]:
        """
        Match a single digit in an image.

        Args:
            image: Preprocessed grayscale image
            region: Optional (x, y, width, height) to search within

        Returns:
            Tuple of (digit or None, confidence score)
        """
        if not self._templates:
            if not self.load_templates():
                return None, 0.0

        # Crop to region if specified
        if region:
            x, y, w, h = region
            image = image[y:y+h, x:x+w]

        best_digit = None
        best_confidence = 0.0

        for digit_str, template in self._templates.items():
            # Skip if template is larger than image
            if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
                continue

            # Template matching
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > best_confidence and max_val >= self.threshold:
                best_confidence = max_val
                best_digit = int(digit_str)

        return best_digit, best_confidence

    def match_number(
        self,
        pil_image: Image.Image,
        max_digits: int = 3,
    ) -> Tuple[Optional[int], float]:
        """
        Match a multi-digit number in an image.

        Args:
            pil_image: PIL Image containing the number
            max_digits: Maximum number of digits expected

        Returns:
            Tuple of (number or None, average confidence)
        """
        if not self._templates:
            if not self.load_templates():
                return None, 0.0

        # Convert and preprocess
        cv2_image = self.pil_to_cv2(pil_image)
        processed = self.preprocess_image(cv2_image)

        # Find all digit matches
        matches = self._find_all_digit_matches(processed)

        if not matches:
            return None, 0.0

        # Sort by x position (left to right)
        matches.sort(key=lambda m: m[1])

        # Take up to max_digits
        matches = matches[:max_digits]

        # Build number from digits
        number_str = "".join(str(m[0]) for m in matches)
        avg_confidence = sum(m[2] for m in matches) / len(matches)

        try:
            number = int(number_str)
            return number, avg_confidence
        except ValueError:
            return None, 0.0

    def _find_all_digit_matches(
        self,
        image: np.ndarray,
        min_distance: int = 5,
    ) -> List[Tuple[int, int, float]]:
        """
        Find all digit matches in an image.

        Args:
            image: Preprocessed grayscale image
            min_distance: Minimum distance between matches

        Returns:
            List of (digit, x_position, confidence) tuples
        """
        all_matches = []

        for digit_str, template in self._templates.items():
            # Skip if template is larger than image
            if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
                continue

            # Template matching
            result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

            # Find all locations above threshold
            locations = np.where(result >= self.threshold)

            for pt in zip(*locations[::-1]):  # x, y coordinates
                confidence = result[pt[1], pt[0]]
                digit = int(digit_str)

                # Check if this match is far enough from existing matches
                is_unique = True
                for existing in all_matches:
                    if abs(pt[0] - existing[1]) < min_distance:
                        # Keep the higher confidence match
                        if confidence > existing[2]:
                            all_matches.remove(existing)
                        else:
                            is_unique = False
                        break

                if is_unique:
                    all_matches.append((digit, pt[0], confidence))

        return all_matches

    def extract_timer(
        self,
        pil_image: Image.Image,
        table_id: Optional[int] = None,
    ) -> Tuple[Optional[int], float]:
        """
        Extract timer value from timer region image.

        Args:
            pil_image: PIL Image of timer region
            table_id: Table ID for logging

        Returns:
            Tuple of (timer value or None, confidence)
        """
        result, confidence = self.match_number(pil_image, max_digits=2)

        if result is not None:
            # Validate timer range (0-25)
            if 0 <= result <= 25:
                logger.debug(
                    f"Extracted timer: {result} (confidence: {confidence:.2f})",
                    extra={"table_id": table_id} if table_id else {},
                )
                return result, confidence
            else:
                logger.warning(
                    f"Timer value out of range: {result}",
                    extra={"table_id": table_id} if table_id else {},
                )

        return None, confidence

    def extract_score(
        self,
        pil_image: Image.Image,
        table_id: Optional[int] = None,
        team: str = "unknown",
    ) -> Tuple[Optional[int], float]:
        """
        Extract score value from score region image.

        Args:
            pil_image: PIL Image of score region
            table_id: Table ID for logging
            team: Team name for logging ("blue" or "red")

        Returns:
            Tuple of (score value or None, confidence)
        """
        result, confidence = self.match_number(pil_image, max_digits=3)

        if result is not None:
            # Validate score range (0-999+)
            if result >= 0:
                logger.debug(
                    f"Extracted {team} score: {result} (confidence: {confidence:.2f})",
                    extra={"table_id": table_id} if table_id else {},
                )
                return result, confidence

        return None, confidence
