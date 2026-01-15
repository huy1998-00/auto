"""
Mini-Game Website Automation & Pattern Tracking Tool

Main entry point for the automation application.
"""

import asyncio
import os
import sys
import threading
import queue
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from .browser.browser_manager import BrowserManager, create_browser
from .browser.screenshot_capture import ScreenshotCapture
from .browser.click_executor import ClickExecutor
from .browser.page_monitor import PageMonitor
from .image_processing.image_extractor import ImageExtractor
from .image_processing.template_matcher import TemplateMatcher
from .image_processing.ocr_fallback import OCRFallback
from .pattern_matching.pattern_matcher import PatternMatcher
from .pattern_matching.pattern_validator import PatternValidator
from .data.session_manager import SessionManager
from .data.json_writer import JSONWriter
from .data.cache_manager import CacheManager
from .orchestration.table_tracker import TableTracker
from .orchestration.multi_table_manager import MultiTableManager
from .orchestration.screenshot_scheduler import ScreenshotScheduler
from .orchestration.error_recovery import ErrorRecovery
from .utils.logger import setup_logging, get_logger
from .utils.resource_monitor import ResourceMonitor
from .utils.coordinate_utils import CoordinateUtils
from .utils.env_manager import EnvManager
from .ui.main_window import MainWindow

# Application logger
logger = get_logger("main")


