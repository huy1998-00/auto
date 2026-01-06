"""
Page monitoring for canvas element and page refresh detection.

Monitors the #layaCanvas element via polling and detects page refreshes
for error recovery.
"""

import asyncio
from typing import Optional, Dict, Callable, Any
from datetime import datetime

from .browser_manager import BrowserManager
from ..utils.logger import get_logger, TIMESTAMP_FORMAT
from ..utils.coordinate_utils import CoordinateUtils

logger = get_logger("page_monitor")


class PageMonitor:
    """
    Monitors page state and canvas element.

    Provides:
    - Canvas element availability monitoring
    - Page refresh detection
    - Canvas position drift detection
    """

    # Monitoring settings
    CANVAS_SELECTOR = "#layaCanvas"
    DEFAULT_POLL_INTERVAL_MS = 500
    DRIFT_THRESHOLD_PX = 5
    VALIDATION_INTERVAL_ROUNDS = 15  # Validate every 10-20 rounds

    def __init__(
        self,
        browser_manager: BrowserManager,
        coordinate_utils: Optional[CoordinateUtils] = None,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS,
    ):
        """
        Initialize page monitor.

        Args:
            browser_manager: Browser manager instance
            coordinate_utils: Coordinate utilities (optional)
            poll_interval_ms: Polling interval in milliseconds
        """
        self.browser_manager = browser_manager
        self.coordinate_utils = coordinate_utils or CoordinateUtils()
        self.poll_interval_ms = poll_interval_ms

        self._is_monitoring = False
        self._last_url: Optional[str] = None
        self._original_canvas_box: Optional[Dict[str, int]] = None
        self._rounds_since_validation = 0
        self._on_refresh_callback: Optional[Callable] = None
        self._on_drift_callback: Optional[Callable] = None

    async def start_monitoring(self) -> None:
        """Start page monitoring."""
        if self._is_monitoring:
            return

        self._is_monitoring = True

        # Store initial state
        if self.browser_manager.page:
            self._last_url = self.browser_manager.page.url
            self._original_canvas_box = await self.browser_manager.get_canvas_box()

        logger.info("Page monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop page monitoring."""
        self._is_monitoring = False
        logger.info("Page monitoring stopped")

    def set_refresh_callback(self, callback: Callable) -> None:
        """
        Set callback for page refresh detection.

        Args:
            callback: Async function to call when refresh detected
        """
        self._on_refresh_callback = callback

    def set_drift_callback(self, callback: Callable) -> None:
        """
        Set callback for canvas drift detection.

        Args:
            callback: Async function to call when drift detected
        """
        self._on_drift_callback = callback

    async def check_page_refresh(self) -> bool:
        """
        Check if page has been refreshed.

        Detects refresh by monitoring URL and page closed state.

        Returns:
            True if refresh detected, False otherwise
        """
        if not self.browser_manager.page:
            return True

        # Check if page is closed
        if await self.browser_manager.is_page_closed():
            logger.warning("Page is closed - refresh detected")
            return True

        # Check URL change
        current_url = await self.browser_manager.get_page_url()
        if current_url != self._last_url:
            logger.warning(f"URL changed from {self._last_url} to {current_url}")
            self._last_url = current_url
            return True

        return False

    async def check_canvas_available(self) -> bool:
        """
        Check if canvas element is available.

        Returns:
            True if canvas is available, False otherwise
        """
        if not self.browser_manager.page:
            return False

        try:
            canvas = await self.browser_manager.page.query_selector(self.CANVAS_SELECTOR)
            return canvas is not None

        except Exception:
            return False

    async def check_canvas_drift(self) -> tuple[bool, Optional[str]]:
        """
        Check if canvas position has drifted beyond threshold.

        Should be called periodically (every 10-20 rounds).

        Returns:
            Tuple of (has_drift, error_message)
        """
        if not self._original_canvas_box:
            return False, None

        current_box = await self.browser_manager.get_canvas_box()
        if not current_box:
            return True, "Canvas element not found"

        return self.coordinate_utils.validate_canvas_position(
            original_box=self._original_canvas_box,
            current_box=current_box,
            drift_threshold=self.DRIFT_THRESHOLD_PX,
        )

    async def validate_canvas_position(self) -> tuple[bool, Optional[str]]:
        """
        Validate canvas position and update drift counter.

        Call this after each round completes.

        Returns:
            Tuple of (is_valid, error_message)
        """
        self._rounds_since_validation += 1

        # Only validate every N rounds
        if self._rounds_since_validation < self.VALIDATION_INTERVAL_ROUNDS:
            return True, None

        self._rounds_since_validation = 0

        # Check for drift
        is_valid, error = await self.check_canvas_drift()

        if not is_valid:
            logger.warning(f"Canvas drift detected: {error}")
            if self._on_drift_callback:
                await self._on_drift_callback(error)

        return is_valid, error

    async def recalibrate_canvas(self) -> bool:
        """
        Recalibrate canvas position after drift detection.

        Returns:
            True if recalibration successful, False otherwise
        """
        new_box = await self.browser_manager.get_canvas_box()
        if new_box:
            self._original_canvas_box = new_box
            self._rounds_since_validation = 0
            logger.info(f"Canvas recalibrated to: {new_box}")
            return True

        logger.error("Failed to recalibrate canvas")
        return False

    async def wait_for_canvas_ready(
        self,
        timeout_ms: int = 30000,
        check_interval_ms: int = 500,
    ) -> bool:
        """
        Wait for canvas to become available after refresh.

        Args:
            timeout_ms: Maximum wait time in milliseconds
            check_interval_ms: Interval between checks

        Returns:
            True if canvas became available, False if timeout
        """
        elapsed = 0

        while elapsed < timeout_ms:
            if await self.check_canvas_available():
                # Update stored canvas position
                await self.recalibrate_canvas()
                return True

            await asyncio.sleep(check_interval_ms / 1000)
            elapsed += check_interval_ms

        logger.error(f"Canvas not available after {timeout_ms}ms timeout")
        return False

    async def poll_once(self) -> Dict[str, Any]:
        """
        Perform one polling cycle.

        Returns:
            Dictionary with status information
        """
        status = {
            "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
            "page_loaded": await self.browser_manager.is_page_loaded(),
            "page_closed": await self.browser_manager.is_page_closed(),
            "canvas_available": await self.check_canvas_available(),
            "refresh_detected": False,
            "drift_detected": False,
        }

        # Check for refresh
        if await self.check_page_refresh():
            status["refresh_detected"] = True
            if self._on_refresh_callback:
                await self._on_refresh_callback()

        # Check for drift (will only actually check every N rounds)
        is_valid, error = await self.check_canvas_drift()
        if not is_valid:
            status["drift_detected"] = True
            status["drift_error"] = error

        return status

    async def monitor_loop(self) -> None:
        """
        Run continuous monitoring loop.

        This is intended to run in a background task.
        """
        logger.info("Starting monitoring loop")

        while self._is_monitoring:
            try:
                await self.poll_once()
                await asyncio.sleep(self.poll_interval_ms / 1000)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1)  # Back off on error

        logger.info("Monitoring loop stopped")

    def get_original_canvas_box(self) -> Optional[Dict[str, int]]:
        """
        Get the stored original canvas position.

        Returns:
            Original canvas bounding box or None
        """
        return self._original_canvas_box
