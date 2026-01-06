"""
Pattern matching module for game decision logic.

Handles pattern validation and priority-based matching
against user-defined patterns.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "PatternMatcher":
        from .pattern_matcher import PatternMatcher
        return PatternMatcher
    elif name == "PatternValidator":
        from .pattern_validator import PatternValidator
        return PatternValidator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "PatternMatcher",
    "PatternValidator",
]
