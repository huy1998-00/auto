"""
Unit tests for CoordinatePicker (Epic 4).

Tests coordinate picker overlay injection, event loop handling,
and coordinate capture functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

from src.automation.ui.coordinate_picker import CoordinatePicker


class TestCoordinatePickerInitialization:
    """Test CoordinatePicker initialization."""

    def test_init(self):
        """Test CoordinatePicker initialization."""
        mock_page = MagicMock()
        picker = CoordinatePicker(mock_page)
        
        assert picker.page == mock_page
        assert picker.is_active is False

    def test_init_with_page(self):
        """Test initialization with Playwright Page object."""
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        
        picker = CoordinatePicker(mock_page)
        
        assert picker.page is not None
        assert picker.is_active is False


class TestCoordinatePickerScriptInjection:
    """Test JavaScript script injection."""

    @pytest.mark.asyncio
    async def test_picker_script_exists(self):
        """Test that PICKER_SCRIPT is defined."""
        assert hasattr(CoordinatePicker, 'PICKER_SCRIPT')
        assert isinstance(CoordinatePicker.PICKER_SCRIPT, str)
        assert len(CoordinatePicker.PICKER_SCRIPT) > 0

    @pytest.mark.asyncio
    async def test_picker_script_contains_overlay_creation(self):
        """Test that script creates overlay element."""
        script = CoordinatePicker.PICKER_SCRIPT
        assert '__coordinatePickerOverlay' in script
        assert 'document.createElement' in script
        assert 'position: fixed' in script

    @pytest.mark.asyncio
    async def test_picker_script_contains_mode_setting(self):
        """Test that script supports mode setting."""
        script = CoordinatePicker.PICKER_SCRIPT
        assert 'setMode' in script
        assert 'table' in script
        assert 'button' in script


class TestCoordinatePickerTableRegion:
    """Test table region picking functionality."""

    @pytest.mark.asyncio
    async def test_pick_table_region_success(self):
        """Test successful table region picking."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True,  # body_exists check
            'Picker initialized successfully',  # script injection
            True,  # picker_exists check
            True,  # overlay_visible check
            None,  # setMode call
            {'x': 100, 'y': 200, 'width': 300, 'height': 250}  # waitForResult
        ])
        
        picker = CoordinatePicker(mock_page)
        result = await picker.pick_table_region()
        
        assert result is not None
        assert result['x'] == 100
        assert result['y'] == 200
        assert result['width'] == 300
        assert result['height'] == 250
        assert picker.is_active is False

    @pytest.mark.asyncio
    async def test_pick_table_region_cancelled(self):
        """Test cancelled table region picking."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True,  # body_exists check
            'Picker initialized successfully',  # script injection
            True,  # picker_exists check
            True,  # overlay_visible check
            None,  # setMode call
            None  # waitForResult (cancelled)
        ])
        
        picker = CoordinatePicker(mock_page)
        result = await picker.pick_table_region()
        
        assert result is None
        assert picker.is_active is False

    @pytest.mark.asyncio
    async def test_pick_table_region_timeout(self):
        """Test table region picking timeout."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True,  # body_exists check
            'Picker initialized successfully',  # script injection
            True,  # picker_exists check
            True,  # overlay_visible check
            None,  # setMode call
            asyncio.TimeoutError()  # waitForResult timeout
        ])
        
        picker = CoordinatePicker(mock_page)
        
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
            result = await picker.pick_table_region()
        
        assert result is None
        assert picker.is_active is False

    @pytest.mark.asyncio
    async def test_pick_table_region_no_body(self):
        """Test picking when page body doesn't exist."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=False)  # body_exists = False
        
        picker = CoordinatePicker(mock_page)
        
        # The exception is caught and handled, returning None
        result = await picker.pick_table_region()
        
        assert result is None
        assert picker.is_active is False

    @pytest.mark.asyncio
    async def test_pick_table_region_picker_not_created(self):
        """Test when picker script fails to create picker."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True,  # body_exists check
            'Picker initialized successfully',  # script injection
            False,  # picker_exists check fails
            None  # stop_picking cleanup call
        ])
        
        picker = CoordinatePicker(mock_page)
        
        # The exception is caught and handled, returning None
        result = await picker.pick_table_region()
        
        assert result is None
        assert picker.is_active is False


