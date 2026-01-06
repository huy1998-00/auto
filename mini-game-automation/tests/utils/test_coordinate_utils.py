"""
Unit tests for CoordinateUtils (Epic 1).

Tests coordinate calculations and canvas offset handling.
"""

import pytest
from src.automation.utils.coordinate_utils import (
    CoordinateUtils,
    Point,
    Region,
    create_button_coordinates,
    CANVAS_TRANSFORM_OFFSET_X,
)


class TestPoint:
    """Test Point dataclass."""

    def test_point_creation(self):
        """Test creating a point."""
        point = Point(x=100, y=200)
        assert point.x == 100
        assert point.y == 200


class TestRegion:
    """Test Region dataclass."""

    def test_region_creation(self):
        """Test creating a region."""
        region = Region(x=100, y=200, width=300, height=250)
        assert region.x == 100
        assert region.y == 200
        assert region.width == 300
        assert region.height == 250

    def test_region_right(self):
        """Test right edge calculation."""
        region = Region(x=100, y=200, width=300, height=250)
        assert region.right == 400

    def test_region_bottom(self):
        """Test bottom edge calculation."""
        region = Region(x=100, y=200, width=300, height=250)
        assert region.bottom == 450

    def test_region_center(self):
        """Test center point calculation."""
        region = Region(x=100, y=200, width=300, height=250)
        center = region.center
        assert center.x == 250  # 100 + 300/2
        assert center.y == 325  # 200 + 250/2

    def test_region_contains(self):
        """Test point containment check."""
        region = Region(x=100, y=200, width=300, height=250)
        
        # Point inside
        assert region.contains(Point(200, 300)) is True
        
        # Point outside
        assert region.contains(Point(50, 100)) is False
        assert region.contains(Point(500, 300)) is False
        
        # Point on edge (should be inside)
        assert region.contains(Point(100, 200)) is True
        assert region.contains(Point(399, 449)) is True

    def test_region_to_dict(self):
        """Test region to dictionary conversion."""
        region = Region(x=100, y=200, width=300, height=250)
        data = region.to_dict()
        assert data == {"x": 100, "y": 200, "width": 300, "height": 250}

    def test_region_from_dict(self):
        """Test creating region from dictionary."""
        data = {"x": 100, "y": 200, "width": 300, "height": 250}
        region = Region.from_dict(data)
        assert region.x == 100
        assert region.y == 200
        assert region.width == 300
        assert region.height == 250


