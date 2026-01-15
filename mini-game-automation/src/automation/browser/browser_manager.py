"""
Browser instance management using Playwright.

Manages a single Playwright browser instance with fixed window size (1920x1080)
as required by the architecture specification.
"""

import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from ..utils.logger import get_logger

logger = get_logger("browser_manager")


class BrowserManager:
    """
    Manages a single Playwright browser instance.

    Enforces single browser instance constraint (NFR5) and
    provides fixed window size (1920x1080).
    """

    # Default browser settings
    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080
    CANVAS_SELECTOR = "#layaCanvas"

    def __init__(
        self,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        headless: bool = False,
    ):
        """
        Initialize browser manager.

        Args:
            width: Browser window width (default: 1920)
            height: Browser window height (default: 1080)
            headless: Run browser in headless mode (default: False)
        """
        self.width = width
        self.height = height
        self.headless = headless

        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._is_initialized = False
        self._original_canvas_box: Optional[Dict[str, int]] = None

    @property
    def is_initialized(self) -> bool:
        """Check if browser is initialized."""
        return self._is_initialized and self._page is not None

    @property
    def page(self) -> Optional[Page]:
        """Get the current page instance."""
        return self._page

    async def initialize(self) -> None:
        """
        Initialize Playwright and launch browser.

        Creates a single browser instance with fixed viewport.
        """
        if self._is_initialized:
            logger.warning("Browser already initialized")
            return

        logger.info("Initializing Playwright browser")

        self._playwright = await async_playwright().start()

        # Launch Chromium browser
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
        )

        # Create browser context with fixed viewport
        self._context = await self._browser.new_context(
            viewport={"width": self.width, "height": self.height},
            # Disable viewport resizing
            no_viewport=False,
        )

        # Create single page
        self._page = await self._context.new_page()

        self._is_initialized = True
        logger.info(f"Browser initialized with viewport {self.width}x{self.height}")

    async def navigate(self, url: str, wait_for_canvas: bool = True) -> bool:
        """
        Navigate to a URL and optionally wait for canvas element.

        Args:
            url: URL to navigate to
            wait_for_canvas: Whether to wait for canvas element

        Returns:
            True if navigation successful, False otherwise
        """
        if not self._page:
            logger.error("Browser not initialized")
            return False

        try:
            logger.info(f"Navigating to {url}")
            await self._page.goto(url, wait_until="domcontentloaded")

            if wait_for_canvas:
                await self.wait_for_canvas()

            return True

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    async def wait_for_canvas(self, timeout: int = 30000) -> bool:
        """
        Wait for canvas element to be available.

        Args:
            timeout: Maximum wait time in milliseconds

        Returns:
            True if canvas found, False otherwise
        """
        if not self._page:
            return False

        try:
            logger.info(f"Waiting for canvas element: {self.CANVAS_SELECTOR}")
            await self._page.wait_for_selector(
                self.CANVAS_SELECTOR,
                timeout=timeout,
                state="visible",
            )

            # Store original canvas position for drift detection
            self._original_canvas_box = await self.get_canvas_box()
            logger.info(f"Canvas found at position: {self._original_canvas_box}")

            return True

        except Exception as e:
            logger.error(f"Canvas not found: {e}")
            return False

    async def get_canvas_box(self) -> Optional[Dict[str, int]]:
        """
        Get canvas element bounding box.

        Returns:
            Dictionary with 'x', 'y', 'width', 'height' or None
        """
        if not self._page:
            return None

        try:
            canvas = await self._page.query_selector(self.CANVAS_SELECTOR)
            if canvas:
                box = await canvas.bounding_box()
                if box:
                    return {
                        "x": int(box["x"]),
                        "y": int(box["y"]),
                        "width": int(box["width"]),
                        "height": int(box["height"]),
                    }
            return None

        except Exception as e:
            logger.error(f"Failed to get canvas box: {e}")
            return None

    async def get_canvas_box_with_retry(self, timeout_ms: int = 2000) -> Optional[Dict[str, int]]:
        """
        Get canvas box with short retry if not found.
        
        Useful for operations that need canvas but can wait briefly.
        Canvas may appear dynamically after page load.
        
        Args:
            timeout_ms: Maximum wait time in milliseconds (default: 2000ms)
        
        Returns:
            Canvas bounding box dictionary or None if not found after retry
        """
        canvas_box = await self.get_canvas_box()
        if canvas_box:
            return canvas_box
        
        # Canvas not found, wait briefly
        logger.debug(f"Canvas not found, waiting {timeout_ms}ms...")
        if await self.wait_for_canvas(timeout=timeout_ms):
            return await self.get_canvas_box()
        
        return None

    async def get_original_canvas_box(self) -> Optional[Dict[str, int]]:
        """
        Get the original canvas box stored at initialization.

        Used for drift detection.

        Returns:
            Original canvas bounding box or None
        """
        return self._original_canvas_box

    async def is_page_loaded(self) -> bool:
        """
        Check if page is fully loaded.

        Returns:
            True if page is loaded, False otherwise
        """
        if not self._page:
            return False

        try:
            state = await self._page.evaluate("document.readyState")
            return state == "complete"

        except Exception:
            return False

    async def get_page_url(self) -> Optional[str]:
        """
        Get current page URL.

        Returns:
            Current URL or None
        """
        if not self._page:
            return None
        return self._page.url

    async def is_page_closed(self) -> bool:
        """
        Check if page is closed.

        Returns:
            True if page is closed, False otherwise
        """
        if not self._page:
            return True
        return self._page.is_closed()

    async def refresh_page(self) -> bool:
        """
        Refresh the current page.

        Returns:
            True if refresh successful, False otherwise
        """
        if not self._page:
            return False

        try:
            await self._page.reload(wait_until="domcontentloaded")
            return True

        except Exception as e:
            logger.error(f"Page refresh failed: {e}")
            return False

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        logger.info("Closing browser")

        if self._page:
            await self._page.close()
            self._page = None

        if self._context:
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._is_initialized = False
        logger.info("Browser closed")

    async def __aenter__(self) -> "BrowserManager":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()


@asynccontextmanager
async def create_browser(
    width: int = BrowserManager.DEFAULT_WIDTH,
    height: int = BrowserManager.DEFAULT_HEIGHT,
    headless: bool = False,
):
    """
    Create a browser manager as an async context manager.

    Args:
        width: Browser window width
        height: Browser window height
        headless: Run in headless mode

    Yields:
        Initialized BrowserManager instance
    """
    manager = BrowserManager(width=width, height=height, headless=headless)
    try:
        await manager.initialize()
        yield manager
    finally:
        await manager.close()
