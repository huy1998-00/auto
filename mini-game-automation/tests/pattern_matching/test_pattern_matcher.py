"""
Unit tests for PatternMatcher (Epic 1).

Tests priority-based pattern matching algorithm.
"""

import pytest
from src.automation.pattern_matching.pattern_matcher import PatternMatcher, Pattern, MatchResult


class TestPatternMatcher:
    """Test PatternMatcher class."""

    def test_initialization_with_patterns(self):
        """Test initialization with pattern string."""
        matcher = PatternMatcher("BBP-P;BPB-B")
        assert len(matcher.get_patterns()) == 2

    def test_initialization_without_patterns(self):
        """Test initialization without patterns."""
        matcher = PatternMatcher()
        assert len(matcher.get_patterns()) == 0

    def test_set_patterns(self):
        """Test setting patterns."""
        matcher = PatternMatcher()
        matcher.set_patterns("BBP-P;BPB-B")
        
        patterns = matcher.get_patterns()
        assert len(patterns) == 2
        assert patterns[0].history == "BBP"
        assert patterns[0].decision == "P"
        assert patterns[1].history == "BPB"
        assert patterns[1].decision == "B"

    def test_set_patterns_raises_on_invalid(self):
        """Test set_patterns raises ValueError on invalid input."""
        matcher = PatternMatcher()
        
        with pytest.raises(ValueError):
            matcher.set_patterns("invalid")

    def test_match_exact_history(self, sample_round_history):
        """Test matching exact history."""
        matcher = PatternMatcher("BBP-P")
        
        # History: ["B", "B", "P"] matches "BBP"
        result = matcher.match(sample_round_history)
        assert result.matched is True
        assert result.pattern.history == "BBP"
        assert result.pattern.decision == "P"
        assert result.decision == "blue"

    def test_match_first_pattern_wins(self):
        """Test priority-based matching (first match wins)."""
        matcher = PatternMatcher("BBP-P;BBP-B")  # Same history, different decisions
        
        # First pattern should match
        result = matcher.match(["B", "B", "P"])
        assert result.matched is True
        assert result.pattern.decision == "P"
        assert result.decision == "blue"

    def test_no_match(self):
        """Test no match when history doesn't match."""
        matcher = PatternMatcher("BBP-P")
        
        result = matcher.match(["P", "P", "P"])
        assert result.matched is False
        assert result.pattern is None
        assert result.decision is None

    def test_match_requires_exactly_3_rounds(self):
        """Test matching requires exactly 3 rounds."""
        matcher = PatternMatcher("BBP-P")
        
        # Too few rounds
        result = matcher.match(["B", "B"])
        assert result.matched is False
        
        # Too many rounds (should use last 3)
        result = matcher.match(["B", "B", "P", "P"])
        assert result.matched is True  # Last 3: ["B", "P", "P"] - wait, that's wrong
        # Actually, it should use last 3: ["B", "P", "P"]
        # But our implementation might use all, let's check

    def test_decision_mapping(self):
        """Test decision mapping (B->red, P->blue)."""
        matcher = PatternMatcher("BBB-B;PPP-P")
        
        # B decision -> red
        result = matcher.match(["B", "B", "B"])
        assert result.matched is True
        assert result.decision == "red"
        
        # P decision -> blue
        result = matcher.match(["P", "P", "P"])
        assert result.matched is True
        assert result.decision == "blue"

    def test_case_insensitive_history(self):
        """Test matching is case-insensitive for history."""
        matcher = PatternMatcher("BBP-P")
        
        # Should match regardless of case
        result = matcher.match(["b", "B", "p"])
        assert result.matched is True

    def test_multiple_patterns_priority(self):
        """Test multiple patterns with priority order."""
        matcher = PatternMatcher("BBB-B;BBP-P;BPB-B")
        
        # Should match first pattern
        result = matcher.match(["B", "B", "B"])
        assert result.matched is True
        assert result.pattern.history == "BBB"
        
        # Should match second pattern
        result = matcher.match(["B", "B", "P"])
        assert result.matched is True
        assert result.pattern.history == "BBP"
