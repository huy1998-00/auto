"""
Unit tests for TableConfigWindow coordinate picker integration (Epic 4).

Tests the integration between TableConfigWindow and CoordinatePicker,
including event loop handling and UI callbacks.
"""

import pytest
import asyncio
import threading
from unittest.mock import MagicMock, AsyncMock, patch, call
from tkinter import Tk

from src.automation.ui.main_window import TableConfigWindow
from src.automation.ui.coordinate_picker import CoordinatePicker


class TestTableConfigWindowCoordinatePickerIntegration:
    """Test TableConfigWindow coordinate picker integration."""

    @pytest.fixture
    def mock_parent(self):
        """Create a mock parent window."""
        parent = MagicMock()
        return parent

    @pytest.fixture
    def mock_browser_page(self):
        """Create a mock browser page."""
        page = AsyncMock()
        page.url = "https://example.com"
        return page

    def test_get_browser_event_loop_method_exists(self, mock_parent):
        """Test that get_browser_event_loop method is set."""
        window = TableConfigWindow(mock_parent, browser_page=MagicMock())
        
        # Simulate setting the method (as done in main.py)
        mock_loop = MagicMock()
        window.get_browser_event_loop = lambda: mock_loop
        
        assert callable(window.get_browser_event_loop)
        assert window.get_browser_event_loop() == mock_loop

    def test_pick_table_region_without_browser_page(self, mock_parent):
        """Test pick_table_region when browser page is not available."""
        window = TableConfigWindow(mock_parent, browser_page=None)
        window.window = MagicMock()
        window.window.after = MagicMock()
        
        # Mock messagebox
        with patch('src.automation.ui.main_window.messagebox') as mock_msgbox:
            window._pick_table_region()
            
            # Should show warning
            window.window.after.assert_called()

    def test_pick_table_region_without_event_loop(self, mock_parent, mock_browser_page):
        """Test pick_table_region when event loop is not available."""
        window = TableConfigWindow(mock_parent, browser_page=mock_browser_page)
        window.window = MagicMock()
        window.window.after = MagicMock()
        
        # Don't set get_browser_event_loop
        window.get_browser_event_loop = None
        
        with patch('src.automation.ui.main_window.messagebox') as mock_msgbox:
            window._pick_table_region()
            
            # Should schedule error message
            window.window.after.assert_called()

    def test_apply_table_region(self, mock_parent):
        """Test applying picked table region to form."""
        window = TableConfigWindow(mock_parent, browser_page=MagicMock())
        
        # Create mock coordinate variables
        window.coord_vars = {
            'x': MagicMock(),
            'y': MagicMock(),
            'width': MagicMock(),
            'height': MagicMock()
        }
        window.status_var = MagicMock()
        
        result = {'x': 100, 'y': 200, 'width': 300, 'height': 250}
        
        with patch('src.automation.ui.main_window.messagebox') as mock_msgbox:
            window._apply_table_region(result)
            
            # Verify coordinates were set
            window.coord_vars['x'].set.assert_called_once_with('100')
            window.coord_vars['y'].set.assert_called_once_with('200')
            window.coord_vars['width'].set.assert_called_once_with('300')
            window.coord_vars['height'].set.assert_called_once_with('250')
            window.status_var.set.assert_called_once_with('✓ Table region captured')

    def test_pick_button_without_browser_page(self, mock_parent):
        """Test pick_button when browser page is not available."""
        window = TableConfigWindow(mock_parent, browser_page=None)
        window.window = MagicMock()
        window.window.after = MagicMock()
        
        with patch('src.automation.ui.main_window.messagebox') as mock_msgbox:
            window._pick_button('start')
            
            # Should show warning
            window.window.after.assert_called()

    def test_pick_button_without_event_loop(self, mock_parent, mock_browser_page):
        """Test pick_button when event loop is not available."""
        window = TableConfigWindow(mock_parent, browser_page=mock_browser_page)
        window.window = MagicMock()
        window.window.after = MagicMock()
        window.get_browser_event_loop = None
        
        with patch('src.automation.ui.main_window.messagebox') as mock_msgbox:
            window._pick_button('start')
            
            # Should schedule error message
            window.window.after.assert_called()


class TestTableConfigWindowErrorHandling:
    """Test error handling in TableConfigWindow coordinate picker."""

    def test_pick_table_region_exception_handling(self, mock_parent):
        """Test exception handling in pick_table_region."""
        window = TableConfigWindow(mock_parent, browser_page=MagicMock())
        window.window = MagicMock()
        window.window.after = MagicMock()
        
        loop = MagicMock()
        window.get_browser_event_loop = lambda: loop
        
        with patch('src.automation.ui.main_window.CoordinatePicker', side_effect=Exception("Test error")):
            with patch('src.automation.ui.main_window.messagebox') as mock_msgbox:
                window._pick_table_region()
                
                # Should schedule error message
                window.window.after.assert_called()
