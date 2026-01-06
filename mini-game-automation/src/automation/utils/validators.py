"""
Validation utilities for pattern format and coordinates.

Provides validation for user-defined patterns and table region coordinates.
"""

import re
from typing import Optional, Tuple, Dict, Any


# Pattern validation regex from architecture specification
PATTERN_REGEX = r"^[BP]{3}-[BP](;[BP]{3}-[BP])*$"


class PatternFormatValidator:
    """Validator for pattern format strings."""

    def __init__(self, regex_pattern: str = PATTERN_REGEX):
        """
        Initialize pattern validator.

        Args:
            regex_pattern: Regular expression for valid pattern format
        """
        self.regex_pattern = regex_pattern
        self._compiled_regex = re.compile(regex_pattern)

    def is_valid(self, pattern_string: str) -> bool:
        """
        Check if a pattern string is valid.

        Args:
            pattern_string: Pattern string to validate (e.g., "BBP-P;BPB-B")

        Returns:
            True if valid, False otherwise
        """
        if not pattern_string or not isinstance(pattern_string, str):
            return False

        return bool(self._compiled_regex.match(pattern_string.strip()))

    def validate(self, pattern_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a pattern string and return detailed error message.

        Args:
            pattern_string: Pattern string to validate

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        if not pattern_string:
            return False, "Pattern string cannot be empty"

        if not isinstance(pattern_string, str):
            return False, f"Pattern must be a string, got {type(pattern_string).__name__}"

        pattern_string = pattern_string.strip()

        if not pattern_string:
            return False, "Pattern string cannot be empty or whitespace only"

        if not self._compiled_regex.match(pattern_string):
            return False, (
                f"Invalid pattern format. Expected format: [BP]{{3}}-[BP] "
                f"(e.g., 'BBP-P;BPB-B'). Got: '{pattern_string}'"
            )

        return True, None

    def parse_patterns(self, pattern_string: str) -> list:
        """
        Parse a valid pattern string into individual patterns.

        Args:
            pattern_string: Valid pattern string

        Returns:
            List of pattern dictionaries with 'history' and 'decision' keys

        Raises:
            ValueError: If pattern string is invalid
        """
        is_valid, error = self.validate(pattern_string)
        if not is_valid:
            raise ValueError(error)

        patterns = []
        for pattern in pattern_string.strip().split(";"):
            history, decision = pattern.split("-")
            patterns.append({
                "history": history,
                "decision": decision,
            })

        return patterns


class CoordinateValidator:
    """Validator for table region coordinates."""

    def __init__(
        self,
        max_width: int = 1920,
        max_height: int = 1080,
    ):
        """
        Initialize coordinate validator.

        Args:
            max_width: Maximum canvas width
            max_height: Maximum canvas height
        """
        self.max_width = max_width
        self.max_height = max_height

    def is_valid_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> bool:
        """
        Check if a region is valid (within bounds).

        Args:
            x: X coordinate (left edge)
            y: Y coordinate (top edge)
            width: Region width
            height: Region height

        Returns:
            True if valid, False otherwise
        """
        is_valid, _ = self.validate_region(x, y, width, height)
        return is_valid

    def validate_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a region and return detailed error message.

        Args:
            x: X coordinate (left edge)
            y: Y coordinate (top edge)
            width: Region width
            height: Region height

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        # Check non-negative values
        if x < 0:
            return False, f"X coordinate must be non-negative, got {x}"
        if y < 0:
            return False, f"Y coordinate must be non-negative, got {y}"
        if width <= 0:
            return False, f"Width must be positive, got {width}"
        if height <= 0:
            return False, f"Height must be positive, got {height}"

        # Check bounds
        if x + width > self.max_width:
            return False, (
                f"Region exceeds canvas width: x({x}) + width({width}) = {x + width} > {self.max_width}"
            )
        if y + height > self.max_height:
            return False, (
                f"Region exceeds canvas height: y({y}) + height({height}) = {y + height} > {self.max_height}"
            )

        return True, None

    def validate_region_dict(self, region: Dict[str, int]) -> Tuple[bool, Optional[str]]:
        """
        Validate a region dictionary.

        Args:
            region: Dictionary with 'x', 'y', 'width', 'height' keys

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        required_keys = {"x", "y", "width", "height"}
        missing_keys = required_keys - set(region.keys())

        if missing_keys:
            return False, f"Missing required keys: {missing_keys}"

        return self.validate_region(
            region["x"],
            region["y"],
            region["width"],
            region["height"],
        )

    def check_drift(
        self,
        original: Dict[str, int],
        current: Dict[str, int],
        threshold: int = 5,
    ) -> Tuple[bool, int]:
        """
        Check if coordinates have drifted beyond threshold.

        Args:
            original: Original coordinates dict
            current: Current coordinates dict
            threshold: Maximum allowed drift in pixels

        Returns:
            Tuple of (has_drift, max_drift_amount)
        """
        max_drift = 0

        for key in ["x", "y"]:
            if key in original and key in current:
                drift = abs(original[key] - current[key])
                max_drift = max(max_drift, drift)

        return max_drift > threshold, max_drift


class TimerValidator:
    """Validator for timer values."""

    def __init__(
        self,
        click_threshold: int = 6,
        max_timer: int = 25,
    ):
        """
        Initialize timer validator.

        Args:
            click_threshold: Minimum timer value for clicking (exclusive)
            max_timer: Maximum expected timer value
        """
        self.click_threshold = click_threshold
        self.max_timer = max_timer

    def is_clickable(self, timer_value: int) -> bool:
        """
        Check if clicking is allowed based on timer value.

        Timer counts DOWN from 15/25 to 0.
        Clicking is allowed when timer > 6 (values 7-25).

        Args:
            timer_value: Current timer value

        Returns:
            True if clicking is allowed, False otherwise
        """
        return timer_value > self.click_threshold

    def is_countdown_phase(self, timer_value: int) -> bool:
        """
        Check if timer is in countdown phase (not clickable).

        Args:
            timer_value: Current timer value

        Returns:
            True if in countdown phase (timer <= 6)
        """
        return timer_value <= self.click_threshold

    def is_valid_timer(self, timer_value: int) -> bool:
        """
        Check if timer value is within expected range.

        Args:
            timer_value: Timer value to check

        Returns:
            True if valid (0-25), False otherwise
        """
        return 0 <= timer_value <= self.max_timer

    def detect_timer_reset(
        self,
        previous_timer: int,
        current_timer: int,
        reset_threshold: int = 10,
    ) -> bool:
        """
        Detect if timer has reset (new round started).

        Timer resets when it jumps from low value (1-6) to high value (15 or 25).

        Args:
            previous_timer: Previous timer value
            current_timer: Current timer value
            reset_threshold: Minimum jump to consider as reset

        Returns:
            True if timer reset detected, False otherwise
        """
        # Timer reset: jumps from low (1-6) to high (15 or 25)
        return (
            previous_timer <= self.click_threshold
            and current_timer > reset_threshold
            and current_timer > previous_timer
        )