class AutomationApp:
    """
    Main automation application.

    Coordinates all components for multi-table game automation.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        game_url: Optional[str] = None,
        headless: bool = False,
        log_level: str = "INFO",
    ):
        """
        Initialize automation application.

        Args:
            config_path: Path to configuration directory
            game_url: Game URL to automate
            headless: Run browser in headless mode
            log_level: Logging level
        """
        self.config_path = Path(config_path or "config")
        # Load GAME_URL from command line, .env file, or environment variable
        self.game_url = game_url or EnvManager.load_game_url() or os.getenv("GAME_URL", "")
        self.headless = headless
        self.log_level = log_level

        # Setup logging
        log_file = Path("logs/automation.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure logs directory exists
        setup_logging(log_level=log_level, log_file=log_file)

        # Configuration
        self.table_regions_config: Dict[str, Any] = {}
        self.default_patterns_config: Dict[str, Any] = {}

        # Core components (initialized on start)
        self.browser_manager: Optional[BrowserManager] = None
        self.session_manager: Optional[SessionManager] = None
        self.cache_manager: Optional[CacheManager] = None
        self.multi_table_manager: Optional[MultiTableManager] = None
        self.page_monitor: Optional[PageMonitor] = None
        self.resource_monitor: Optional[ResourceMonitor] = None

        # State
        self._is_running: bool = False
        self.ui_window: Optional[MainWindow] = None
        self._ui_thread: Optional[threading.Thread] = None
        self.browser_event_loop: Optional[asyncio.AbstractEventLoop] = None

    def load_config(self) -> bool:
        """
        Load configuration files.

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Load table regions config
            table_regions_path = self.config_path / "table_regions.yaml"
            if table_regions_path.exists():
                with open(table_regions_path, "r") as f:
                    self.table_regions_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded table regions from {table_regions_path}")
            else:
                logger.warning(f"Table regions config not found: {table_regions_path}")

            # Load default patterns config
            default_patterns_path = self.config_path / "default_patterns.yaml"
            if default_patterns_path.exists():
                with open(default_patterns_path, "r") as f:
                    self.default_patterns_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded default patterns from {default_patterns_path}")
            else:
                logger.warning(f"Default patterns config not found: {default_patterns_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False

    async def initialize(self) -> bool:
        """
        Initialize all components.

        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Initializing automation application")

        # Load configuration
        if not self.load_config():
            logger.warning("Configuration load failed, using defaults")

        # Initialize browser manager
        self.browser_manager = BrowserManager(
            width=1920,
            height=1080,
            headless=self.headless,
        )
        await self.browser_manager.initialize()

        # Initialize session manager
        self.session_manager = SessionManager()
        self.session_manager.create_session()

        # Initialize JSON writer and cache manager
        json_writer = JSONWriter()
        self.cache_manager = CacheManager(
            session_manager=self.session_manager,
            json_writer=json_writer,
        )

        # Initialize resource monitor
        self.resource_monitor = ResourceMonitor()

        # Initialize screenshot scheduler
        screenshot_scheduler = ScreenshotScheduler(
            resource_monitor=self.resource_monitor,
        )

        # Initialize image extractor
        template_matcher = TemplateMatcher()
        template_matcher.load_templates()
        ocr_fallback = OCRFallback(lazy_load=True)
        image_extractor = ImageExtractor(
            template_matcher=template_matcher,
            ocr_fallback=ocr_fallback,
        )

        # Initialize error recovery
        error_recovery = ErrorRecovery()

        # Initialize multi-table manager
        self.multi_table_manager = MultiTableManager(
            browser_manager=self.browser_manager,
            session_manager=self.session_manager,
            cache_manager=self.cache_manager,
            image_extractor=image_extractor,
            screenshot_scheduler=screenshot_scheduler,
            error_recovery=error_recovery,
        )

        # Initialize page monitor
        self.page_monitor = PageMonitor(
            browser_manager=self.browser_manager,
        )

        logger.info("Application initialized successfully")
        return True

    async def navigate_to_game(self) -> bool:
        """
        Navigate browser to game URL.

        Returns:
            True if navigation successful, False otherwise
        """
        if not self.game_url:
            logger.error("No game URL configured")
            return False

        logger.info(f"Navigating to game: {self.game_url}")
        success = await self.browser_manager.navigate(
            url=self.game_url,
            wait_for_canvas=True,
        )

        if success:
            await self.page_monitor.start_monitoring()

        return success

    def add_table_from_config(self, table_id: int) -> bool:
        """
        Add a table using configuration.

        Args:
            table_id: Table ID to add (1-6)

        Returns:
            True if added successfully
        """
        tables_config = self.table_regions_config.get("tables", {})
        table_config = tables_config.get(table_id)

        if not table_config:
            logger.error(f"No configuration found for table {table_id}")
            return False

        # Get default patterns
        default_patterns = self.default_patterns_config.get("default_patterns", "")

        return self.multi_table_manager.add_table(
            table_id=table_id,
            table_region={
                "x": table_config["x"],
                "y": table_config["y"],
                "width": table_config["width"],
                "height": table_config["height"],
            },
            button_coords=table_config.get("buttons", {}),
            timer_region=table_config.get("timer", {}),
            blue_score_region=table_config.get("blue_score", {}),
            red_score_region=table_config.get("red_score", {}),
            patterns=default_patterns,
        )

    async def run_automation_loop(self) -> None:
        """
        Main automation loop.

        Continuously processes tables until stopped.
        """
        logger.info("Starting automation loop")
        self._is_running = True

        try:
            while self._is_running:
                # Check for page refresh
                if await self.page_monitor.check_page_refresh():
                    logger.warning("Page refresh detected, pausing tables")
                    self.multi_table_manager.pause_all()

                    # Wait for canvas to be ready
                    if await self.page_monitor.wait_for_canvas_ready():
                        logger.info("Canvas ready, resuming tables")
                        self.multi_table_manager.resume_all()
                    else:
                        logger.error("Canvas not ready after refresh")
                        continue

                # Process all tables
                results = await self.multi_table_manager.process_all_tables()

                # Get dynamic interval based on table states
                interval_ms = self.multi_table_manager.get_screenshot_interval()

                # Sleep before next iteration
                await asyncio.sleep(interval_ms / 1000)

        except asyncio.CancelledError:
            logger.info("Automation loop cancelled")
        except Exception as e:
            logger.error(f"Error in automation loop: {e}")
        finally:
            self._is_running = False

    def stop(self) -> None:
        """Stop the automation."""
        logger.info("Stopping automation")
        self._is_running = False

        if self.multi_table_manager:
            self.multi_table_manager.stop_all()

    async def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        logger.info("Shutting down application")

        # Stop automation
        self.stop()

        # Stop page monitoring
        if self.page_monitor:
            await self.page_monitor.stop_monitoring()

        # Flush all caches
        if self.cache_manager:
            self.cache_manager.flush_all()

        # End session
        if self.session_manager:
            self.session_manager.end_session()

        # Close browser
        if self.browser_manager:
            await self.browser_manager.close()

        logger.info("Application shutdown complete")

    def start_ui(self):
        """Start the UI (must be called from main thread)."""
        try:
            self.ui_window = MainWindow(
                on_open_browser=self._on_ui_open_browser,
                on_start=self._on_ui_start,
                on_stop=self._on_ui_stop,
                on_pattern_update=self._on_pattern_update,
                on_coordinates_update=self._on_coordinates_update,
            )
            if self.game_url:
                self.ui_window.game_url_var.set(self.game_url)
            
            # Add method to get browser page for coordinate picker
            self.ui_window.get_browser_page = lambda: self.browser_manager.page if self.browser_manager else None
            
            # Add method to get browser event loop for coordinate picker
            # Use a function that reads the current value, not a lambda that captures it
            def get_event_loop():
                return self.browser_event_loop
            self.ui_window.get_browser_event_loop = get_event_loop
            
            # Start UI update loop
            self._schedule_ui_updates()
            
            # Run UI main loop (blocks until window closed)
            self.ui_window.run()
        except Exception as e:
            logger.error(f"Failed to start UI: {e}", exc_info=True)
            print(f"\n[ERROR] Failed to start UI: {e}")
            print("Check logs/automation.log for details.")
            raise

    def _schedule_ui_updates(self):
        """Schedule periodic UI updates."""
        if self.ui_window:
            self.update_ui_status()
            self.ui_window.root.after(500, self._schedule_ui_updates)

    def _on_ui_open_browser(self, game_url: Optional[str]) -> None:
        """
        Handle UI open browser button click.
        
        Opens the browser in a background thread and maintains the event loop
        so that Playwright Page objects can be used from other threads via
        run_coroutine_threadsafe.
        
        Args:
            game_url: Optional URL to navigate to. If None, opens test page.
        """
        self.game_url = game_url
        
        # Save Game URL to .env file automatically if provided
        if game_url:
            EnvManager.save_game_url(game_url)
        
        # Open browser in background thread
        def open_thread() -> None:
            """
            Thread function that creates and maintains the browser event loop.
            
            This loop must stay alive for the lifetime of the browser session
            to allow Playwright Page objects to be used from other threads.
            """
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Store the loop reference for coordinate picker
            # This allows other threads to schedule coroutines using run_coroutine_threadsafe
            self.browser_event_loop = loop
            logger.info(f"Browser event loop stored: {loop}")
            
            try:
                # Run browser initialization
                loop.run_until_complete(self._open_browser_only())
                
                # Keep loop running so we can schedule coroutines to it later
                # Create a background task that keeps the loop alive
                async def keepalive() -> None:
                    """Background task to keep event loop running."""
                    while True:
                        await asyncio.sleep(1)
                
                loop.create_task(keepalive())
                
                # Run loop forever (until thread is killed)
                # This is necessary because Playwright Page objects are bound
                # to their original event loop and cannot be used in a different one
                loop.run_forever()
            except Exception as e:
                logger.error(f"Failed to open browser: {e}", exc_info=True)
                if self.ui_window:
                    self.ui_window.root.after(0, lambda: self.ui_window._on_browser_error(str(e)))
            finally:
                logger.info("Closing browser event loop")
                loop.close()
                self.browser_event_loop = None
        
        threading.Thread(target=open_thread, daemon=True).start()

    async def _open_browser_only(self):
        """
        Open browser (optionally navigate to URL, or open blank page).
        
        User can then manually navigate, login, and set up the page.
        Automation will start only after user clicks "Start Automation".
        """
        # Initialize browser manager only
        if not self.browser_manager:
            self.browser_manager = BrowserManager(
                width=1920,
                height=1080,
                headless=self.headless,
            )
            await self.browser_manager.initialize()

        # Navigate to URL if provided, otherwise open test page for coordinate picker
        if self.game_url:
            # Navigate to game URL (don't wait for canvas - user will navigate manually)
            if not await self.browser_manager.navigate(self.game_url, wait_for_canvas=False):
                raise Exception("Failed to navigate to game URL")
            logger.info(f"Browser opened and navigated to: {self.game_url}")
        else:
            # Open test page for coordinate picker testing
            test_page_path = Path(__file__).parent.parent.parent / "test_coordinate_picker.html"
            if test_page_path.exists():
                test_url = f"file:///{test_page_path.absolute().as_posix()}"
                await self.browser_manager.navigate(test_url, wait_for_canvas=False)
                logger.info("Browser opened with coordinate picker test page")
            else:
                # Fallback to blank page
                await self.browser_manager.navigate("about:blank", wait_for_canvas=False)
                logger.info("Browser opened (blank page - navigate manually)")

        # Don't start page monitoring yet - wait for user to be ready
        # User will manually navigate, login, and set up the page

        # Update UI
        if self.ui_window:
            self.ui_window.root.after(0, self.ui_window._on_browser_opened)

        logger.info("Please navigate, login, and set up the page manually.")
        logger.info("After setup, configure tables and patterns, then click 'Start Automation'.")

    def _on_ui_start(self):
        """Handle UI start button click (automation starts after configuration)."""
        # Start automation in background thread
        def start_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._start_automation_after_config())
        
        threading.Thread(target=start_thread, daemon=True).start()

    async def _start_automation_after_config(self):
        """
        Start automation after browser is opened and user has completed manual setup.
        
        This is called when user clicks "Start Automation" button.
        User should have already:
        1. Opened browser
        2. Manually navigated and logged in
        3. Set up the page
        4. Configured tables and patterns
        """
        # Browser should already be open
        if not self.browser_manager or not self.browser_manager.is_initialized:
            if self.ui_window:
                self.ui_window.log("Error: Browser not opened. Please open browser first.")
            return

        # Load configuration early to check table prerequisites
        self.load_config()

        # Check if tables are configured (required prerequisite)
        tables_config = self.table_regions_config.get("tables", {})
        if not tables_config:
            if self.ui_window:
                self.ui_window.log("Warning: No tables configured. Please configure tables first.")
                from tkinter import messagebox
                self.ui_window.root.after(0, lambda: messagebox.showwarning(
                    "No Tables Configured",
                    "No tables are configured.\n\n"
                    "Please:\n"
                    "1. Click 'Configure Tables'\n"
                    "2. Use visual picker to set table coordinates\n"
                    "3. Save configuration\n"
                    "4. Then click 'Start Automation' again"
                ))
            return

        # Browser page is available and tables are configured - proceed with automation
        if self.ui_window:
            self.ui_window.log("Starting automation...")

        # Initialize page monitor
        if not self.page_monitor:
            self.page_monitor = PageMonitor(self.browser_manager)
            await self.page_monitor.start_monitoring()

        # Initialize remaining components
        if not self.session_manager:
            self.session_manager = SessionManager()
            self.session_manager.create_session()

        if not self.cache_manager:
            json_writer = JSONWriter()
            self.cache_manager = CacheManager(
                session_manager=self.session_manager,
                json_writer=json_writer,
            )

        if not self.resource_monitor:
            self.resource_monitor = ResourceMonitor()

        # Initialize multi-table manager if not exists
        if not self.multi_table_manager:
            screenshot_scheduler = ScreenshotScheduler(
                resource_monitor=self.resource_monitor,
            )

            template_matcher = TemplateMatcher()
            template_matcher.load_templates()
            ocr_fallback = OCRFallback(lazy_load=True)
            image_extractor = ImageExtractor(
                template_matcher=template_matcher,
                ocr_fallback=ocr_fallback,
            )

            error_recovery = ErrorRecovery()

            self.multi_table_manager = MultiTableManager(
                browser_manager=self.browser_manager,
                session_manager=self.session_manager,
                cache_manager=self.cache_manager,
                image_extractor=image_extractor,
                screenshot_scheduler=screenshot_scheduler,
                error_recovery=error_recovery,
            )

        # Add tables from configuration (already validated above)
        tables_added = 0
        for table_id in tables_config.keys():
            if self.add_table_from_config(table_id):
                tables_added += 1
                if self.ui_window:
                    self.ui_window.log(f"Added table {table_id}")

        # Start all tables
        if self.multi_table_manager:
            self.multi_table_manager.start_all()
            if self.ui_window:
                self.ui_window.log(f"✓ Automation started with {tables_added} table(s)")
                self.ui_window.log("Automation is now running. Monitor status in the UI.")

        # Start automation loop
        await self.run_automation_loop()

    def _on_ui_stop(self):
        """Handle UI stop button click."""
        # Stop automation in background thread
        def stop_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._stop_automation())
        
        threading.Thread(target=stop_thread, daemon=True).start()

    def _on_pattern_update(self, table_id: int, patterns: str):
        """Handle pattern update from UI."""
        if self.multi_table_manager:
            self.multi_table_manager.set_patterns(table_id, patterns)
        logger.info(f"Pattern updated for Table {table_id}: {patterns}")
        if self.ui_window:
            self.ui_window.log(f"Pattern updated for Table {table_id}")

    def _on_coordinates_update(self, table_id: int, coords: Dict[str, Any]):
        """Handle coordinates update from UI."""
        # Save to config file
        config_path = self.config_path / "table_regions.yaml"
        
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {"tables": {}}

            if "tables" not in config:
                config["tables"] = {}

            config["tables"][table_id] = coords

            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Coordinates saved for Table {table_id}")
            if self.ui_window:
                self.ui_window.log(f"Coordinates saved for Table {table_id}")
            
            # Reload config
            self.load_config()
            
            # Update table if already added
            if self.multi_table_manager and table_id in self.multi_table_manager._tables:
                # Remove and re-add table with new coordinates
                self.multi_table_manager.remove_table(table_id)
                self.add_table_from_config(table_id)

        except Exception as e:
            logger.error(f"Failed to save coordinates: {e}")
            if self.ui_window:
                self.ui_window.log(f"Error saving coordinates: {e}")


    async def _stop_automation(self):
        """Stop automation from UI."""
        await self.shutdown()

    def update_ui_status(self):
        """Update UI with current status."""
        if not self.ui_window or not self.multi_table_manager:
            return

        # Update table statuses
        for table_id, tracker in self.multi_table_manager._tables.items():
            stats = tracker.get_statistics()
            self.ui_window.update_table_status(table_id, {
                "status": stats["status"],
                "timer": stats["current_timer"],
                "last_3_rounds": stats["last_3_rounds"],
                "pattern_match": tracker.pattern_matcher.get_patterns_string() if tracker.pattern_matcher.has_patterns() else None,
                "decision": tracker.state.last_decision,
            })

        # Update resources
        if self.resource_monitor:
            usage = self.resource_monitor.get_resource_usage()
            self.ui_window.update_resources(usage.cpu_percent, usage.memory_percent)

        # Process UI queue from multi-table manager
        if self.multi_table_manager:
            try:
                while True:
                    update = self.multi_table_manager.ui_queue.get_nowait()
                    if self.ui_window:
                        self.ui_window.ui_queue.put(update)
            except queue.Empty:
                pass

    async def run(self) -> None:
        """
        Run the complete automation flow.

        Initialize, navigate, add tables, and run loop.
        """
        try:
            # Initialize
            if not await self.initialize():
                logger.error("Initialization failed")
                return

            # Navigate to game
            if not await self.navigate_to_game():
                logger.error("Navigation failed")
                return

            # Add tables from configuration
            tables_config = self.table_regions_config.get("tables", {})
            for table_id in tables_config.keys():
                if self.add_table_from_config(table_id):
                    logger.info(f"Added table {table_id}")

            # Start all tables
            self.multi_table_manager.start_all()

            # Run automation loop
            await self.run_automation_loop()

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
        finally:
            await self.shutdown()


def main():
    """Entry point for the application."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Mini-Game Website Automation & Pattern Tracking Tool"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Game URL to automate",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config",
        help="Path to configuration directory",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Run without UI (command line only)",
    )

    args = parser.parse_args()

    # Create application
    app = AutomationApp(
        config_path=args.config,
        game_url=args.url,
        headless=args.headless,
        log_level=args.log_level,
    )

    try:
        if args.no_ui:
            # Run without UI
            asyncio.run(app.run())
        else:
            # Run with UI (blocks until window closed)
            app.start_ui()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n[ERROR] Application crashed: {e}")
        print("Check logs/automation.log for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
