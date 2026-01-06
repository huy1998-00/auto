"""
Utility module for shared functionality.

Provides logging, validation, and coordinate utilities
used across all modules.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "get_logger":
        from .logger import get_logger
        return get_logger
    elif name == "setup_logging":
        from .logger import setup_logging
        return setup_logging
    elif name == "PatternFormatValidator":
        from .validators import PatternFormatValidator
        return PatternFormatValidator
    elif name == "CoordinateValidator":
        from .validators import CoordinateValidator
        return CoordinateValidator
    elif name == "CoordinateUtils":
        from .coordinate_utils import CoordinateUtils
        return CoordinateUtils
    elif name == "ResourceMonitor":
        from .resource_monitor import ResourceMonitor
        return ResourceMonitor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "get_logger",
    "setup_logging",
    "PatternFormatValidator",
    "CoordinateValidator",
    "CoordinateUtils",
    "ResourceMonitor",
]