class TestCoordinateUtils:
    """Test CoordinateUtils class."""

    def test_calculate_absolute_coordinates(self):
        """Test absolute coordinate calculation."""
        utils = CoordinateUtils()
        
        canvas_box = {"x": 0, "y": 0, "width": 1920, "height": 1080}
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_x = 50
        button_y = 30
        
        abs_x, abs_y = utils.calculate_absolute_coordinates(
            canvas_box, table_region, button_x, button_y
        )
        
        # Expected: 0 + 100 + 50 + 17 = 167
        assert abs_x == 167
        # Expected: 0 + 200 + 30 + 0 = 230
        assert abs_y == 230

    def test_canvas_offset_applied(self):
        """Test that canvas offset (17px) is applied."""
        utils = CoordinateUtils()
        
        canvas_box = {"x": 0, "y": 0, "width": 1920, "height": 1080}
        table_region = {"x": 0, "y": 0, "width": 300, "height": 250}
        button_x = 0
        button_y = 0
        
        abs_x, abs_y = utils.calculate_absolute_coordinates(
            canvas_box, table_region, button_x, button_y
        )
        
        assert abs_x == CANVAS_TRANSFORM_OFFSET_X  # 17
        assert abs_y == 0

    def test_get_click_coordinates(self):
        """Test getting click coordinates from button coords dict."""
        utils = CoordinateUtils()
        
        canvas_box = {"x": 10, "y": 20, "width": 1920, "height": 1080}
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        button_coords = {"x": 50, "y": 30}
        
        abs_x, abs_y = utils.get_click_coordinates(
            canvas_box, table_region, button_coords
        )
        
        assert abs_x == 177  # 10 + 100 + 50 + 17
        assert abs_y == 250  # 20 + 200 + 30

    def test_get_region_screenshot_coords(self):
        """Test getting screenshot coordinates for region."""
        utils = CoordinateUtils()
        
        canvas_box = {"x": 10, "y": 20, "width": 1920, "height": 1080}
        table_region = {"x": 100, "y": 200, "width": 300, "height": 250}
        
        coords = utils.get_region_screenshot_coords(canvas_box, table_region)
        
        assert coords["x"] == 110  # 10 + 100
        assert coords["y"] == 220  # 20 + 200
        assert coords["width"] == 300
        assert coords["height"] == 250

    def test_get_subregion_coords(self):
        """Test getting subregion coordinates."""
        utils = CoordinateUtils()
        
        subregion = {"x": 50, "y": 30, "width": 100, "height": 80}
        
        coords = utils.get_subregion_coords(300, 250, subregion)
        
        assert coords["left"] == 50
        assert coords["upper"] == 30
        assert coords["right"] == 150  # 50 + 100
        assert coords["lower"] == 110  # 30 + 80

    def test_get_subregion_coords_raises_on_invalid(self):
        """Test subregion validation raises ValueError."""
        utils = CoordinateUtils()
        
        # Subregion exceeds width
        with pytest.raises(ValueError):
            utils.get_subregion_coords(
                300, 250, {"x": 250, "y": 0, "width": 100, "height": 50}
            )
        
        # Subregion exceeds height
        with pytest.raises(ValueError):
            utils.get_subregion_coords(
                300, 250, {"x": 0, "y": 200, "width": 100, "height": 100}
            )

    def test_validate_canvas_position_no_drift(self):
        """Test canvas position validation with no drift."""
        utils = CoordinateUtils()
        
        original_box = {"x": 0, "y": 0, "width": 1920, "height": 1080}
        current_box = {"x": 0, "y": 0, "width": 1920, "height": 1080}
        
        is_valid, error = utils.validate_canvas_position(original_box, current_box)
        assert is_valid is True
        assert error is None

    def test_validate_canvas_position_with_drift(self):
        """Test canvas position validation detects drift."""
        utils = CoordinateUtils()
        
        original_box = {"x": 0, "y": 0, "width": 1920, "height": 1080}
        current_box = {"x": 10, "y": 0, "width": 1920, "height": 1080}  # 10px X drift
        
        is_valid, error = utils.validate_canvas_position(
            original_box, current_box, drift_threshold=5
        )
        assert is_valid is False
        assert error is not None
        assert "drifted" in error.lower()

    def test_custom_offset(self):
        """Test using custom offset values."""
        utils = CoordinateUtils(offset_x=20, offset_y=5)
        
        canvas_box = {"x": 0, "y": 0, "width": 1920, "height": 1080}
        table_region = {"x": 0, "y": 0, "width": 300, "height": 250}
        
        abs_x, abs_y = utils.calculate_absolute_coordinates(
            canvas_box, table_region, 0, 0
        )
        
        assert abs_x == 20  # Custom offset_x
        assert abs_y == 5   # Custom offset_y


class TestCreateButtonCoordinates:
    """Test create_button_coordinates helper function."""

    def test_create_button_coordinates(self):
        """Test creating button coordinates dictionary."""
        coords = create_button_coordinates(
            blue_x=10, blue_y=20,
            red_x=30, red_y=40,
            confirm_x=50, confirm_y=60,
            cancel_x=70, cancel_y=80,
        )
        
        assert coords["blue"] == {"x": 10, "y": 20}
        assert coords["red"] == {"x": 30, "y": 40}
        assert coords["confirm"] == {"x": 50, "y": 60}
        assert coords["cancel"] == {"x": 70, "y": 80}
