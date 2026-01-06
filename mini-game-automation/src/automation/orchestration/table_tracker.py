"""
Per-table state tracking and round history management.

Tracks table state including round history, learning phase,
scores, and decision-making state.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..pattern_matching.pattern_matcher import PatternMatcher
from ..utils.logger import get_logger, TIMESTAMP_FORMAT

logger = get_logger("table_tracker")


class TableStatus(Enum):
    """Table status enumeration."""

    ACTIVE = "active"
    LEARNING = "learning"
    PAUSED = "paused"
    STUCK = "stuck"
    STOPPED = "stopped"


@dataclass
class RoundResult:
    """Result of a completed round."""

    round_number: int
    timestamp: str
    timer_start: int
    blue_score: int
    red_score: int
    winner: str  # "B" or "P"
    decision_made: Optional[str]  # "blue", "red", or None
    pattern_matched: Optional[str]  # Pattern that was matched
    result: Optional[str]  # "correct", "incorrect", or None


@dataclass
class TableState:
    """Complete state for a single table."""

    table_id: int
    status: TableStatus = TableStatus.LEARNING
    learning_phase: bool = True
    rounds_watched: int = 0
    round_history: List[str] = field(default_factory=list)

    # Current game state
    current_timer: Optional[int] = None
    blue_score: int = 0
    red_score: int = 0
    previous_blue_score: int = 0
    previous_red_score: int = 0

    # Pattern configuration
    patterns: str = ""

    # Round tracking
    completed_rounds: List[RoundResult] = field(default_factory=list)
    current_round_number: int = 0

    # Decision tracking
    last_decision: Optional[str] = None
    decision_pending: bool = False

    # Statistics
    total_decisions: int = 0
    correct_decisions: int = 0

    # Timestamps
    session_start: str = field(default_factory=lambda: datetime.now().strftime(TIMESTAMP_FORMAT))
    last_update: str = field(default_factory=lambda: datetime.now().strftime(TIMESTAMP_FORMAT))


class TableTracker:
    """
    Tracks state for a single game table.

    Manages:
    - Round history (last 3 rounds as B/P)
    - Learning phase (first 3 rounds)
    - Score tracking and winner detection
    - Pattern matching integration
    - Decision tracking and statistics
    """

    # Learning phase settings
    LEARNING_ROUNDS_REQUIRED = 3

    def __init__(
        self,
        table_id: int,
        patterns: Optional[str] = None,
        table_region: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize table tracker.

        Args:
            table_id: Unique table identifier (1-6)
            patterns: Initial pattern string
            table_region: Table region coordinates
        """
        self.table_id = table_id
        self.table_region = table_region or {}

        # Initialize state
        self.state = TableState(table_id=table_id)

        # Pattern matcher
        self.pattern_matcher = PatternMatcher()
        if patterns:
            self.set_patterns(patterns)

        logger.info(f"TableTracker initialized", extra={"table_id": table_id})

    def set_patterns(self, patterns: str) -> bool:
        """
        Set patterns for this table.

        Args:
            patterns: Pattern string (e.g., "BBP-P;BPB-B")

        Returns:
            True if patterns set successfully
        """
        try:
            self.pattern_matcher.set_patterns(patterns)
            self.state.patterns = patterns
            logger.info(
                f"Patterns set: {patterns}",
                extra={"table_id": self.table_id},
            )
            return True
        except ValueError as e:
            logger.error(
                f"Failed to set patterns: {e}",
                extra={"table_id": self.table_id},
            )
            return False

    def update_timer(self, timer_value: int) -> None:
        """
        Update current timer value.

        Args:
            timer_value: Current timer value (0-25)
        """
        self.state.current_timer = timer_value
        self._update_timestamp()

    def update_scores(self, blue_score: int, red_score: int) -> Optional[str]:
        """
        Update scores and detect winner if score changed.

        Args:
            blue_score: Current blue team score
            red_score: Current red team score

        Returns:
            Winner ("B" or "P") if detected, None otherwise
        """
        # Store previous scores
        prev_blue = self.state.blue_score
        prev_red = self.state.red_score

        # Update current scores
        self.state.blue_score = blue_score
        self.state.red_score = red_score
        self._update_timestamp()

        # Detect winner by score change
        winner = None
        if blue_score > prev_blue:
            winner = "P"  # Blue (Player) won
        elif red_score > prev_red:
            winner = "B"  # Red (Banker) won

        if winner:
            logger.debug(
                f"Score changed: Blue {prev_blue}->{blue_score}, Red {prev_red}->{red_score}, Winner: {winner}",
                extra={"table_id": self.table_id},
            )

        # Update previous scores for next comparison
        self.state.previous_blue_score = blue_score
        self.state.previous_red_score = red_score

        return winner

    def record_round_result(
        self,
        winner: str,
        timer_start: Optional[int] = None,
    ) -> RoundResult:
        """
        Record a completed round result.

        Args:
            winner: Round winner ("B" or "P")
            timer_start: Timer value at round start

        Returns:
            RoundResult for the completed round
        """
        # Increment round number
        self.state.current_round_number += 1
        self.state.rounds_watched += 1

        # Add to round history
        self.state.round_history.append(winner)
        # Keep only last 3
        if len(self.state.round_history) > 3:
            self.state.round_history = self.state.round_history[-3:]

        # Check learning phase completion
        if self.state.learning_phase and self.state.rounds_watched >= self.LEARNING_ROUNDS_REQUIRED:
            self.state.learning_phase = False
            self.state.status = TableStatus.ACTIVE
            logger.info(
                f"Learning phase complete, now active",
                extra={"table_id": self.table_id},
            )

        # Determine if decision was correct
        result = None
        if self.state.last_decision:
            self.state.total_decisions += 1
            # Check if decision matched winner
            if (self.state.last_decision == "blue" and winner == "P") or \
               (self.state.last_decision == "red" and winner == "B"):
                result = "correct"
                self.state.correct_decisions += 1
            else:
                result = "incorrect"

        # Create round result
        round_result = RoundResult(
            round_number=self.state.current_round_number,
            timestamp=datetime.now().strftime(TIMESTAMP_FORMAT),
            timer_start=timer_start or 15,
            blue_score=self.state.blue_score,
            red_score=self.state.red_score,
            winner=winner,
            decision_made=self.state.last_decision,
            pattern_matched=self.pattern_matcher.get_patterns_string() if self.state.last_decision else None,
            result=result,
        )

        self.state.completed_rounds.append(round_result)

        # Reset decision state
        self.state.last_decision = None
        self.state.decision_pending = False

        logger.info(
            f"Round {round_result.round_number} complete: Winner={winner}, Decision={round_result.decision_made}, Result={result}",
            extra={"table_id": self.table_id},
        )

        self._update_timestamp()
        return round_result

    def get_last_3_rounds(self) -> Optional[str]:
        """
        Get the last 3 rounds as a string.

        Returns:
            String like "BBP" or None if not enough rounds
        """
        if len(self.state.round_history) < 3:
            return None
        return "".join(self.state.round_history[-3:])

    def should_make_decision(self) -> bool:
        """
        Check if table should make a decision.

        Returns:
            True if decision should be made, False otherwise
        """
        # Not in learning phase
        if self.state.learning_phase:
            return False

        # Not already pending
        if self.state.decision_pending:
            return False

        # Has enough history
        if len(self.state.round_history) < 3:
            return False

        # Timer is in clickable range
        if self.state.current_timer is None or self.state.current_timer <= 6:
            return False

        return True

    def get_decision(self) -> Optional[str]:
        """
        Get click decision based on pattern match.

        Returns:
            "blue", "red", or None
        """
        if not self.should_make_decision():
            return None

        last_3 = self.get_last_3_rounds()
        if not last_3:
            return None

        decision = self.pattern_matcher.get_decision(last_3, self.table_id)

        if decision:
            self.state.last_decision = decision
            self.state.decision_pending = True
            logger.info(
                f"Decision made: {decision} (history: {last_3})",
                extra={"table_id": self.table_id},
            )

        return decision

    def is_timer_clickable(self) -> bool:
        """
        Check if timer value allows clicking.

        Returns:
            True if timer > 6, False otherwise
        """
        if self.state.current_timer is None:
            return False
        return self.state.current_timer > 6

    def detect_new_round(self, current_timer: int) -> bool:
        """
        Detect if a new round has started.

        New round = timer jumps from low (1-6) to high (15 or 25)

        Args:
            current_timer: Current timer value

        Returns:
            True if new round detected, False otherwise
        """
        previous_timer = self.state.current_timer

        if previous_timer is None:
            return False

        # Timer reset: from low (1-6) to high (15 or 25)
        if previous_timer <= 6 and current_timer > 10:
            logger.debug(
                f"New round detected: timer {previous_timer} -> {current_timer}",
                extra={"table_id": self.table_id},
            )
            return True

        return False

    def pause(self) -> None:
        """Pause table tracking."""
        self.state.status = TableStatus.PAUSED
        logger.info(f"Table paused", extra={"table_id": self.table_id})

    def resume(self) -> None:
        """Resume table tracking."""
        if self.state.learning_phase:
            self.state.status = TableStatus.LEARNING
        else:
            self.state.status = TableStatus.ACTIVE
        logger.info(f"Table resumed", extra={"table_id": self.table_id})

    def mark_stuck(self) -> None:
        """Mark table as stuck (3 consecutive failures)."""
        self.state.status = TableStatus.STUCK
        logger.warning(f"Table marked as stuck", extra={"table_id": self.table_id})

    def stop(self) -> None:
        """Stop table tracking."""
        self.state.status = TableStatus.STOPPED
        logger.info(f"Table stopped", extra={"table_id": self.table_id})

    def is_active(self) -> bool:
        """Check if table is actively processing."""
        return self.state.status in (TableStatus.ACTIVE, TableStatus.LEARNING)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get table statistics.

        Returns:
            Dictionary with statistics
        """
        accuracy = 0.0
        if self.state.total_decisions > 0:
            accuracy = self.state.correct_decisions / self.state.total_decisions * 100

        return {
            "table_id": self.table_id,
            "status": self.state.status.value,
            "total_rounds": len(self.state.completed_rounds),
            "rounds_watched": self.state.rounds_watched,
            "total_decisions": self.state.total_decisions,
            "correct_decisions": self.state.correct_decisions,
            "accuracy": round(accuracy, 2),
            "learning_phase": self.state.learning_phase,
            "current_timer": self.state.current_timer,
            "blue_score": self.state.blue_score,
            "red_score": self.state.red_score,
            "last_3_rounds": self.get_last_3_rounds(),
        }

    def get_state_dict(self) -> Dict[str, Any]:
        """
        Get complete state as dictionary for JSON serialization.

        Returns:
            Dictionary representation of state
        """
        return {
            "table_id": self.table_id,
            "session_start": self.state.session_start,
            "patterns": self.state.patterns,
            "rounds": [
                {
                    "round_number": r.round_number,
                    "timestamp": r.timestamp,
                    "timer_start": r.timer_start,
                    "blue_score": r.blue_score,
                    "red_score": r.red_score,
                    "winner": r.winner,
                    "decision_made": r.decision_made,
                    "pattern_matched": r.pattern_matched,
                    "result": r.result,
                }
                for r in self.state.completed_rounds
            ],
            "statistics": self.get_statistics(),
        }

    def _update_timestamp(self) -> None:
        """Update last_update timestamp."""
        self.state.last_update = datetime.now().strftime(TIMESTAMP_FORMAT)
