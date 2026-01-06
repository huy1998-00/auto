"""
Unit tests for SessionManager (Epic 2).

Tests date-based session folder management.
"""

import pytest
import json
from pathlib import Path
from src.automation.data.session_manager import SessionManager


class TestSessionManager:
    """Test SessionManager class."""

    def test_initialization(self):
        """Test session manager initialization."""
        manager = SessionManager()
        assert manager.base_path == Path("data/sessions")
        assert manager.max_tables == 6

    def test_initialization_custom_path(self):
        """Test initialization with custom path."""
        manager = SessionManager(base_path="custom/path")
        assert manager.base_path == Path("custom/path")

    def test_create_session(self, temp_session_dir):
        """Test creating a new session."""
        manager = SessionManager(base_path=str(temp_session_dir))
        
        session_path = manager.create_session()
        
        assert session_path.exists()
        assert session_path.is_dir()
        assert manager.session_path == session_path
        assert manager.session_start is not None

    def test_session_config_created(self, temp_session_dir):
        """Test session config file is created."""
        manager = SessionManager(base_path=str(temp_session_dir))
        session_path = manager.create_session()
        
        config_path = session_path / "session_config.json"
        assert config_path.exists()
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "session_start" in config
        assert "tables_active" in config
        assert config["max_tables"] == 6

    def test_get_table_file_path(self, temp_session_dir):
        """Test getting table file path."""
        manager = SessionManager(base_path=str(temp_session_dir))
        manager.create_session()
        
        table_path = manager.get_table_file_path(1)
        assert table_path is not None
        assert table_path.name == "table_1.json"

    def test_get_table_file_path_no_session(self):
        """Test getting table file path without session."""
        manager = SessionManager()
        table_path = manager.get_table_file_path(1)
        assert table_path is None

    def test_register_table(self, temp_session_dir):
        """Test registering a table."""
        manager = SessionManager(base_path=str(temp_session_dir))
        manager.create_session()
        
        table_path = manager.register_table(1)
        
        assert table_path.exists()
        assert table_path.name == "table_1.json"
        
        # Check table file content
        with open(table_path) as f:
            data = json.load(f)
        
        assert data["table_id"] == 1
        assert "rounds" in data
        assert "statistics" in data

    def test_register_table_no_session(self):
        """Test registering table without session raises error."""
        manager = SessionManager()
        
        with pytest.raises(RuntimeError):
            manager.register_table(1)

    def test_register_multiple_tables(self, temp_session_dir):
        """Test registering multiple tables."""
        manager = SessionManager(base_path=str(temp_session_dir))
        manager.create_session()
        
        manager.register_table(1)
        manager.register_table(2)
        manager.register_table(3)
        
        assert len(manager._active_tables) == 3
        assert 1 in manager._active_tables
        assert 2 in manager._active_tables
        assert 3 in manager._active_tables

    def test_unregister_table(self, temp_session_dir):
        """Test unregistering a table."""
        manager = SessionManager(base_path=str(temp_session_dir))
        manager.create_session()
        
        manager.register_table(1)
        assert 1 in manager._active_tables
        
        manager.unregister_table(1)
        assert 1 not in manager._active_tables

    def test_end_session(self, temp_session_dir):
        """Test ending a session."""
        manager = SessionManager(base_path=str(temp_session_dir))
        session_path = manager.create_session()
        
        manager.end_session()
        
        # Check session config updated
        config_path = session_path / "session_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        assert config["session_end"] is not None
        assert manager.session_path is None

    def test_list_sessions(self, temp_session_dir):
        """Test listing sessions."""
        manager = SessionManager(base_path=str(temp_session_dir))
        
        # Create multiple sessions
        manager.create_session()
        manager.end_session()
        manager.create_session()
        
        sessions = manager.list_sessions()
        assert len(sessions) >= 2

    def test_get_session_info(self, temp_session_dir):
        """Test getting session info."""
        manager = SessionManager(base_path=str(temp_session_dir))
        manager.create_session()
        manager.register_table(1)
        
        info = manager.get_session_info()
        
        assert info is not None
        assert "path" in info
        assert "session_start" in info
        assert "active_tables" in info
        assert 1 in info["active_tables"]

    def test_get_session_info_no_session(self):
        """Test getting session info without active session."""
        manager = SessionManager()
        info = manager.get_session_info()
        assert info is None
