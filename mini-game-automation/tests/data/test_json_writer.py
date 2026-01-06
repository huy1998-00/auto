"""
Unit tests for JSONWriter (Epic 2).

Tests thread-safe JSON file writing with portalocker.
"""

import pytest
import json
import threading
import time
from pathlib import Path
from src.automation.data.json_writer import JSONWriter


class TestJSONWriter:
    """Test JSONWriter class."""

    def test_initialization(self):
        """Test JSONWriter initialization."""
        writer = JSONWriter()
        assert writer.timeout == 5.0

    def test_initialization_custom_timeout(self):
        """Test initialization with custom timeout."""
        writer = JSONWriter(timeout=10.0)
        assert writer.timeout == 10.0

    def test_write_json_file(self, temp_session_dir):
        """Test writing JSON file."""
        writer = JSONWriter()
        filepath = temp_session_dir / "test.json"
        
        data = {"key": "value", "number": 42}
        result = writer.write(filepath, data)
        
        assert result is True
        assert filepath.exists()
        
        with open(filepath) as f:
            loaded = json.load(f)
        
        assert loaded == data

    def test_write_creates_directory(self, temp_session_dir):
        """Test write creates parent directory."""
        writer = JSONWriter()
        filepath = temp_session_dir / "subdir" / "test.json"
        
        data = {"test": True}
        result = writer.write(filepath, data)
        
        assert result is True
        assert filepath.exists()
        assert filepath.parent.exists()

    def test_read_json_file(self, temp_session_dir):
        """Test reading JSON file."""
        writer = JSONWriter()
        filepath = temp_session_dir / "test.json"
        
        # Write first
        data = {"key": "value"}
        writer.write(filepath, data)
        
        # Read
        loaded = writer.read(filepath)
        assert loaded == data

    def test_read_nonexistent_file(self, temp_session_dir):
        """Test reading nonexistent file returns None."""
        writer = JSONWriter()
        filepath = temp_session_dir / "nonexistent.json"
        
        result = writer.read(filepath)
        assert result is None

    def test_update_json_file(self, temp_session_dir):
        """Test updating JSON file."""
        writer = JSONWriter()
        filepath = temp_session_dir / "test.json"
        
        # Write initial data
        writer.write(filepath, {"count": 0})
        
        # Update
        def increment_count(data):
            data["count"] += 1
            return data
        
        result = writer.update(filepath, increment_count)
        assert result is True
        
        # Verify update
        loaded = writer.read(filepath)
        assert loaded["count"] == 1

    def test_append_round(self, temp_session_dir):
        """Test appending round data."""
        writer = JSONWriter()
        filepath = temp_session_dir / "table_1.json"
        
        # Create initial table file
        initial_data = {
            "table_id": 1,
            "rounds": [],
            "statistics": {"total_rounds": 0, "correct_decisions": 0, "accuracy": 0.0},
        }
        writer.write(filepath, initial_data)
        
        # Append round
        round_data = {
            "round_number": 1,
            "winner": "P",
            "result": "correct",
        }
        result = writer.append_round(filepath, round_data, table_id=1)
        assert result is True
        
        # Verify
        loaded = writer.read(filepath)
        assert len(loaded["rounds"]) == 1
        assert loaded["rounds"][0] == round_data
        assert loaded["statistics"]["total_rounds"] == 1
        assert loaded["statistics"]["correct_decisions"] == 1

    def test_append_round_updates_statistics(self, temp_session_dir):
        """Test append_round updates statistics correctly."""
        writer = JSONWriter()
        filepath = temp_session_dir / "table_1.json"
        
        initial_data = {
            "table_id": 1,
            "rounds": [],
            "statistics": {"total_rounds": 0, "correct_decisions": 0, "accuracy": 0.0},
        }
        writer.write(filepath, initial_data)
        
        # Append correct round
        writer.append_round(filepath, {"result": "correct", "decision_made": "blue"}, table_id=1)
        
        # Append incorrect round
        writer.append_round(filepath, {"result": "incorrect", "decision_made": "red"}, table_id=1)
        
        # Verify statistics
        loaded = writer.read(filepath)
        assert loaded["statistics"]["total_rounds"] == 2
        assert loaded["statistics"]["correct_decisions"] == 1
        assert loaded["statistics"]["accuracy"] == 50.0

    def test_update_patterns(self, temp_session_dir):
        """Test updating patterns."""
        writer = JSONWriter()
        filepath = temp_session_dir / "table_1.json"
        
        initial_data = {"table_id": 1, "patterns": ""}
        writer.write(filepath, initial_data)
        
        result = writer.update_patterns(filepath, "BBP-P;BPB-B", table_id=1)
        assert result is True
        
        loaded = writer.read(filepath)
        assert loaded["patterns"] == "BBP-P;BPB-B"

    def test_concurrent_writes(self, temp_session_dir):
        """Test concurrent writes are thread-safe."""
        writer = JSONWriter()
        filepath = temp_session_dir / "concurrent.json"
        
        # Write initial data
        writer.write(filepath, {"count": 0})
        
        def increment():
            def update(data):
                data["count"] = data.get("count", 0) + 1
                return data
            writer.update(filepath, update)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=increment)
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Verify final count
        loaded = writer.read(filepath)
        assert loaded["count"] == 10  # All increments should be applied
