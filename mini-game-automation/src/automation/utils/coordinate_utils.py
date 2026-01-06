"""
Coordinate utilities for canvas offset calculations.

Handles the 17px canvas transform offset and coordinate conversions
for accurate click execution.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass


# Canvas transform offset from architecture specification
CANVAS_TRANSFORM_OFFSET_X = 17
CANVAS_TRANSFORM_OFFSET_Y = 0


@dataclass
class Point:
    """Represents a 2D point."""

    x: int
    y: int


@dataclass
class Region:
    """Represents a rectangular region."""

    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """Get right edge x coordinate."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Get bottom edge y coordinate."""
        return self.y + self.height

    @property
    def center(self) -> Point:
        """Get center point of region."""
        return Point(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2,
        )

    def contains(self, point: Point) -> bool:
        """Check if point is inside region."""
        return (
            self.x <= point.x < self.right
            and self.y <= point.y < self.bottom
        )

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Region":
        """Create Region from dictionary."""
        return cls(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
        )


class CoordinateUtils:
    """
    Utility class for coordinate calculations.

    Handles canvas offset application and coordinate transformations
    for accurate click positioning.
    """

    def __init__(
        self,
        offset_x: int = CANVAS_TRANSFORM_OFFSET_X,
        offset_y: int = CANVAS_TRANSFORM_OFFSET_Y,
    ):
        """
        Initialize coordinate utilities.

        Args:
            offset_x: Canvas transform X offset (default: 17px)
            offset_y: Canvas transform Y offset (default: 0px)
        """
        self.offset_x = offset_x
        self.offset_y = offset_y

    def calculate_absolute_coordinates(
        self,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_x: int,
        button_y: int,
    ) -> Tuple[int, int]:
        """
        Calculate absolute page coordinates for a button click.

        Formula from architecture:
        - absolute_x = canvas_box['x'] + table_region['x'] + button_x + 17
        - absolute_y = canvas_box['y'] + table_region['y'] + button_y

        Args:
            canvas_box: Canvas element bounding box {'x', 'y', 'width', 'height'}
            table_region: Table region coordinates {'x', 'y', 'width', 'height'}
            button_x: Button X coordinate relative to table region
            button_y: Button Y coordinate relative to table region

        Returns:
            Tuple of (absolute_x, absolute_y) for mouse click
        """
        absolute_x = (
            canvas_box["x"]
            + table_region["x"]
            + button_x
            + self.offset_x
        )
        absolute_y = (
            canvas_box["y"]
            + table_region["y"]
            + button_y
            + self.offset_y
        )

        return absolute_x, absolute_y

    def get_click_coordinates(
        self,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, int],
    ) -> Tuple[int, int]:
        """
        Get click coordinates for a button.

        Args:
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates {'x', 'y'} relative to table

        Returns:
            Tuple of (absolute_x, absolute_y) for mouse click
        """
        return self.calculate_absolute_coordinates(
            canvas_box=canvas_box,
            table_region=table_region,
            button_x=button_coords["x"],
            button_y=button_coords["y"],
        )

    def get_region_screenshot_coords(
        self,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
    ) -> Dict[str, int]:
        """
        Get coordinates for region screenshot capture.

        Args:
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates

        Returns:
            Dictionary with screenshot region coordinates
        """
        return {
            "x": canvas_box["x"] + table_region["x"],
            "y": canvas_box["y"] + table_region["y"],
            "width": table_region["width"],
            "height": table_region["height"],
        }

    def get_subregion_coords(
        self,
        table_region_image_width: int,
        table_region_image_height: int,
        subregion: Dict[str, int],
    ) -> Dict[str, int]:
        """
        Get coordinates for a subregion within a table region image.

        Used for cropping timer/score regions from table screenshot.

        Args:
            table_region_image_width: Width of table region screenshot
            table_region_image_height: Height of table region screenshot
            subregion: Subregion coordinates within table {'x', 'y', 'width', 'height'}

        Returns:
            Crop box coordinates for PIL Image.crop()
        """
        # Validate subregion is within bounds
        if subregion["x"] + subregion["width"] > table_region_image_width:
            raise ValueError(
                f"Subregion exceeds image width: "
                f"{subregion['x']} + {subregion['width']} > {table_region_image_width}"
            )
        if subregion["y"] + subregion["height"] > table_region_image_height:
            raise ValueError(
                f"Subregion exceeds image height: "
                f"{subregion['y']} + {subregion['height']} > {table_region_image_height}"
            )

        return {
            "left": subregion["x"],
            "upper": subregion["y"],
            "right": subregion["x"] + subregion["width"],
            "lower": subregion["y"] + subregion["height"],
        }

    def validate_canvas_position(
        self,
        original_box: Dict[str, int],
        current_box: Dict[str, int],
        drift_threshold: int = 5,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that canvas position hasn't drifted.

        Should be called every 10-20 rounds per architecture.

        Args:
            original_box: Original canvas bounding box
            current_box: Current canvas bounding box
            drift_threshold: Maximum allowed drift in pixels

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        x_drift = abs(original_box["x"] - current_box["x"])
        y_drift = abs(original_box["y"] - current_box["y"])

        if x_drift > drift_threshold:
            return False, f"Canvas X position drifted by {x_drift}px (threshold: {drift_threshold}px)"

        if y_drift > drift_threshold:
            return False, f"Canvas Y position drifted by {y_drift}px (threshold: {drift_threshold}px)"

        return True, None


def create_button_coordinates(
    blue_x: int,
    blue_y: int,
    red_x: int,
    red_y: int,
    confirm_x: int,
    confirm_y: int,
    cancel_x: int,
    cancel_y: int,
) -> Dict[str, Dict[str, int]]:
    """
    Create button coordinates dictionary.

    Args:
        blue_x, blue_y: Blue team button coordinates
        red_x, red_y: Red team button coordinates
        confirm_x, confirm_y: Confirm (✓) button coordinates
        cancel_x, cancel_y: Cancel (✗) button coordinates

    Returns:
        Dictionary of button coordinates
    """
    return {
        "blue": {"x": blue_x, "y": blue_y},
        "red": {"x": red_x, "y": red_y},
        "confirm": {"x": confirm_x, "y": confirm_y},
        "cancel": {"x": cancel_x, "y": cancel_y},
    }
