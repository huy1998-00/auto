"""
Multi-table orchestration manager.

Coordinates up to 6 tables running in parallel threads,
handling state management, screenshot capture, and click execution.
"""

import asyncio
import threading
import queue
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from .table_tracker import TableTracker, TableStatus
from .screenshot_scheduler import ScreenshotScheduler
from .error_recovery import ErrorRecovery
from ..browser.browser_manager import BrowserManager
from ..browser.screenshot_capture import ScreenshotCapture
from ..browser.click_executor import ClickExecutor
from ..image_processing.image_extractor import ImageExtractor
from ..data.session_manager import SessionManager
from ..data.cache_manager import CacheManager
from ..utils.logger import get_logger, TIMESTAMP_FORMAT

logger = get_logger("multi_table_manager")


# Maximum tables (hard limit from requirements)
MAX_TABLES = 6


@dataclass
class UIUpdate:
    """Update message for UI thread."""

    type: str  # "status_update", "error", "round_complete"
    table_id: int
    data: Dict[str, Any]
    timestamp: str


class MultiTableManager:
    """
    Manages multiple game tables running in parallel.

    Coordinates:
    - Up to 6 tables running simultaneously
    - Thread-safe operations for shared data
    - Screenshot scheduling and capture
    - Click execution with per-table isolation
    - Error recovery with per-table fault isolation
    """

    def __init__(
        self,
        browser_manager: BrowserManager,
        session_manager: SessionManager,
        cache_manager: CacheManager,
        image_extractor: Optional[ImageExtractor] = None,
        screenshot_scheduler: Optional[ScreenshotScheduler] = None,
        error_recovery: Optional[ErrorRecovery] = None,
    ):
        """
        Initialize multi-table manager.

        Args:
            browser_manager: Browser manager instance
            session_manager: Session manager instance
            cache_manager: Cache manager instance
            image_extractor: Image extractor instance
            screenshot_scheduler: Screenshot scheduler instance
            error_recovery: Error recovery instance
        """
        self.browser_manager = browser_manager
        self.session_manager = session_manager
        self.cache_manager = cache_manager
        self.image_extractor = image_extractor or ImageExtractor()
        self.screenshot_scheduler = screenshot_scheduler or ScreenshotScheduler()
        self.error_recovery = error_recovery or ErrorRecovery()

        # Screenshot capture and click execution
        self.screenshot_capture = ScreenshotCapture(browser_manager)
        self.click_executor = ClickExecutor(browser_manager)

        # Table trackers
        self._tables: Dict[int, TableTracker] = {}
        self._table_configs: Dict[int, Dict[str, Any]] = {}

        # Per-table locks
        self._table_locks: Dict[int, threading.Lock] = {}

        # Worker threads
        self._worker_threads: Dict[int, threading.Thread] = {}
        self._stop_events: Dict[int, threading.Event] = {}

        # UI communication queue
        self.ui_queue: queue.Queue = queue.Queue()

        # Global state
        self._is_running = False
        self._global_lock = threading.Lock()

        logger.info("MultiTableManager initialized")

    def add_table(
        self,
        table_id: int,
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
        timer_region: Dict[str, int],
        blue_score_region: Dict[str, int],
        red_score_region: Dict[str, int],
        patterns: Optional[str] = None,
    ) -> bool:
        """
        Add a table to management.

        Args:
            table_id: Table ID (1-6)
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary
            timer_region: Timer region coordinates
            blue_score_region: Blue score region coordinates
            red_score_region: Red score region coordinates
            patterns: Optional pattern string

        Returns:
            True if added successfully, False otherwise
        """
        with self._global_lock:
            # Check table limit
            if len(self._tables) >= MAX_TABLES:
                logger.error(f"Maximum tables ({MAX_TABLES}) reached, cannot add table {table_id}")
                return False

            # Check if table already exists
            if table_id in self._tables:
                logger.warning(f"Table {table_id} already exists")
                return False

            # Create table tracker
            tracker = TableTracker(
                table_id=table_id,
                patterns=patterns,
                table_region=table_region,
            )

            # Store configuration
            self._table_configs[table_id] = {
                "table_region": table_region,
                "button_coords": button_coords,
                "timer_region": timer_region,
                "blue_score_region": blue_score_region,
                "red_score_region": red_score_region,
            }

            # Create per-table lock
            self._table_locks[table_id] = threading.Lock()

            # Store tracker
            self._tables[table_id] = tracker

            # Initialize cache
            self.cache_manager.initialize_table(table_id)

            logger.info(f"Added table {table_id}", extra={"table_id": table_id})

            return True

    def remove_table(self, table_id: int) -> bool:
        """
        Remove a table from management.

        Args:
            table_id: Table ID to remove

        Returns:
            True if removed, False if not found
        """
        with self._global_lock:
            if table_id not in self._tables:
                return False

            # Stop table if running
            self.stop_table(table_id)

            # Remove from collections
            del self._tables[table_id]
            del self._table_configs[table_id]
            del self._table_locks[table_id]

            # Remove from cache
            self.cache_manager.remove_table(table_id)

            logger.info(f"Removed table {table_id}", extra={"table_id": table_id})

            return True

    def get_table(self, table_id: int) -> Optional[TableTracker]:
        """Get table tracker by ID."""
        return self._tables.get(table_id)

    def get_all_tables(self) -> List[TableTracker]:
        """Get all table trackers."""
        return list(self._tables.values())

    def table_count(self) -> int:
        """Get number of active tables."""
        return len(self._tables)

    async def process_table(self, table_id: int) -> bool:
        """
        Process a single table iteration.

        Captures screenshot, extracts state, makes decisions,
        and executes clicks as needed.

        Args:
            table_id: Table ID to process

        Returns:
            True if processed successfully, False otherwise
        """
        tracker = self._tables.get(table_id)
        config = self._table_configs.get(table_id)

        if not tracker or not config:
            return False

        # Skip if not active
        if not tracker.is_active():
            return False

        try:
            # Capture screenshot
            screenshot = await self.screenshot_capture.capture_region(
                table_id=table_id,
                table_region=config["table_region"],
            )

            if screenshot is None:
                # Handle capture failure
                should_continue = self.error_recovery.handle_screenshot_failure(
                    table_id=table_id,
                    tracker=tracker,
                )
                if not should_continue:
                    self._send_error_update(table_id, "Screenshot capture failed")
                return False

            # Extract game state
            game_state = self.image_extractor.extract_game_state(
                table_image=screenshot,
                table_id=table_id,
                timer_region=config["timer_region"],
                blue_score_region=config["blue_score_region"],
                red_score_region=config["red_score_region"],
            )

            # Check extraction success
            if game_state.timer is None:
                should_continue = self.error_recovery.handle_extraction_failure(
                    table_id=table_id,
                    tracker=tracker,
                    failure_type="timer",
                )
                if not should_continue:
                    self._send_error_update(table_id, "Timer extraction failed")
                return False

            # Reset error counts on success
            self.error_recovery.reset_error_count(table_id, "screenshot")
            self.error_recovery.reset_error_count(table_id, "extraction")

            # Update tracker state
            with self._table_locks[table_id]:
                # Check for new round
                if tracker.detect_new_round(game_state.timer):
                    # Get winner from score change
                    winner = tracker.update_scores(
                        game_state.blue_score or 0,
                        game_state.red_score or 0,
                    )

                    if winner:
                        # Record round result
                        round_result = tracker.record_round_result(
                            winner=winner,
                            timer_start=game_state.timer,
                        )

                        # Persist to cache/JSON
                        self.cache_manager.append_round(
                            table_id=table_id,
                            round_data={
                                "round_number": round_result.round_number,
                                "timestamp": round_result.timestamp,
                                "timer_start": round_result.timer_start,
                                "blue_score": round_result.blue_score,
                                "red_score": round_result.red_score,
                                "winner": round_result.winner,
                                "decision_made": round_result.decision_made,
                                "pattern_matched": round_result.pattern_matched,
                                "result": round_result.result,
                            },
                        )

                        self._send_round_complete_update(table_id, round_result)

                # Update timer
                tracker.update_timer(game_state.timer)

                # Update scores
                tracker.update_scores(
                    game_state.blue_score or 0,
                    game_state.red_score or 0,
                )

                # Check for decision
                if tracker.should_make_decision():
                    decision = tracker.get_decision()

                    if decision and tracker.is_timer_clickable():
                        # Execute click
                        canvas_box = await self.browser_manager.get_canvas_box()
                        if canvas_box:
                            await self.click_executor.execute_two_phase_click(
                                table_id=table_id,
                                team=decision,
                                canvas_box=canvas_box,
                                table_region=config["table_region"],
                                button_coords=config["button_coords"],
                                confirm=True,
                            )

            # Send status update to UI
            self._send_status_update(table_id, tracker)

            return True

        except Exception as e:
            logger.error(
                f"Error processing table: {e}",
                extra={"table_id": table_id},
            )
            self._send_error_update(table_id, str(e))
            return False

    async def process_all_tables(self) -> Dict[int, bool]:
        """
        Process all active tables in parallel.

        Returns:
            Dictionary mapping table_id to success status
        """
        # Get tables to process
        tables_to_process = self.screenshot_scheduler.get_tables_to_capture(
            list(self._tables.values())
        )

        # Process in parallel using asyncio
        results = {}
        tasks = []

        for tracker in tables_to_process:
            task = asyncio.create_task(self.process_table(tracker.table_id))
            tasks.append((tracker.table_id, task))

        for table_id, task in tasks:
            try:
                results[table_id] = await task
            except Exception as e:
                logger.error(f"Task failed for table {table_id}: {e}")
                results[table_id] = False

        return results

    def start_table(self, table_id: int) -> bool:
        """
        Start processing a specific table.

        Args:
            table_id: Table ID to start

        Returns:
            True if started, False otherwise
        """
        tracker = self._tables.get(table_id)
        if not tracker:
            return False

        tracker.resume()
        logger.info(f"Started table {table_id}", extra={"table_id": table_id})
        return True

    def stop_table(self, table_id: int) -> bool:
        """
        Stop processing a specific table.

        Args:
            table_id: Table ID to stop

        Returns:
            True if stopped, False otherwise
        """
        tracker = self._tables.get(table_id)
        if not tracker:
            return False

        tracker.stop()
        logger.info(f"Stopped table {table_id}", extra={"table_id": table_id})
        return True

    def pause_table(self, table_id: int) -> bool:
        """
        Pause a specific table.

        Args:
            table_id: Table ID to pause

        Returns:
            True if paused, False otherwise
        """
        tracker = self._tables.get(table_id)
        if not tracker:
            return False

        tracker.pause()
        self._send_status_update(table_id, tracker)
        return True

    def resume_table(self, table_id: int) -> bool:
        """
        Resume a paused table.

        Args:
            table_id: Table ID to resume

        Returns:
            True if resumed, False otherwise
        """
        tracker = self._tables.get(table_id)
        if not tracker:
            return False

        tracker.resume()
        self.error_recovery.reset_all_errors(table_id)
        self._send_status_update(table_id, tracker)
        return True

    def start_all(self) -> None:
        """Start all tables."""
        for table_id in self._tables:
            self.start_table(table_id)
        self._is_running = True
        logger.info("All tables started")

    def stop_all(self) -> None:
        """Stop all tables."""
        self._is_running = False
        for table_id in self._tables:
            self.stop_table(table_id)

        # Flush all caches
        self.cache_manager.flush_all()
        logger.info("All tables stopped")

    def pause_all(self) -> None:
        """Pause all tables."""
        for table_id in self._tables:
            self.pause_table(table_id)
        logger.info("All tables paused")

    def resume_all(self) -> None:
        """Resume all tables."""
        for table_id in self._tables:
            self.resume_table(table_id)
        logger.info("All tables resumed")

    def _send_status_update(self, table_id: int, tracker: TableTracker) -> None:
        """Send status update to UI queue."""
        stats = tracker.get_statistics()
        update = UIUpdate(
            type="status_update",
            table_id=table_id,
            data={
                "timer": tracker.state.current_timer,
                "last_3_rounds": tracker.get_last_3_rounds(),
                "pattern_match": tracker.pattern_matcher.get_patterns_string() if tracker.pattern_matcher.has_patterns() else None,
                "decision": tracker.state.last_decision,
                "status": tracker.state.status.value,
                "statistics": stats,
            },
            timestamp=datetime.now().strftime(TIMESTAMP_FORMAT),
        )
        self.ui_queue.put(update)

    def _send_round_complete_update(self, table_id: int, round_result) -> None:
        """Send round complete update to UI queue."""
        update = UIUpdate(
            type="round_complete",
            table_id=table_id,
            data={
                "round_number": round_result.round_number,
                "winner": round_result.winner,
                "decision_made": round_result.decision_made,
                "result": round_result.result,
            },
            timestamp=datetime.now().strftime(TIMESTAMP_FORMAT),
        )
        self.ui_queue.put(update)

    def _send_error_update(self, table_id: int, error_message: str) -> None:
        """Send error update to UI queue."""
        update = UIUpdate(
            type="error",
            table_id=table_id,
            data={
                "error": error_message,
            },
            timestamp=datetime.now().strftime(TIMESTAMP_FORMAT),
        )
        self.ui_queue.put(update)

    def get_screenshot_interval(self) -> int:
        """Get current screenshot interval based on table states."""
        return self.screenshot_scheduler.calculate_interval(list(self._tables.values()))

    def get_all_statistics(self) -> Dict[int, Dict[str, Any]]:
        """Get statistics for all tables."""
        stats = {}
        for table_id, tracker in self._tables.items():
            stats[table_id] = tracker.get_statistics()
        return stats

    def set_patterns(self, table_id: int, patterns: str) -> bool:
        """
        Set patterns for a specific table.

        Args:
            table_id: Table ID
            patterns: Pattern string

        Returns:
            True if set successfully
        """
        tracker = self._tables.get(table_id)
        if not tracker:
            return False

        if tracker.set_patterns(patterns):
            self.cache_manager.update_patterns(table_id, patterns)
            return True
        return False
