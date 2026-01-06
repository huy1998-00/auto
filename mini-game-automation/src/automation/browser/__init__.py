"""
Browser automation module using Playwright.

Handles browser instance management, screenshot capture,
click execution, and page monitoring.
"""

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "BrowserManager":
        from .browser_manager import BrowserManager
        return BrowserManager
    elif name == "ScreenshotCapture":
        from .screenshot_capture import ScreenshotCapture
        return ScreenshotCapture
    elif name == "ClickExecutor":
        from .click_executor import ClickExecutor
        return ClickExecutor
    elif name == "PageMonitor":
        from .page_monitor import PageMonitor
        return PageMonitor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "BrowserManager",
    "ScreenshotCapture",
    "ClickExecutor",
    "PageMonitor",
]
