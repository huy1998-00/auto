"""
Pytest configuration and shared fixtures.

This file contains fixtures used across multiple test modules.
"""

import pytest
from pathlib import Path
from PIL import Image
import tempfile
import shutil


@pytest.fixture
def temp_session_dir():
    """Create a temporary session directory for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_session_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_table_region():
    """Sample table region coordinates for testing."""
    return {
        "x": 100,
        "y": 200,
        "width": 300,
        "height": 250,
    }


@pytest.fixture
def sample_patterns():
    """Sample pattern string for testing."""
    return "BBP-P;BPB-B;BBB-P;PPP-B"


@pytest.fixture
def sample_round_history():
    """Sample round history for testing."""
    return ["B", "B", "P"]


@pytest.fixture
def mock_screenshot():
    """Create a mock screenshot image for testing."""
    # Create a simple test image (100x100 RGB)
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    return img


@pytest.fixture
def sample_table_state():
    """Sample table state for testing."""
    return {
        "table_id": 1,
        "status": "active",
        "learning_phase": False,
        "rounds_watched": 5,
        "round_history": ["B", "B", "P"],
        "current_timer": 12,
        "blue_score": 3,
        "red_score": 2,
        "previous_blue_score": 3,
        "previous_red_score": 1,
        "patterns": "BBP-P;BPB-B",
    }


@pytest.fixture
def sample_round_data():
    """Sample round data for testing JSON persistence."""
    return {
        "round_number": 1,
        "timestamp": "2026-01-06_14-30-00",
        "timer_start": 15,
        "blue_score": 1,
        "red_score": 0,
        "winner": "P",
        "decision_made": "blue",
        "pattern_matched": "BBP-P",
        "result": "correct",
    }


@pytest.fixture
def mock_canvas_box():
    """Mock canvas bounding box for coordinate testing."""
    return {
        "x": 0,
        "y": 0,
        "width": 1920,
        "height": 1080,
    }


@pytest.fixture
def sample_button_coords():
    """Sample button coordinates for testing."""
    return {
        "blue": {"x": 10, "y": 20},
        "red": {"x": 30, "y": 40},
        "confirm": {"x": 50, "y": 60},
        "cancel": {"x": 70, "y": 80},
    }
