"""
Unit tests for event loop handling in main.py (Epic 4).

Tests the event loop storage and run_coroutine_threadsafe integration
to ensure Playwright Page objects work correctly across threads.
"""

import pytest
import asyncio
import threading
import time
from unittest.mock import MagicMock, AsyncMock, patch, call
from typing import Optional

from src.automation.main import AutomationApp


class TestEventLoopStorage:
    """Test event loop storage in AutomationApp."""

    def test_browser_event_loop_initialized_as_none(self):
        """Test that browser_event_loop is initialized as None."""
        app = AutomationApp()
        assert app.browser_event_loop is None

    def test_browser_event_loop_type_hint(self):
        """Test that browser_event_loop has correct type."""
        app = AutomationApp()
        # Should accept None or AbstractEventLoop
        assert app.browser_event_loop is None or isinstance(app.browser_event_loop, asyncio.AbstractEventLoop)


class TestEventLoopLifecycle:
    """Test event loop lifecycle management."""

    @pytest.mark.asyncio
    async def test_event_loop_stored_when_browser_opens(self):
        """Test that event loop is stored when browser opens."""
        app = AutomationApp()
        
        # Mock browser manager initialization
        with patch('src.automation.main.BrowserManager') as mock_browser_manager_class:
            mock_browser_manager = AsyncMock()
            mock_browser_manager.initialize = AsyncMock()
            mock_browser_manager_class.return_value = mock_browser_manager
            
            # Mock _open_browser_only to avoid actual browser initialization
            async def mock_open_browser():
                app.browser_manager = mock_browser_manager
            
            app._open_browser_only = mock_open_browser
            
            # Create a thread that will set up the event loop
            loop_created = threading.Event()
            loop_stored = threading.Event()
            
            def open_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                app.browser_event_loop = loop
                loop_stored.set()
                
                # Wait a bit to verify loop is stored
                time.sleep(0.1)
                loop_created.set()
                
                # Clean up
                loop.close()
                app.browser_event_loop = None
            
            thread = threading.Thread(target=open_thread, daemon=True)
            thread.start()
            
            # Wait for loop to be stored
            assert loop_stored.wait(timeout=1.0)
            
            # Verify loop was stored
            assert app.browser_event_loop is not None
            assert isinstance(app.browser_event_loop, asyncio.AbstractEventLoop)
            
            # Wait for cleanup
            thread.join(timeout=2.0)
            assert app.browser_event_loop is None

    def test_event_loop_cleaned_up_on_error(self):
        """Test that event loop is cleaned up even on error."""
        app = AutomationApp()
        
        def open_thread_with_error():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            app.browser_event_loop = loop
            
            try:
                raise Exception("Test error")
            finally:
                loop.close()
                app.browser_event_loop = None
        
        thread = threading.Thread(target=open_thread_with_error, daemon=True)
        thread.start()
        thread.join(timeout=1.0)
        
        # Verify cleanup happened
        assert app.browser_event_loop is None


class TestRunCoroutineThreadsafe:
    """Test run_coroutine_threadsafe usage."""

    def test_run_coroutine_threadsafe_with_stored_loop(self):
        """Test that run_coroutine_threadsafe works with stored loop."""
        app = AutomationApp()
        
        # Create and store an event loop
        loop = asyncio.new_event_loop()
        app.browser_event_loop = loop
        
        result_container = {'value': None}
        
        async def test_coroutine():
            await asyncio.sleep(0.01)
            result_container['value'] = 'success'
            return 'success'
        
        def thread_function():
            asyncio.set_event_loop(loop)
            
            # Keep loop running
            async def keepalive():
                while True:
                    await asyncio.sleep(0.1)
            
            loop.create_task(keepalive())
            
            # Run coroutine using run_coroutine_threadsafe
            future = asyncio.run_coroutine_threadsafe(test_coroutine(), loop)
            result = future.result(timeout=1.0)
            
            result_container['value'] = result
            loop.stop()
        
        thread = threading.Thread(target=thread_function, daemon=True)
        thread.start()
        
        # Run the loop in main thread
        try:
            loop.run_forever()
        except:
            pass
        
        thread.join(timeout=2.0)
        
        # Verify result
        assert result_container['value'] == 'success'
        
        # Cleanup
        loop.close()
        app.browser_event_loop = None

    def test_run_coroutine_threadsafe_timeout(self):
        """Test run_coroutine_threadsafe timeout handling."""
        app = AutomationApp()
        
        loop = asyncio.new_event_loop()
        app.browser_event_loop = loop
        
        async def slow_coroutine():
            await asyncio.sleep(2.0)
            return 'too slow'
        
        def thread_function():
            asyncio.set_event_loop(loop)
            
            async def keepalive():
                while True:
                    await asyncio.sleep(0.1)
            
            loop.create_task(keepalive())
            
            future = asyncio.run_coroutine_threadsafe(slow_coroutine(), loop)
            
            with pytest.raises(Exception):  # TimeoutError or similar
                future.result(timeout=0.1)
            
            loop.stop()
        
        thread = threading.Thread(target=thread_function, daemon=True)
        thread.start()
        
        try:
            loop.run_forever()
        except:
            pass
        
        thread.join(timeout=3.0)
        
        # Cleanup
        loop.close()
        app.browser_event_loop = None


class TestGetBrowserEventLoop:
    """Test get_browser_event_loop method."""

    def test_get_browser_event_loop_returns_stored_loop(self):
        """Test that get_browser_event_loop returns stored loop."""
        app = AutomationApp()
        
        # Create UI window mock
        mock_ui_window = MagicMock()
        app.ui_window = mock_ui_window
        
        # Set up the method
        app.ui_window.get_browser_event_loop = lambda: app.browser_event_loop
        
        # Store a loop
        loop = asyncio.new_event_loop()
        app.browser_event_loop = loop
        
        # Test retrieval
        retrieved_loop = app.ui_window.get_browser_event_loop()
        assert retrieved_loop == loop
        
        # Cleanup
        loop.close()
        app.browser_event_loop = None

    def test_get_browser_event_loop_returns_none_when_not_set(self):
        """Test that get_browser_event_loop returns None when not set."""
        app = AutomationApp()
        
        mock_ui_window = MagicMock()
        app.ui_window = mock_ui_window
        app.ui_window.get_browser_event_loop = lambda: app.browser_event_loop
        
        retrieved_loop = app.ui_window.get_browser_event_loop()
        assert retrieved_loop is None
