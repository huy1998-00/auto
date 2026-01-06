"""
Unit tests for MultiTableManager (Epic 2).

Tests multi-table parallel processing and thread management.
"""

import pytest
import threading
import time
from unittest.mock import Mock, MagicMock, patch
from src.automation.orchestration.multi_table_manager import MultiTableManager, MAX_TABLES


class TestMultiTableManager:
    """Test MultiTableManager class."""

    @pytest.fixture
    def mock_browser_manager(self):
        """Create mock browser manager."""
        mock = Mock()
        mock.is_initialized = True
        mock.page = Mock()
        return mock

    @pytest.fixture
    def mock_session_manager(self, temp_session_dir):
        """Create mock session manager."""
        from src.automation.data.session_manager import SessionManager
        manager = SessionManager(base_path=str(temp_session_dir))
        manager.create_session()
        return manager

    @pytest.fixture
    def mock_cache_manager(self):
        """Create mock cache manager."""
        from src.automation.data.cache_manager import CacheManager
        from src.automation.data.session_manager import SessionManager
        from src.automation.data.json_writer import JSONWriter
        
        session_manager = Mock()
        json_writer = JSONWriter()
        return CacheManager(session_manager=session_manager, json_writer=json_writer)

    @pytest.fixture
    def manager(self, mock_browser_manager, mock_session_manager, mock_cache_manager):
        """Create MultiTableManager instance."""
        return MultiTableManager(
            browser_manager=mock_browser_manager,
            session_manager=mock_session_manager,
            cache_manager=mock_cache_manager,
        )

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.browser_manager is not None
        assert manager.session_manager is not None
        assert len(manager._tables) == 0
        assert manager._is_running is False

    def test_add_table(self, manager):
        """Test adding a table."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {
            "blue": {"x": 10, "y": 20},
            "red": {"x": 30, "y": 40},
            "confirm": {"x": 50, "y": 60},
            "cancel": {"x": 70, "y": 80},
        }
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        result = manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
            patterns="BBP-P",
        )
        
        assert result is True
        assert 1 in manager._tables
        assert 1 in manager._table_configs
        assert 1 in manager._table_locks

    def test_add_table_max_limit(self, manager):
        """Test adding tables up to MAX_TABLES limit."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"blue": {"x": 10, "y": 20}, "red": {"x": 30, "y": 40},
                        "confirm": {"x": 50, "y": 60}, "cancel": {"x": 70, "y": 80}}
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        # Add MAX_TABLES tables
        for i in range(1, MAX_TABLES + 1):
            result = manager.add_table(
                table_id=i,
                table_region=table_region,
                button_coords=button_coords,
                timer_region=timer_region,
                blue_score_region=blue_score,
                red_score_region=red_score,
            )
            assert result is True
        
        # Try to add one more (should fail)
        result = manager.add_table(
            table_id=MAX_TABLES + 1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        assert result is False

    def test_add_duplicate_table(self, manager):
        """Test adding duplicate table returns False."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"blue": {"x": 10, "y": 20}, "red": {"x": 30, "y": 40},
                        "confirm": {"x": 50, "y": 60}, "cancel": {"x": 70, "y": 80}}
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        # Add table once
        result1 = manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        assert result1 is True
        
        # Try to add again
        result2 = manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        assert result2 is False

    def test_remove_table(self, manager):
        """Test removing a table."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"blue": {"x": 10, "y": 20}, "red": {"x": 30, "y": 40},
                        "confirm": {"x": 50, "y": 60}, "cancel": {"x": 70, "y": 80}}
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        
        result = manager.remove_table(1)
        assert result is True
        assert 1 not in manager._tables

    def test_remove_nonexistent_table(self, manager):
        """Test removing nonexistent table returns False."""
        result = manager.remove_table(999)
        assert result is False

    def test_set_patterns(self, manager):
        """Test setting patterns for a table."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"blue": {"x": 10, "y": 20}, "red": {"x": 30, "y": 40},
                        "confirm": {"x": 50, "y": 60}, "cancel": {"x": 70, "y": 80}}
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        
        result = manager.set_patterns(1, "BBP-P;BPB-B")
        assert result is True
        
        tracker = manager._tables[1]
        assert tracker.state.patterns == "BBP-P;BPB-B"

    def test_get_table_status(self, manager):
        """Test getting table status."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"blue": {"x": 10, "y": 20}, "red": {"x": 30, "y": 40},
                        "confirm": {"x": 50, "y": 60}, "cancel": {"x": 70, "y": 80}}
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        
        status = manager.get_table_status(1)
        assert status is not None
        assert "table_id" in status
        assert "status" in status

    def test_get_all_table_statuses(self, manager):
        """Test getting all table statuses."""
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"blue": {"x": 10, "y": 20}, "red": {"x": 30, "y": 40},
                        "confirm": {"x": 50, "y": 60}, "cancel": {"x": 70, "y": 80}}
        timer_region = {"x": 5, "y": 5, "width": 50, "height": 30}
        blue_score = {"x": 10, "y": 10, "width": 30, "height": 20}
        red_score = {"x": 40, "y": 10, "width": 30, "height": 20}
        
        manager.add_table(
            table_id=1,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        manager.add_table(
            table_id=2,
            table_region=table_region,
            button_coords=button_coords,
            timer_region=timer_region,
            blue_score_region=blue_score,
            red_score_region=red_score,
        )
        
        statuses = manager.get_all_table_statuses()
        assert len(statuses) == 2
        assert 1 in statuses
        assert 2 in statuses
