"""
EasyOCR fallback for text extraction when template matching fails.

Used as a fallback after 3 consecutive template matching failures.
"""

from typing import Optional, Tuple
from PIL import Image
import numpy as np

from ..utils.logger import get_logger

logger = get_logger("ocr_fallback")

# Lazy import for EasyOCR (heavy dependency)
_easyocr_reader = None


def _get_easyocr_reader():
    """Lazy load EasyOCR reader."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            # Use English only, GPU disabled by default for compatibility
            _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            logger.info("EasyOCR reader initialized")
        except ImportError:
            logger.error("EasyOCR not installed. Install with: pip install easyocr")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            raise
    return _easyocr_reader


class OCRFallback:
    """
    EasyOCR fallback for number extraction.

    Used when OpenCV template matching fails 3 consecutive times.
    Simpler setup than Tesseract (no system installation required).
    """

    def __init__(self, lazy_load: bool = True):
        """
        Initialize OCR fallback.

        Args:
            lazy_load: If True, load EasyOCR only when first used
        """
        self.lazy_load = lazy_load
        self._reader = None

        if not lazy_load:
            self._reader = _get_easyocr_reader()

    def _get_reader(self):
        """Get EasyOCR reader, loading if necessary."""
        if self._reader is None:
            self._reader = _get_easyocr_reader()
        return self._reader

    def pil_to_numpy(self, pil_image: Image.Image) -> np.ndarray:
        """
        Convert PIL Image to numpy array for EasyOCR.

        Args:
            pil_image: PIL Image

        Returns:
            Numpy array (RGB format)
        """
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        return np.array(pil_image)

    def extract_text(
        self,
        pil_image: Image.Image,
        table_id: Optional[int] = None,
    ) -> Tuple[str, float]:
        """
        Extract text from an image using EasyOCR.

        Args:
            pil_image: PIL Image containing text
            table_id: Table ID for logging

        Returns:
            Tuple of (extracted text, confidence)
        """
        try:
            reader = self._get_reader()
            image_array = self.pil_to_numpy(pil_image)

            # Run OCR
            results = reader.readtext(image_array, detail=1)

            if not results:
                return "", 0.0

            # Combine all detected text
            texts = []
            total_confidence = 0.0

            for bbox, text, confidence in results:
                texts.append(text)
                total_confidence += confidence

            combined_text = " ".join(texts)
            avg_confidence = total_confidence / len(results) if results else 0.0

            logger.debug(
                f"OCR extracted: '{combined_text}' (confidence: {avg_confidence:.2f})",
                extra={"table_id": table_id} if table_id else {},
            )

            return combined_text, avg_confidence

        except Exception as e:
            logger.error(
                f"OCR extraction failed: {e}",
                extra={"table_id": table_id} if table_id else {},
            )
            return "", 0.0

    def extract_number(
        self,
        pil_image: Image.Image,
        table_id: Optional[int] = None,
        value_type: str = "number",
    ) -> Tuple[Optional[int], float]:
        """
        Extract a number from an image using EasyOCR.

        Args:
            pil_image: PIL Image containing a number
            table_id: Table ID for logging
            value_type: Type of value for logging ("timer", "blue_score", etc.)

        Returns:
            Tuple of (extracted number or None, confidence)
        """
        text, confidence = self.extract_text(pil_image, table_id)

        if not text:
            return None, 0.0

        # Extract digits from text
        digits = "".join(char for char in text if char.isdigit())

        if not digits:
            logger.warning(
                f"No digits found in OCR result for {value_type}: '{text}'",
                extra={"table_id": table_id} if table_id else {},
            )
            return None, 0.0

        try:
            number = int(digits)
            logger.debug(
                f"OCR extracted {value_type}: {number} (from '{text}')",
                extra={"table_id": table_id} if table_id else {},
            )
            return number, confidence

        except ValueError:
            logger.warning(
                f"Failed to parse number from OCR result: '{digits}'",
                extra={"table_id": table_id} if table_id else {},
            )
            return None, 0.0

    def extract_timer(
        self,
        pil_image: Image.Image,
        table_id: Optional[int] = None,
    ) -> Tuple[Optional[int], float]:
        """
        Extract timer value using OCR.

        Args:
            pil_image: PIL Image of timer region
            table_id: Table ID for logging

        Returns:
            Tuple of (timer value or None, confidence)
        """
        number, confidence = self.extract_number(pil_image, table_id, "timer")

        if number is not None:
            # Validate timer range (0-25)
            if 0 <= number <= 25:
                return number, confidence
            else:
                logger.warning(
                    f"OCR timer value out of range: {number}",
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
        Extract score value using OCR.

        Args:
            pil_image: PIL Image of score region
            table_id: Table ID for logging
            team: Team name for logging

        Returns:
            Tuple of (score value or None, confidence)
        """
        number, confidence = self.extract_number(pil_image, table_id, f"{team}_score")

        if number is not None and number >= 0:
            return number, confidence

        return None, confidence

    def is_available(self) -> bool:
        """
        Check if EasyOCR is available.

        Returns:
            True if EasyOCR can be loaded, False otherwise
        """
        try:
            import easyocr
            return True
        except ImportError:
            return False
