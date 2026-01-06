"""
Unit tests for PatternValidator (Epic 1).

Tests pattern format validation and parsing.
"""

import pytest
from src.automation.pattern_matching.pattern_validator import PatternValidator


class TestPatternValidator:
    """Test PatternValidator class."""

    def test_valid_single_pattern(self):
        """Test validation of a single valid pattern."""
        validator = PatternValidator()
        assert validator.is_valid("BBP-P") is True
        assert validator.is_valid("BPB-B") is True
        assert validator.is_valid("PPP-B") is True
        assert validator.is_valid("BBB-P") is True

    def test_valid_multiple_patterns(self):
        """Test validation of multiple patterns."""
        validator = PatternValidator()
        assert validator.is_valid("BBP-P;BPB-B") is True
        assert validator.is_valid("BBP-P;BPB-B;PPP-B") is True
        assert validator.is_valid("BBB-P;PPP-B;BPB-B;BBP-P") is True

    def test_invalid_empty_string(self):
        """Test validation rejects empty strings."""
        validator = PatternValidator()
        assert validator.is_valid("") is False
        assert validator.is_valid("   ") is False

    def test_invalid_wrong_length(self):
        """Test validation rejects patterns with wrong length."""
        validator = PatternValidator()
        assert validator.is_valid("BB-P") is False  # History too short
        assert validator.is_valid("BBBP-P") is False  # History too long
        assert validator.is_valid("BBP--P") is False  # Decision too long
        assert validator.is_valid("BBP-") is False  # Missing decision

    def test_invalid_characters(self):
        """Test validation rejects invalid characters."""
        validator = PatternValidator()
        assert validator.is_valid("ABC-P") is False  # Invalid history chars
        assert validator.is_valid("BBP-X") is False  # Invalid decision char
        assert validator.is_valid("123-P") is False  # Numbers not allowed

    def test_case_insensitive(self):
        """Test validation is case-insensitive."""
        validator = PatternValidator()
        assert validator.is_valid("bbp-p") is True
        assert validator.is_valid("Bbp-P") is True
        assert validator.is_valid("BBP-p") is True

    def test_validate_with_error_message(self):
        """Test validate() returns error messages."""
        validator = PatternValidator()
        
        # Valid pattern
        is_valid, error = validator.validate("BBP-P")
        assert is_valid is True
        assert error is None

        # Invalid pattern
        is_valid, error = validator.validate("ABC-P")
        assert is_valid is False
        assert error is not None
        assert "Invalid character" in error or "Invalid pattern format" in error

    def test_parse_patterns(self):
        """Test parsing valid patterns."""
        validator = PatternValidator()
        
        patterns = validator.parse_patterns("BBP-P;BPB-B")
        assert len(patterns) == 2
        assert patterns[0]["history"] == "BBP"
        assert patterns[0]["decision"] == "P"
        assert patterns[1]["history"] == "BPB"
        assert patterns[1]["decision"] == "B"

    def test_parse_patterns_raises_on_invalid(self):
        """Test parse_patterns raises ValueError on invalid input."""
        validator = PatternValidator()
        
        with pytest.raises(ValueError):
            validator.parse_patterns("invalid")

    def test_format_pattern(self):
        """Test formatting a single pattern."""
        validator = PatternValidator()
        
        pattern_str = validator.format_pattern("BBP", "P")
        assert pattern_str == "BBP-P"
        
        pattern_str = validator.format_pattern("bpB", "b")
        assert pattern_str == "BPB-B"

    def test_format_pattern_raises_on_invalid(self):
        """Test format_pattern raises ValueError on invalid input."""
        validator = PatternValidator()
        
        with pytest.raises(ValueError):
            validator.format_pattern("AB", "P")  # Invalid history length

    def test_combine_patterns(self):
        """Test combining multiple patterns."""
        validator = PatternValidator()
        
        patterns = [
            {"history": "BBP", "decision": "P"},
            {"history": "BPB", "decision": "B"},
        ]
        combined = validator.combine_patterns(patterns)
        assert combined == "BBP-P;BPB-B"

    def test_get_format_help(self):
        """Test format help text."""
        validator = PatternValidator()
        help_text = validator.get_format_help()
        assert isinstance(help_text, str)
        assert "Pattern Format" in help_text
        assert "B = Red" in help_text or "B = Banker" in help_text
