"""
Priority-based pattern matching algorithm.

Matches the last 3 rounds against user-defined patterns
and returns the decision from the first matching pattern.
"""

from typing import Optional, List, Dict
from dataclasses import dataclass

from .pattern_validator import PatternValidator
from ..utils.logger import get_logger

logger = get_logger("pattern_matcher")


@dataclass
class Pattern:
    """A single pattern with history and decision."""

    history: str  # e.g., "BBP"
    decision: str  # "B" for Red, "P" for Blue


@dataclass
class MatchResult:
    """Result of a pattern match attempt."""

    matched: bool
    pattern: Optional[Pattern]
    decision: Optional[str]  # "blue", "red", or None


class PatternMatcher:
    """
    Priority-based pattern matching.

    Matches the last 3 rounds (e.g., "BBP") against user-defined
    patterns. First match wins (priority-based).

    Pattern format: BBP-P;BPB-B (semicolon-separated)
    - B = Red team (Banker)
    - P = Blue team (Player)
    """

    def __init__(
        self,
        patterns_string: Optional[str] = None,
        validator: Optional[PatternValidator] = None,
    ):
        """
        Initialize pattern matcher.

        Args:
            patterns_string: Pattern string (e.g., "BBP-P;BPB-B")
            validator: Pattern validator instance
        """
        self.validator = validator or PatternValidator()
        self._patterns: List[Pattern] = []

        if patterns_string:
            self.set_patterns(patterns_string)

    def set_patterns(self, patterns_string: str) -> bool:
        """
        Set patterns from a pattern string.

        Args:
            patterns_string: Pattern string (e.g., "BBP-P;BPB-B")

        Returns:
            True if patterns set successfully, False if invalid

        Raises:
            ValueError: If pattern string is invalid
        """
        # Validate pattern format
        is_valid, error = self.validator.validate(patterns_string)
        if not is_valid:
            logger.error(f"Invalid pattern string: {error}")
            raise ValueError(error)

        # Parse patterns
        self._patterns = []
        for pattern_str in patterns_string.strip().split(";"):
            parts = pattern_str.split("-")
            if len(parts) == 2:
                self._patterns.append(Pattern(
                    history=parts[0],
                    decision=parts[1],
                ))

        logger.info(f"Loaded {len(self._patterns)} patterns")
        return True

    def get_patterns(self) -> List[Pattern]:
        """
        Get current patterns.

        Returns:
            List of Pattern objects
        """
        return self._patterns.copy()

    def get_patterns_string(self) -> str:
        """
        Get patterns as a string.

        Returns:
            Pattern string (e.g., "BBP-P;BPB-B")
        """
        return ";".join(f"{p.history}-{p.decision}" for p in self._patterns)

    def match(self, last_3_rounds: str) -> MatchResult:
        """
        Match last 3 rounds against patterns.

        First matching pattern wins (priority-based).

        Args:
            last_3_rounds: String of last 3 rounds (e.g., "BBP")

        Returns:
            MatchResult with match status and decision
        """
        if not last_3_rounds or len(last_3_rounds) != 3:
            logger.debug(f"Invalid round history: '{last_3_rounds}'")
            return MatchResult(matched=False, pattern=None, decision=None)

        # Normalize to uppercase
        last_3_rounds = last_3_rounds.upper()

        # Check each pattern in order (first match wins)
        for pattern in self._patterns:
            if pattern.history == last_3_rounds:
                # Convert decision to team name
                # B = Red (Banker), P = Blue (Player)
                decision = "red" if pattern.decision == "B" else "blue"

                logger.debug(
                    f"Pattern matched: {pattern.history}-{pattern.decision} -> {decision}"
                )

                return MatchResult(
                    matched=True,
                    pattern=pattern,
                    decision=decision,
                )

        logger.debug(f"No pattern matched for: {last_3_rounds}")
        return MatchResult(matched=False, pattern=None, decision=None)

    def get_decision(
        self,
        last_3_rounds: str,
        table_id: Optional[int] = None,
    ) -> Optional[str]:
        """
        Get click decision based on pattern match.

        Convenience method that returns just the decision.

        Args:
            last_3_rounds: String of last 3 rounds (e.g., "BBP")
            table_id: Table ID for logging

        Returns:
            "blue", "red", or None if no match
        """
        result = self.match(last_3_rounds)

        if result.matched:
            logger.info(
                f"Decision: {result.decision} (pattern: {result.pattern.history}-{result.pattern.decision})",
                extra={"table_id": table_id} if table_id else {},
            )
        else:
            logger.debug(
                f"No decision for: {last_3_rounds}",
                extra={"table_id": table_id} if table_id else {},
            )

        return result.decision

    def add_pattern(self, history: str, decision: str) -> bool:
        """
        Add a single pattern.

        Args:
            history: 3-character history (e.g., "BBP")
            decision: Decision character ("B" or "P")

        Returns:
            True if added successfully, False otherwise
        """
        # Validate
        pattern_str = f"{history}-{decision}"
        is_valid, error = self.validator.validate(pattern_str)
        if not is_valid:
            logger.error(f"Invalid pattern: {error}")
            return False

        self._patterns.append(Pattern(history=history, decision=decision))
        logger.info(f"Added pattern: {pattern_str}")
        return True

    def remove_pattern(self, history: str) -> bool:
        """
        Remove a pattern by history.

        Args:
            history: 3-character history to remove

        Returns:
            True if removed, False if not found
        """
        for i, pattern in enumerate(self._patterns):
            if pattern.history == history:
                self._patterns.pop(i)
                logger.info(f"Removed pattern: {pattern.history}-{pattern.decision}")
                return True

        return False

    def clear_patterns(self) -> None:
        """Clear all patterns."""
        self._patterns.clear()
        logger.info("All patterns cleared")

    def has_patterns(self) -> bool:
        """Check if any patterns are loaded."""
        return len(self._patterns) > 0

    def pattern_count(self) -> int:
        """Get number of loaded patterns."""
        return len(self._patterns)
