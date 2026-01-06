"""
Error recovery and per-table fault isolation.

Implements retry logic with exponential backoff and
per-table error isolation to prevent cascade failures.
"""

import time
import asyncio
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from PIL import Image

from .table_tracker import TableTracker
from ..utils.logger import get_logger, TIMESTAMP_FORMAT

logger = get_logger("error_recovery")


@dataclass
class ErrorState:
    """Error state for a single table."""

    screenshot_failures: int = 0
    extraction_failures: int = 0
    click_failures: int = 0
    total_errors: int = 0
    last_error_time: Optional[str] = None
    last_error_message: Optional[str] = None
    is_stuck: bool = False


class ErrorRecovery:
    """
    Error recovery manager with per-table isolation.

    Implements:
    - Exponential backoff retry logic (1s, 2s, 4s)
    - Per-table error isolation
    - Stuck state detection (3 consecutive failures)
    - Error screenshot saving for debugging
    """

    # Default settings from architecture
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # Seconds
    STUCK_THRESHOLD = 3
    SCREENSHOT_DIR = "error_screenshots"

    def __init__(
        self,
        max_retries: int = MAX_RETRIES,
        retry_delays: Optional[list] = None,
        stuck_threshold: int = STUCK_THRESHOLD,
        screenshot_dir: Optional[str] = None,
    ):
        """
        Initialize error recovery.

        Args:
            max_retries: Maximum retry attempts
            retry_delays: List of retry delays in seconds
            stuck_threshold: Consecutive failures before marking stuck
            screenshot_dir: Directory for error screenshots
        """
        self.max_retries = max_retries
        self.retry_delays = retry_delays or self.RETRY_DELAYS
        self.stuck_threshold = stuck_threshold
        self.screenshot_dir = Path(screenshot_dir or self.SCREENSHOT_DIR)

        # Per-table error states
        self._error_states: Dict[int, ErrorState] = {}

    def get_error_state(self, table_id: int) -> ErrorState:
        """
        Get or create error state for a table.

        Args:
            table_id: Table ID

        Returns:
            ErrorState for the table
        """
        if table_id not in self._error_states:
            self._error_states[table_id] = ErrorState()
        return self._error_states[table_id]

    def handle_screenshot_failure(
        self,
        table_id: int,
        tracker: TableTracker,
    ) -> bool:
        """
        Handle screenshot capture failure.

        Args:
            table_id: Table ID
            tracker: Table tracker

        Returns:
            True if should continue, False if stuck
        """
        error_state = self.get_error_state(table_id)
        error_state.screenshot_failures += 1
        error_state.total_errors += 1
        error_state.last_error_time = datetime.now().strftime(TIMESTAMP_FORMAT)
        error_state.last_error_message = "Screenshot capture failed"

        logger.warning(
            f"Screenshot failure ({error_state.screenshot_failures}/{self.stuck_threshold})",
            extra={"table_id": table_id},
        )

        # Check if stuck
        if error_state.screenshot_failures >= self.stuck_threshold:
            return self._mark_stuck(table_id, tracker, "screenshot")

        return True

    def handle_extraction_failure(
        self,
        table_id: int,
        tracker: TableTracker,
        failure_type: str = "extraction",
    ) -> bool:
        """
        Handle image extraction failure.

        Args:
            table_id: Table ID
            tracker: Table tracker
            failure_type: Type of extraction that failed

        Returns:
            True if should continue, False if stuck
        """
        error_state = self.get_error_state(table_id)
        error_state.extraction_failures += 1
        error_state.total_errors += 1
        error_state.last_error_time = datetime.now().strftime(TIMESTAMP_FORMAT)
        error_state.last_error_message = f"{failure_type} extraction failed"

        logger.warning(
            f"Extraction failure ({error_state.extraction_failures}/{self.stuck_threshold}): {failure_type}",
            extra={"table_id": table_id},
        )

        if error_state.extraction_failures >= self.stuck_threshold:
            return self._mark_stuck(table_id, tracker, "extraction")

        return True

    def handle_click_failure(
        self,
        table_id: int,
        tracker: TableTracker,
    ) -> bool:
        """
        Handle click execution failure.

        Args:
            table_id: Table ID
            tracker: Table tracker

        Returns:
            True if should continue, False if stuck
        """
        error_state = self.get_error_state(table_id)
        error_state.click_failures += 1
        error_state.total_errors += 1
        error_state.last_error_time = datetime.now().strftime(TIMESTAMP_FORMAT)
        error_state.last_error_message = "Click execution failed"

        logger.warning(
            f"Click failure ({error_state.click_failures}/{self.stuck_threshold})",
            extra={"table_id": table_id},
        )

        if error_state.click_failures >= self.stuck_threshold:
            return self._mark_stuck(table_id, tracker, "click")

        return True

    def _mark_stuck(
        self,
        table_id: int,
        tracker: TableTracker,
        failure_type: str,
    ) -> bool:
        """
        Mark a table as stuck.

        Args:
            table_id: Table ID
            tracker: Table tracker
            failure_type: Type of failure causing stuck state

        Returns:
            False (table should not continue)
        """
        error_state = self.get_error_state(table_id)
        error_state.is_stuck = True

        tracker.mark_stuck()

        logger.error(
            f"Table marked as STUCK due to {self.stuck_threshold} consecutive {failure_type} failures",
            extra={"table_id": table_id},
        )

        return False

    def reset_error_count(self, table_id: int, error_type: str) -> None:
        """
        Reset specific error count for a table.

        Args:
            table_id: Table ID
            error_type: Type of error to reset
        """
        error_state = self.get_error_state(table_id)

        if error_type == "screenshot":
            error_state.screenshot_failures = 0
        elif error_type == "extraction":
            error_state.extraction_failures = 0
        elif error_type == "click":
            error_state.click_failures = 0

    def reset_all_errors(self, table_id: int) -> None:
        """
        Reset all error counts for a table.

        Args:
            table_id: Table ID
        """
        self._error_states[table_id] = ErrorState()
        logger.info(f"Reset all error counts", extra={"table_id": table_id})

    async def retry_with_backoff(
        self,
        operation: Callable,
        table_id: int,
        operation_name: str = "operation",
    ) -> tuple:
        """
        Retry an async operation with exponential backoff.

        Args:
            operation: Async callable to retry
            table_id: Table ID for logging
            operation_name: Name for logging

        Returns:
            Tuple of (success, result)
        """
        for attempt, delay in enumerate(self.retry_delays, 1):
            try:
                result = await operation()

                if result is not None:
                    logger.debug(
                        f"{operation_name} succeeded on attempt {attempt}",
                        extra={"table_id": table_id},
                    )
                    return True, result

            except Exception as e:
                logger.warning(
                    f"{operation_name} failed (attempt {attempt}/{self.max_retries}): {e}",
                    extra={"table_id": table_id},
                )

            # Wait before next retry
            if attempt < self.max_retries:
                logger.debug(
                    f"Waiting {delay}s before retry",
                    extra={"table_id": table_id},
                )
                await asyncio.sleep(delay)

        logger.error(
            f"{operation_name} failed after {self.max_retries} attempts",
            extra={"table_id": table_id},
        )
        return False, None

    def retry_sync_with_backoff(
        self,
        operation: Callable,
        table_id: int,
        operation_name: str = "operation",
    ) -> tuple:
        """
        Retry a synchronous operation with exponential backoff.

        Args:
            operation: Callable to retry
            table_id: Table ID for logging
            operation_name: Name for logging

        Returns:
            Tuple of (success, result)
        """
        for attempt, delay in enumerate(self.retry_delays, 1):
            try:
                result = operation()

                if result is not None:
                    logger.debug(
                        f"{operation_name} succeeded on attempt {attempt}",
                        extra={"table_id": table_id},
                    )
                    return True, result

            except Exception as e:
                logger.warning(
                    f"{operation_name} failed (attempt {attempt}/{self.max_retries}): {e}",
                    extra={"table_id": table_id},
                )

            # Wait before next retry
            if attempt < self.max_retries:
                logger.debug(
                    f"Waiting {delay}s before retry",
                    extra={"table_id": table_id},
                )
                time.sleep(delay)

        logger.error(
            f"{operation_name} failed after {self.max_retries} attempts",
            extra={"table_id": table_id},
        )
        return False, None

    def save_error_screenshot(
        self,
        image: Image.Image,
        table_id: int,
        error_type: str,
    ) -> Optional[Path]:
        """
        Save screenshot for error debugging.

        Args:
            image: PIL Image to save
            table_id: Table ID
            error_type: Type of error

        Returns:
            Path to saved screenshot, or None if failed
        """
        try:
            # Create directory
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_{table_id}_{error_type}_{timestamp}.png"
            filepath = self.screenshot_dir / filename

            # Save image
            image.save(filepath)

            logger.info(
                f"Error screenshot saved: {filepath}",
                extra={"table_id": table_id},
            )

            return filepath

        except Exception as e:
            logger.error(
                f"Failed to save error screenshot: {e}",
                extra={"table_id": table_id},
            )
            return None

    def get_error_summary(self, table_id: int) -> Dict[str, any]:
        """
        Get error summary for a table.

        Args:
            table_id: Table ID

        Returns:
            Dictionary with error statistics
        """
        error_state = self.get_error_state(table_id)

        return {
            "table_id": table_id,
            "screenshot_failures": error_state.screenshot_failures,
            "extraction_failures": error_state.extraction_failures,
            "click_failures": error_state.click_failures,
            "total_errors": error_state.total_errors,
            "is_stuck": error_state.is_stuck,
            "last_error_time": error_state.last_error_time,
            "last_error_message": error_state.last_error_message,
        }

    def is_table_stuck(self, table_id: int) -> bool:
        """Check if a table is in stuck state."""
        error_state = self.get_error_state(table_id)
        return error_state.is_stuck
