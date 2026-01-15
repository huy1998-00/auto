"""
Region-only screenshot capture using Playwright.

Captures screenshots of specific table regions using coordinates,
not full page screenshots for efficiency.
"""

from typing import Optional, Dict
from PIL import Image
import io

from .browser_manager import BrowserManager
from ..utils.logger import get_logger
from ..utils.coordinate_utils import CoordinateUtils

logger = get_logger("screenshot_capture")


class ScreenshotCapture:
    """
    Captures region-specific screenshots from the browser.

    Takes screenshots directly for each table's region using coordinates
    instead of full page capture for better performance.
    """

    def __init__(
        self,
        browser_manager: BrowserManager,
        coordinate_utils: Optional[CoordinateUtils] = None,
    ):
        """
        Initialize screenshot capture.

        Args:
            browser_manager: Browser manager instance
            coordinate_utils: Coordinate utilities (optional)
        """
        self.browser_manager = browser_manager
        self.coordinate_utils = coordinate_utils or CoordinateUtils()

    async def capture_region(
        self,
        table_id: int,
        table_region: Dict[str, int],
    ) -> Optional[Image.Image]:
        """
        Capture screenshot of a specific table region.

        Args:
            table_id: Table ID for logging
            table_region: Region coordinates {'x', 'y', 'width', 'height'}

        Returns:
            PIL Image of the region, or None on failure
        """
        if not self.browser_manager.page:
            logger.error(f"Browser not initialized", extra={"table_id": table_id})
            return None

        try:
            # Try to get canvas box (may not exist yet)
            canvas_box = await self.browser_manager.get_canvas_box_with_retry(timeout_ms=2000)
            if not canvas_box:
                logger.error(
                    "Canvas element not found after retry",
                    extra={"table_id": table_id},
                )
                return None

            # Calculate screenshot region coordinates
            screenshot_coords = self.coordinate_utils.get_region_screenshot_coords(
                canvas_box=canvas_box,
                table_region=table_region,
            )

            # Capture screenshot of the specific region
            screenshot_bytes = await self.browser_manager.page.screenshot(
                clip={
                    "x": screenshot_coords["x"],
                    "y": screenshot_coords["y"],
                    "width": screenshot_coords["width"],
                    "height": screenshot_coords["height"],
                },
                type="png",
            )

            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))

            logger.debug(
                f"Captured region screenshot: {screenshot_coords['width']}x{screenshot_coords['height']}",
                extra={"table_id": table_id},
            )

            return image

        except Exception as e:
            logger.error(
                f"Failed to capture region screenshot: {e}",
                extra={"table_id": table_id},
            )
            return None

    async def capture_subregion(
        self,
        table_id: int,
        table_region: Dict[str, int],
        subregion: Dict[str, int],
    ) -> Optional[Image.Image]:
        """
        Capture a subregion within a table region.

        Useful for capturing timer/score regions directly.

        Args:
            table_id: Table ID for logging
            table_region: Table region coordinates
            subregion: Subregion coordinates within table

        Returns:
            PIL Image of the subregion, or None on failure
        """
        if not self.browser_manager.page:
            logger.error("Browser not initialized", extra={"table_id": table_id})
            return None

        try:
            # Try to get canvas box (may not exist yet)
            canvas_box = await self.browser_manager.get_canvas_box_with_retry(timeout_ms=2000)
            if not canvas_box:
                logger.error(
                    "Canvas element not found after retry",
                    extra={"table_id": table_id},
                )
                return None

            # Calculate absolute subregion coordinates
            absolute_x = canvas_box["x"] + table_region["x"] + subregion["x"]
            absolute_y = canvas_box["y"] + table_region["y"] + subregion["y"]

            # Capture screenshot of the specific subregion
            screenshot_bytes = await self.browser_manager.page.screenshot(
                clip={
                    "x": absolute_x,
                    "y": absolute_y,
                    "width": subregion["width"],
                    "height": subregion["height"],
                },
                type="png",
            )

            # Convert to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))

            logger.debug(
                f"Captured subregion screenshot: {subregion['width']}x{subregion['height']}",
                extra={"table_id": table_id},
            )

            return image

        except Exception as e:
            logger.error(
                f"Failed to capture subregion screenshot: {e}",
                extra={"table_id": table_id},
            )
            return None

    async def capture_full_canvas(self) -> Optional[Image.Image]:
        """
        Capture the full canvas element.

        Returns:
            PIL Image of the full canvas, or None on failure
        """
        if not self.browser_manager.page:
            logger.error("Browser not initialized")
            return None

        try:
            # Try to get canvas box (may not exist yet)
            canvas_box = await self.browser_manager.get_canvas_box_with_retry(timeout_ms=2000)
            if not canvas_box:
                logger.error("Canvas element not found after retry")
                return None

            screenshot_bytes = await self.browser_manager.page.screenshot(
                clip={
                    "x": canvas_box["x"],
                    "y": canvas_box["y"],
                    "width": canvas_box["width"],
                    "height": canvas_box["height"],
                },
                type="png",
            )

            image = Image.open(io.BytesIO(screenshot_bytes))
            logger.debug(f"Captured full canvas: {canvas_box['width']}x{canvas_box['height']}")

            return image

        except Exception as e:
            logger.error(f"Failed to capture full canvas: {e}")
            return None

    def crop_region_from_image(
        self,
        image: Image.Image,
        region: Dict[str, int],
    ) -> Optional[Image.Image]:
        """
        Crop a region from an existing image.

        Args:
            image: Source image
            region: Region to crop {'x', 'y', 'width', 'height'}

        Returns:
            Cropped PIL Image, or None on failure
        """
        try:
            # PIL crop uses (left, upper, right, lower)
            crop_box = (
                region["x"],
                region["y"],
                region["x"] + region["width"],
                region["y"] + region["height"],
            )

            return image.crop(crop_box)

        except Exception as e:
            logger.error(f"Failed to crop region: {e}")
            return None

    async def save_screenshot(
        self,
        image: Image.Image,
        filepath: str,
        table_id: Optional[int] = None,
    ) -> bool:
        """
        Save a screenshot to file.

        Args:
            image: PIL Image to save
            filepath: Path to save the image
            table_id: Optional table ID for logging

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            image.save(filepath, "PNG")

            if table_id is not None:
                logger.debug(f"Saved screenshot to {filepath}", extra={"table_id": table_id})
            else:
                logger.debug(f"Saved screenshot to {filepath}")

            return True

        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False
