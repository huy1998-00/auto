"""
Adaptive screenshot frequency management.

Adjusts screenshot frequency based on game phase:
- Normal: 200ms when timer > 6 (clickable phase)
- Fast: 100ms when timer <= 6 (countdown phase)
- Slow: 1000ms when all tables in result phase
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

from .table_tracker import TableTracker, TableStatus
from ..utils.logger import get_logger
from ..utils.resource_monitor import ResourceMonitor

logger = get_logger("screenshot_scheduler")


class GamePhase(Enum):
    """Game phase for a table."""

    CLICKABLE = "clickable"  # Timer > 6
    COUNTDOWN = "countdown"  # Timer <= 6
    RESULT = "result"  # Timer = 0, waiting for reset


class SchedulingStrategy(Enum):
    """Screenshot scheduling strategy options."""

    FASTEST_TIMER = "fastest"  # Use fastest timer's interval (recommended)
    SLOWEST_TIMER = "slowest"  # Use slowest timer's interval
    FIXED = "fixed"  # Use fixed interval
    MAJORITY = "majority"  # Use majority phase's interval
    PER_TABLE = "per_table"  # Per-table independent intervals (advanced)


@dataclass
class IntervalSettings:
    """Screenshot interval settings in milliseconds."""

    normal_ms: int = 200  # Timer > 6 (clickable phase)
    fast_ms: int = 100  # Timer <= 6 (countdown phase)
    slow_ms: int = 1000  # Result phase (timer = 0)


class ScreenshotScheduler:
    """
    Manages adaptive screenshot frequency across tables.

    Adjusts capture frequency based on game phase to:
    - Catch critical moments (round completion)
    - Avoid wasting resources during slow phases
    """

    def __init__(
        self,
        interval_settings: Optional[IntervalSettings] = None,
        strategy: SchedulingStrategy = SchedulingStrategy.FASTEST_TIMER,
        resource_monitor: Optional[ResourceMonitor] = None,
    ):
        """
        Initialize screenshot scheduler.

        Args:
            interval_settings: Interval configuration
            strategy: Scheduling strategy to use
            resource_monitor: Resource monitor for CPU throttling
        """
        self.intervals = interval_settings or IntervalSettings()
        self.strategy = strategy
        self.resource_monitor = resource_monitor

        # Per-table intervals (for PER_TABLE strategy)
        self._table_intervals: Dict[int, int] = {}

    def get_table_phase(self, timer_value: Optional[int]) -> GamePhase:
        """
        Determine game phase from timer value.

        Args:
            timer_value: Current timer value

        Returns:
            GamePhase enum value
        """
        if timer_value is None or timer_value == 0:
            return GamePhase.RESULT
        elif timer_value <= 6:
            return GamePhase.COUNTDOWN
        else:
            return GamePhase.CLICKABLE

    def get_phase_interval(self, phase: GamePhase) -> int:
        """
        Get interval for a specific phase.

        Args:
            phase: Game phase

        Returns:
            Interval in milliseconds
        """
        if phase == GamePhase.COUNTDOWN:
            return self.intervals.fast_ms
        elif phase == GamePhase.CLICKABLE:
            return self.intervals.normal_ms
        else:
            return self.intervals.slow_ms

    def calculate_interval(
        self,
        table_trackers: List[TableTracker],
    ) -> int:
        """
        Calculate screenshot interval based on current table states.

        Uses the configured strategy to determine interval.

        Args:
            table_trackers: List of active table trackers

        Returns:
            Screenshot interval in milliseconds
        """
        # Filter to active tables only
        active_trackers = [
            t for t in table_trackers
            if t.is_active()
        ]

        if not active_trackers:
            return self.intervals.slow_ms

        # Get timer values
        timer_values = [
            t.state.current_timer
            for t in active_trackers
            if t.state.current_timer is not None
        ]

        if not timer_values:
            return self.intervals.normal_ms

        # Calculate based on strategy
        interval = self._calculate_by_strategy(timer_values, active_trackers)

        # Apply CPU throttling if resource monitor available
        if self.resource_monitor:
            interval = self.resource_monitor.get_adjusted_interval(interval)

        return interval

    def _calculate_by_strategy(
        self,
        timer_values: List[int],
        trackers: List[TableTracker],
    ) -> int:
        """
        Calculate interval based on selected strategy.

        Args:
            timer_values: List of current timer values
            trackers: List of active table trackers

        Returns:
            Interval in milliseconds
        """
        if self.strategy == SchedulingStrategy.FASTEST_TIMER:
            return self._fastest_timer_strategy(timer_values)

        elif self.strategy == SchedulingStrategy.SLOWEST_TIMER:
            return self._slowest_timer_strategy(timer_values)

        elif self.strategy == SchedulingStrategy.FIXED:
            return self.intervals.normal_ms

        elif self.strategy == SchedulingStrategy.MAJORITY:
            return self._majority_strategy(timer_values)

        elif self.strategy == SchedulingStrategy.PER_TABLE:
            # For per-table, return fastest interval needed
            return self._fastest_timer_strategy(timer_values)

        return self.intervals.normal_ms

    def _fastest_timer_strategy(self, timer_values: List[int]) -> int:
        """
        Fastest timer strategy (recommended).

        If ANY table is in countdown phase, use fast interval.

        Args:
            timer_values: List of timer values

        Returns:
            Interval in milliseconds
        """
        # Check phases
        phases = [self.get_table_phase(t) for t in timer_values]

        # If any in countdown, use fast
        if GamePhase.COUNTDOWN in phases:
            return self.intervals.fast_ms

        # If any in clickable, use normal
        if GamePhase.CLICKABLE in phases:
            return self.intervals.normal_ms

        # All in result phase
        return self.intervals.slow_ms

    def _slowest_timer_strategy(self, timer_values: List[int]) -> int:
        """
        Slowest timer strategy.

        Use the slowest timer (highest value) to determine interval.

        Args:
            timer_values: List of timer values

        Returns:
            Interval in milliseconds
        """
        # Get highest timer (slowest = further from completion)
        max_timer = max(timer_values)
        phase = self.get_table_phase(max_timer)
        return self.get_phase_interval(phase)

    def _majority_strategy(self, timer_values: List[int]) -> int:
        """
        Majority rule strategy.

        Use interval based on phase with most tables.

        Args:
            timer_values: List of timer values

        Returns:
            Interval in milliseconds
        """
        phases = [self.get_table_phase(t) for t in timer_values]

        # Count phases
        phase_counts = {
            GamePhase.COUNTDOWN: 0,
            GamePhase.CLICKABLE: 0,
            GamePhase.RESULT: 0,
        }

        for phase in phases:
            phase_counts[phase] += 1

        # Find majority phase
        majority_phase = max(phase_counts, key=phase_counts.get)
        return self.get_phase_interval(majority_phase)

    def get_table_interval(self, table_id: int, timer_value: Optional[int]) -> int:
        """
        Get interval for a specific table (for PER_TABLE strategy).

        Args:
            table_id: Table ID
            timer_value: Current timer value

        Returns:
            Interval in milliseconds
        """
        phase = self.get_table_phase(timer_value)
        interval = self.get_phase_interval(phase)

        # Apply CPU throttling if available
        if self.resource_monitor:
            interval = self.resource_monitor.get_adjusted_interval(interval)

        self._table_intervals[table_id] = interval
        return interval

    def should_capture_table(
        self,
        table_tracker: TableTracker,
    ) -> bool:
        """
        Determine if a table should have screenshot captured.

        Inactive/paused tables are skipped to save resources.

        Args:
            table_tracker: Table tracker instance

        Returns:
            True if screenshot should be captured
        """
        return table_tracker.is_active()

    def get_tables_to_capture(
        self,
        table_trackers: List[TableTracker],
    ) -> List[TableTracker]:
        """
        Get list of tables that need screenshots.

        Filters out inactive/paused tables.

        Args:
            table_trackers: All table trackers

        Returns:
            List of active table trackers to capture
        """
        return [
            t for t in table_trackers
            if self.should_capture_table(t)
        ]

    def get_status(self) -> Dict[str, any]:
        """
        Get scheduler status for monitoring.

        Returns:
            Dictionary with scheduler status
        """
        status = {
            "strategy": self.strategy.value,
            "intervals": {
                "normal_ms": self.intervals.normal_ms,
                "fast_ms": self.intervals.fast_ms,
                "slow_ms": self.intervals.slow_ms,
            },
            "table_intervals": self._table_intervals.copy(),
        }

        if self.resource_monitor:
            status["throttled"] = self.resource_monitor.should_throttle()
            status["throttle_factor"] = self.resource_monitor.get_throttle_factor()

        return status

    def set_strategy(self, strategy: SchedulingStrategy) -> None:
        """
        Change scheduling strategy.

        Args:
            strategy: New strategy to use
        """
        self.strategy = strategy
        logger.info(f"Screenshot strategy changed to: {strategy.value}")

    def set_intervals(
        self,
        normal_ms: Optional[int] = None,
        fast_ms: Optional[int] = None,
        slow_ms: Optional[int] = None,
    ) -> None:
        """
        Update interval settings.

        Args:
            normal_ms: Normal interval (timer > 6)
            fast_ms: Fast interval (timer <= 6)
            slow_ms: Slow interval (result phase)
        """
        if normal_ms is not None:
            self.intervals.normal_ms = normal_ms
        if fast_ms is not None:
            self.intervals.fast_ms = fast_ms
        if slow_ms is not None:
            self.intervals.slow_ms = slow_ms

        logger.info(
            f"Intervals updated: normal={self.intervals.normal_ms}ms, "
            f"fast={self.intervals.fast_ms}ms, slow={self.intervals.slow_ms}ms"
        )
