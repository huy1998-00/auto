"""
Orchestration module for multi-table coordination.

Handles table state tracking, multi-table management,
screenshot scheduling, and error recovery.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "TableTracker":
        from .table_tracker import TableTracker
        return TableTracker
    elif name == "MultiTableManager":
        from .multi_table_manager import MultiTableManager
        return MultiTableManager
    elif name == "ScreenshotScheduler":
        from .screenshot_scheduler import ScreenshotScheduler
        return ScreenshotScheduler
    elif name == "ErrorRecovery":
        from .error_recovery import ErrorRecovery
        return ErrorRecovery
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "TableTracker",
    "MultiTableManager",
    "ScreenshotScheduler",
    "ErrorRecovery",
]
