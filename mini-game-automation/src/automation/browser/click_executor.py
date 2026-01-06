"""
Two-phase click execution with canvas transform offset.

Handles the two-phase clicking process:
1. Choose team (blue/red button)
2. Confirm (✓ tick) or Cancel (✗ tick)

Accounts for 17px canvas transform offset in coordinates.
"""

import asyncio
import random
from typing import Optional, Dict, Tuple
from datetime import datetime

from .browser_manager import BrowserManager
from ..utils.logger import get_logger, TIMESTAMP_FORMAT
from ..utils.coordinate_utils import CoordinateUtils

logger = get_logger("click_executor")


class ClickExecutor:
    """
    Executes two-phase clicks with canvas transform offset.

    Phase 1: Click team button (blue or red)
    Phase 2: Click confirm button (✓ tick)

    Accounts for 17px horizontal canvas transform offset.
    """

    # Click timing settings
    MIN_PHASE_DELAY_MS = 50
    MAX_PHASE_DELAY_MS = 100
    MIN_CLICK_DELAY_MS = 10
    MAX_CLICK_DELAY_MS = 20

    def __init__(
        self,
        browser_manager: BrowserManager,
        coordinate_utils: Optional[CoordinateUtils] = None,
    ):
        """
        Initialize click executor.

        Args:
            browser_manager: Browser manager instance
            coordinate_utils: Coordinate utilities (optional)
        """
        self.browser_manager = browser_manager
        self.coordinate_utils = coordinate_utils or CoordinateUtils()

    async def execute_click(
        self,
        x: int,
        y: int,
        table_id: int,
        description: str = "click",
    ) -> bool:
        """
        Execute a single mouse click at coordinates.

        Args:
            x: Absolute X coordinate
            y: Absolute Y coordinate
            table_id: Table ID for logging
            description: Click description for logging

        Returns:
            True if click successful, False otherwise
        """
        if not self.browser_manager.page:
            logger.error("Browser not initialized", extra={"table_id": table_id})
            return False

        try:
            # Add slight random delay for anti-bot measures (NFR15)
            delay_ms = random.randint(self.MIN_CLICK_DELAY_MS, self.MAX_CLICK_DELAY_MS)
            await asyncio.sleep(delay_ms / 1000)

            await self.browser_manager.page.mouse.click(x, y)

            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            logger.debug(
                f"Executed {description} at ({x}, {y}) at {timestamp}",
                extra={"table_id": table_id},
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to execute {description}: {e}",
                extra={"table_id": table_id},
            )
            return False

    async def click_team_button(
        self,
        table_id: int,
        team: str,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
    ) -> bool:
        """
        Execute Phase 1: Click team button (blue or red).

        Args:
            table_id: Table ID
            team: "blue" or "red"
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary

        Returns:
            True if click successful, False otherwise
        """
        if team not in ["blue", "red"]:
            logger.error(f"Invalid team: {team}", extra={"table_id": table_id})
            return False

        # Get button coordinates
        button = button_coords.get(team)
        if not button:
            logger.error(f"Button coords not found for team: {team}", extra={"table_id": table_id})
            return False

        # Calculate absolute coordinates with canvas transform offset
        abs_x, abs_y = self.coordinate_utils.calculate_absolute_coordinates(
            canvas_box=canvas_box,
            table_region=table_region,
            button_x=button["x"],
            button_y=button["y"],
        )

        return await self.execute_click(
            x=abs_x,
            y=abs_y,
            table_id=table_id,
            description=f"Phase 1: {team} team button",
        )

    async def click_confirm_button(
        self,
        table_id: int,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
    ) -> bool:
        """
        Execute Phase 2: Click confirm button (✓ tick).

        Args:
            table_id: Table ID
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary

        Returns:
            True if click successful, False otherwise
        """
        confirm = button_coords.get("confirm")
        if not confirm:
            logger.error("Confirm button coords not found", extra={"table_id": table_id})
            return False

        abs_x, abs_y = self.coordinate_utils.calculate_absolute_coordinates(
            canvas_box=canvas_box,
            table_region=table_region,
            button_x=confirm["x"],
            button_y=confirm["y"],
        )

        return await self.execute_click(
            x=abs_x,
            y=abs_y,
            table_id=table_id,
            description="Phase 2: confirm button",
        )

    async def click_cancel_button(
        self,
        table_id: int,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
    ) -> bool:
        """
        Execute Phase 2: Click cancel button (✗ tick).

        Args:
            table_id: Table ID
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary

        Returns:
            True if click successful, False otherwise
        """
        cancel = button_coords.get("cancel")
        if not cancel:
            logger.error("Cancel button coords not found", extra={"table_id": table_id})
            return False

        abs_x, abs_y = self.coordinate_utils.calculate_absolute_coordinates(
            canvas_box=canvas_box,
            table_region=table_region,
            button_x=cancel["x"],
            button_y=cancel["y"],
        )

        return await self.execute_click(
            x=abs_x,
            y=abs_y,
            table_id=table_id,
            description="Phase 2: cancel button",
        )

    async def execute_two_phase_click(
        self,
        table_id: int,
        team: str,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
        confirm: bool = True,
    ) -> bool:
        """
        Execute full two-phase click sequence.

        Phase 1: Click team button (blue or red)
        Wait: 50-100ms for confirmation UI to appear
        Phase 2: Click confirm or cancel button

        Args:
            table_id: Table ID
            team: "blue" or "red"
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary
            confirm: Whether to confirm (True) or cancel (False)

        Returns:
            True if both phases successful, False otherwise
        """
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        logger.info(
            f"Starting two-phase click for team '{team}'",
            extra={"table_id": table_id},
        )

        # Phase 1: Click team button
        phase1_success = await self.click_team_button(
            table_id=table_id,
            team=team,
            canvas_box=canvas_box,
            table_region=table_region,
            button_coords=button_coords,
        )

        if not phase1_success:
            logger.error(
                f"Phase 1 failed for team '{team}'",
                extra={"table_id": table_id},
            )
            return False

        # Wait for confirmation UI to appear (50-100ms)
        phase_delay_ms = random.randint(self.MIN_PHASE_DELAY_MS, self.MAX_PHASE_DELAY_MS)
        await asyncio.sleep(phase_delay_ms / 1000)

        # Phase 2: Click confirm or cancel
        if confirm:
            phase2_success = await self.click_confirm_button(
                table_id=table_id,
                canvas_box=canvas_box,
                table_region=table_region,
                button_coords=button_coords,
            )
        else:
            phase2_success = await self.click_cancel_button(
                table_id=table_id,
                canvas_box=canvas_box,
                table_region=table_region,
                button_coords=button_coords,
            )

        if not phase2_success:
            logger.error(
                f"Phase 2 failed for team '{team}'",
                extra={"table_id": table_id},
            )
            return False

        logger.info(
            f"Two-phase click completed for team '{team}' at {timestamp}",
            extra={"table_id": table_id},
        )

        return True

    async def click_blue(
        self,
        table_id: int,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
    ) -> bool:
        """
        Convenience method to click blue team and confirm.

        Args:
            table_id: Table ID
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary

        Returns:
            True if successful, False otherwise
        """
        return await self.execute_two_phase_click(
            table_id=table_id,
            team="blue",
            canvas_box=canvas_box,
            table_region=table_region,
            button_coords=button_coords,
            confirm=True,
        )

    async def click_red(
        self,
        table_id: int,
        canvas_box: Dict[str, int],
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
    ) -> bool:
        """
        Convenience method to click red team and confirm.

        Args:
            table_id: Table ID
            canvas_box: Canvas element bounding box
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary

        Returns:
            True if successful, False otherwise
        """
        return await self.execute_two_phase_click(
            table_id=table_id,
            team="red",
            canvas_box=canvas_box,
            table_region=table_region,
            button_coords=button_coords,
            confirm=True,
        )
