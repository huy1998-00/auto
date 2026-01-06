"""
Data persistence module for JSON storage.

Handles session management, thread-safe JSON writing,
and in-memory cache with write-through strategy.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "SessionManager":
        from .session_manager import SessionManager
        return SessionManager
    elif name == "JSONWriter":
        from .json_writer import JSONWriter
        return JSONWriter
    elif name == "CacheManager":
        from .cache_manager import CacheManager
        return CacheManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "SessionManager",
    "JSONWriter",
    "CacheManager",
]