class TestCoordinatePickerButtonPosition:
    """Test button position picking functionality."""

    @pytest.mark.asyncio
    async def test_pick_button_position_success(self):
        """Test successful button position picking."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True,  # body_exists check
            'Picker initialized successfully',  # script injection
            True,  # picker_exists check
            True,  # overlay_visible check
            None,  # setMode call
            {'x': 150, 'y': 250}  # waitForResult
        ])
        
        picker = CoordinatePicker(mock_page)
        result = await picker.pick_button_position()
        
        assert result is not None
        assert result['x'] == 150
        assert result['y'] == 250
        assert 'width' not in result
        assert 'height' not in result


class TestCoordinatePickerStopPicking:
    """Test stop picking functionality."""

    @pytest.mark.asyncio
    async def test_stop_picking_when_active(self):
        """Test stopping picker when active."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock()
        
        picker = CoordinatePicker(mock_page)
        picker.is_active = True
        
        await picker.stop_picking()
        
        mock_page.evaluate.assert_called_once()
        assert 'destroy' in mock_page.evaluate.call_args[0][0]
        assert picker.is_active is False

    @pytest.mark.asyncio
    async def test_stop_picking_when_inactive(self):
        """Test stopping picker when not active."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock()
        
        picker = CoordinatePicker(mock_page)
        picker.is_active = False
        
        await picker.stop_picking()
        
        # Should not call evaluate when inactive
        mock_page.evaluate.assert_not_called()
        assert picker.is_active is False

    @pytest.mark.asyncio
    async def test_stop_picking_handles_exception(self):
        """Test stop picking handles exceptions gracefully."""
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=Exception("Page closed"))
        
        picker = CoordinatePicker(mock_page)
        picker.is_active = True
        
        # Should not raise exception
        await picker.stop_picking()
        
        assert picker.is_active is False


class TestCoordinatePickerConcurrency:
    """Test concurrent picker usage."""

    @pytest.mark.asyncio
    async def test_multiple_picks_sequential(self):
        """Test multiple sequential picks."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            # First pick
            True, 'Picker initialized', True, True, None, {'x': 100, 'y': 200, 'width': 300, 'height': 250},
            # Second pick
            True, 'Picker initialized', True, True, None, {'x': 200, 'y': 300, 'width': 400, 'height': 350},
        ])
        
        picker = CoordinatePicker(mock_page)
        
        result1 = await picker.pick_table_region()
        result2 = await picker.pick_table_region()
        
        assert result1['x'] == 100
        assert result2['x'] == 200

    @pytest.mark.asyncio
    async def test_picker_stops_previous_when_active(self):
        """Test that picker stops previous instance when starting new one."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True, 'Picker initialized', True, True, None, {'x': 100, 'y': 200, 'width': 300, 'height': 250}
        ])
        
        picker = CoordinatePicker(mock_page)
        picker.is_active = True
        
        # Should call stop_picking first
        with patch.object(picker, 'stop_picking', new_callable=AsyncMock) as mock_stop:
            await picker.pick_table_region()
            mock_stop.assert_called_once()


class TestCoordinatePickerModes:
    """Test different picker modes."""

    @pytest.mark.asyncio
    async def test_pick_timer_region(self):
        """Test timer region picking."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True, 'Picker initialized', True, True, None, {'x': 50, 'y': 50, 'width': 100, 'height': 50}
        ])
        
        picker = CoordinatePicker(mock_page)
        result = await picker.pick_timer_region()
        
        assert result is not None
        # Verify setMode was called with 'timer'
        calls = [call[0][0] for call in mock_page.evaluate.call_args_list if 'setMode' in str(call)]
        assert any('timer' in str(call) for call in calls)

    @pytest.mark.asyncio
    async def test_pick_score_region(self):
        """Test score region picking."""
        mock_page = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=[
            True, 'Picker initialized', True, True, None, {'x': 50, 'y': 50, 'width': 100, 'height': 50}
        ])
        
        picker = CoordinatePicker(mock_page)
        result = await picker.pick_score_region()
        
        assert result is not None
        # Verify setMode was called with 'score'
        calls = [call[0][0] for call in mock_page.evaluate.call_args_list if 'setMode' in str(call)]
        assert any('score' in str(call) for call in calls)
