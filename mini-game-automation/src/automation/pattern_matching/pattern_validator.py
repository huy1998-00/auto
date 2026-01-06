"""
Pattern format validation using regex.

Validates pattern strings against the required format:
^[BP]{3}-[BP](;[BP]{3}-[BP])*$
"""

import re
from typing import Tuple, Optional, List

from ..utils.logger import get_logger

logger = get_logger("pattern_validator")


# Pattern validation regex from architecture specification
PATTERN_REGEX = r"^[BP]{3}-[BP](;[BP]{3}-[BP])*$"


class PatternValidator:
    """
    Validates pattern format strings.

    Pattern format: BBP-P;BPB-B
    - Each pattern: [BP]{3}-[BP] (3 history chars + 1 decision char)
    - Multiple patterns separated by semicolons
    - B = Red team (Banker)
    - P = Blue team (Player)
    """

    def __init__(self, regex_pattern: str = PATTERN_REGEX):
        """
        Initialize pattern validator.

        Args:
            regex_pattern: Regex for valid pattern format
        """
        self.regex_pattern = regex_pattern
        self._compiled_regex = re.compile(regex_pattern)

    def is_valid(self, pattern_string: str) -> bool:
        """
        Check if a pattern string is valid.

        Args:
            pattern_string: Pattern string to validate

        Returns:
            True if valid, False otherwise
        """
        if not pattern_string or not isinstance(pattern_string, str):
            return False

        return bool(self._compiled_regex.match(pattern_string.strip().upper()))

    def validate(self, pattern_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a pattern string with detailed error message.

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

        # Normalize to uppercase
        pattern_string = pattern_string.upper()

        if not self._compiled_regex.match(pattern_string):
            # Provide helpful error message
            error_details = self._get_validation_error(pattern_string)
            return False, error_details

        return True, None

    def _get_validation_error(self, pattern_string: str) -> str:
        """
        Get detailed validation error for an invalid pattern.

        Args:
            pattern_string: Invalid pattern string

        Returns:
            Detailed error message
        """
        patterns = pattern_string.split(";")

        for i, pattern in enumerate(patterns):
            parts = pattern.split("-")

            if len(parts) != 2:
                return (
                    f"Pattern {i + 1} ('{pattern}'): Must have format 'XXX-X' "
                    f"(3 characters, dash, 1 character)"
                )

            history, decision = parts

            if len(history) != 3:
                return (
                    f"Pattern {i + 1} ('{pattern}'): History must be exactly 3 characters, "
                    f"got {len(history)}"
                )

            for j, char in enumerate(history):
                if char not in "BP":
                    return (
                        f"Pattern {i + 1} ('{pattern}'): Invalid character '{char}' in history. "
                        f"Only 'B' (Red) and 'P' (Blue) are allowed"
                    )

            if len(decision) != 1:
                return (
                    f"Pattern {i + 1} ('{pattern}'): Decision must be exactly 1 character, "
                    f"got {len(decision)}"
                )

            if decision not in "BP":
                return (
                    f"Pattern {i + 1} ('{pattern}'): Invalid decision '{decision}'. "
                    f"Only 'B' (Red) and 'P' (Blue) are allowed"
                )

        return (
            f"Invalid pattern format. Expected format: [BP]{{3}}-[BP] "
            f"(e.g., 'BBP-P;BPB-B'). Got: '{pattern_string}'"
        )

    def parse_patterns(self, pattern_string: str) -> List[dict]:
        """
        Parse a valid pattern string into pattern dictionaries.

        Args:
            pattern_string: Valid pattern string

        Returns:
            List of {'history': str, 'decision': str} dicts

        Raises:
            ValueError: If pattern string is invalid
        """
        is_valid, error = self.validate(pattern_string)
        if not is_valid:
            raise ValueError(error)

        patterns = []
        for pattern in pattern_string.strip().upper().split(";"):
            history, decision = pattern.split("-")
            patterns.append({
                "history": history,
                "decision": decision,
            })

        return patterns

    def format_pattern(self, history: str, decision: str) -> str:
        """
        Format a single pattern as string.

        Args:
            history: 3-character history
            decision: Decision character

        Returns:
            Formatted pattern string (e.g., "BBP-P")

        Raises:
            ValueError: If pattern components are invalid
        """
        pattern_str = f"{history.upper()}-{decision.upper()}"
        is_valid, error = self.validate(pattern_str)

        if not is_valid:
            raise ValueError(error)

        return pattern_str

    def combine_patterns(self, patterns: List[dict]) -> str:
        """
        Combine multiple patterns into a pattern string.

        Args:
            patterns: List of {'history': str, 'decision': str} dicts

        Returns:
            Combined pattern string (e.g., "BBP-P;BPB-B")

        Raises:
            ValueError: If any pattern is invalid
        """
        pattern_strings = []

        for pattern in patterns:
            history = pattern.get("history", "")
            decision = pattern.get("decision", "")
            pattern_strings.append(self.format_pattern(history, decision))

        combined = ";".join(pattern_strings)

        # Validate the combined result
        is_valid, error = self.validate(combined)
        if not is_valid:
            raise ValueError(error)

        return combined

    @staticmethod
    def get_format_help() -> str:
        """
        Get help text explaining the pattern format.

        Returns:
            Help text string
        """
        return """
Pattern Format Help:

Format: [history]-[decision]
- History: 3 characters representing the last 3 round results
- Decision: 1 character representing the bet decision

Characters:
- B = Red team (Banker)
- P = Blue team (Player)

Examples:
- "BBP-P" = If last 3 rounds were Red, Red, Blue, then bet Blue
- "BPB-B" = If last 3 rounds were Red, Blue, Red, then bet Red
- "PPP-B" = If last 3 rounds were Blue, Blue, Blue, then bet Red

Multiple patterns are separated by semicolons:
- "BBP-P;BPB-B;PPP-B"

Patterns are matched in order (first match wins).
""".strip()
