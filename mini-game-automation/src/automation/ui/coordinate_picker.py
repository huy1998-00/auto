"""
Visual coordinate picker for table regions and buttons.

Provides drag-to-select and click-to-capture functionality
without requiring DevTools knowledge.
"""

import asyncio
from typing import Optional, Dict, Any, Callable
from playwright.async_api import Page

from ..utils.logger import get_logger

logger = get_logger("ui.coordinate_picker")


class CoordinatePicker:
    """
    Visual coordinate picker that overlays on browser page.
    
    Allows users to:
    - Drag to select table regions
    - Click to capture button positions
    - See visual feedback with highlighted regions
    """

    PICKER_SCRIPT = """
    (function() {
        // Remove existing picker if present
        if (window.__coordinatePicker) {
            window.__coordinatePicker.destroy();
        }

        const picker = {
            mode: 'table', // 'table', 'button', 'timer', 'score'
            isActive: false,
            startX: 0,
            startY: 0,
            currentRect: null,
            overlay: null,
            result: null,
            resolveFunc: null,

            init() {
                // Ensure document.body exists
                if (!document.body) {
                    console.error('Document body not found - cannot initialize picker');
                    throw new Error('Document body not found');
                }
                
                console.log('Initializing coordinate picker...');
                console.log('Document ready state:', document.readyState);
                console.log('Body exists:', !!document.body);
                
                // Create overlay div - Make it VERY visible with green tint
                this.overlay = document.createElement('div');
                this.overlay.id = '__coordinatePickerOverlay';
                this.overlay.style.cssText = `
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    z-index: 999999 !important;
                    pointer-events: auto !important;
                    cursor: crosshair !important;
                    background: rgba(0, 255, 0, 0.15) !important;
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                `;
                document.body.appendChild(this.overlay);
                
                // Force overlay to be visible and verify
                this.overlay.style.display = 'block';
                this.overlay.style.visibility = 'visible';
                this.overlay.style.opacity = '1';
                
                // Verify it's actually in the DOM
                const overlayCheck = document.getElementById('__coordinatePickerOverlay');
                if (!overlayCheck) {
                    console.error('FAILED: Overlay not found in DOM after creation');
                    throw new Error('Failed to create overlay');
                }
                console.log('✓ Coordinate picker overlay created and verified');

                // Create instruction panel
                const panel = document.createElement('div');
                panel.id = '__coordinatePickerPanel';
                panel.style.cssText = `
                    position: fixed;
                    top: 20px;
                    left: 20px;
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    z-index: 1000000;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    max-width: 300px;
                `;
                this.updateInstructions(panel);
                document.body.appendChild(panel);

                // Create selection rectangle - Make it BRIGHT GREEN and visible
                this.currentRect = document.createElement('div');
                this.currentRect.id = '__coordinatePickerRect';
                this.currentRect.style.cssText = `
                    position: fixed !important;
                    border: 3px solid #00ff00 !important;
                    background: rgba(0, 255, 0, 0.2) !important;
                    pointer-events: none !important;
                    z-index: 1000000 !important;
                    display: none !important;
                    box-shadow: 0 0 10px rgba(0, 255, 0, 0.5) !important;
                `;
                document.body.appendChild(this.currentRect);
                console.log('✓ Selection rectangle created');

                // Event listeners
                this.overlay.addEventListener('mousedown', (e) => this.onMouseDown(e));
                this.overlay.addEventListener('mousemove', (e) => this.onMouseMove(e));
                this.overlay.addEventListener('mouseup', (e) => this.onMouseUp(e));
                this.overlay.addEventListener('click', (e) => this.onClick(e));

                // ESC to cancel
                const escHandler = (e) => {
                    if (e.key === 'Escape') {
                        this.cancel();
                    }
                };
                document.addEventListener('keydown', escHandler);
                this.escHandler = escHandler;
            },

            updateInstructions(panel) {
                const modeText = {
                    'table': 'Drag to select TABLE region',
                    'button': 'Click on BUTTON position',
                    'timer': 'Drag to select TIMER region',
                    'score': 'Drag to select SCORE region'
                };
                panel.innerHTML = `
                    <div style="font-weight: bold; margin-bottom: 10px; color: #333;">
                        📍 Coordinate Picker
                    </div>
                    <div style="margin-bottom: 10px; color: #666;">
                        ${modeText[this.mode] || 'Select region'}
                    </div>
                    <div style="font-size: 12px; color: #999; margin-bottom: 10px;">
                        Mode: <strong>${this.mode.toUpperCase()}</strong>
                    </div>
                    <div style="font-size: 11px; color: #999;">
                        ${this.mode === 'button' ? '• Click to capture point' : '• Drag to select area'}<br>
                        • ESC to cancel
                    </div>
                `;
            },

            getCanvasOffset() {
                // Try to find canvas element, but if not found, use page origin (0,0)
                const canvas = document.querySelector('#layaCanvas');
                if (!canvas) {
                    // No canvas - coordinates will be relative to page
                    return { x: 0, y: 0 };
                }
                const rect = canvas.getBoundingClientRect();
                return { x: rect.x, y: rect.y };
            },

            onMouseDown(e) {
                if (this.mode === 'button') return; // Button mode uses click, not drag
                
                console.log('Mouse down - starting drag');
                this.isActive = true;
                const canvasOffset = this.getCanvasOffset();
                this.startX = e.clientX - canvasOffset.x;
                this.startY = e.clientY - canvasOffset.y;
                
                // Make rectangle visible and bright green
                this.currentRect.style.display = 'block';
                this.currentRect.style.visibility = 'visible';
                this.currentRect.style.opacity = '1';
                this.currentRect.style.border = '3px solid #00ff00';
                this.currentRect.style.background = 'rgba(0, 255, 0, 0.2)';
                this.currentRect.style.left = e.clientX + 'px';
                this.currentRect.style.top = e.clientY + 'px';
                this.currentRect.style.width = '0px';
                this.currentRect.style.height = '0px';
                console.log('Green rectangle should now be visible');
            },

            onMouseMove(e) {
                if (!this.isActive || this.mode === 'button') return;

                const canvasOffset = this.getCanvasOffset();
                const currentX = e.clientX - canvasOffset.x;
                const currentY = e.clientY - canvasOffset.y;

                const left = Math.min(this.startX, currentX);
                const top = Math.min(this.startY, currentY);
                const width = Math.abs(currentX - this.startX);
                const height = Math.abs(currentY - this.startY);

                // Update visual rectangle (screen coordinates)
                const screenX = e.clientX;
                const screenY = e.clientY;
                const screenLeft = Math.min(screenX, this.startX + canvasOffset.x);
                const screenTop = Math.min(screenY, this.startY + canvasOffset.y);
                const screenWidth = Math.abs(screenX - (this.startX + canvasOffset.x));
                const screenHeight = Math.abs(screenY - (this.startY + canvasOffset.y));

                this.currentRect.style.left = screenLeft + 'px';
                this.currentRect.style.top = screenTop + 'px';
                this.currentRect.style.width = screenWidth + 'px';
                this.currentRect.style.height = screenHeight + 'px';
            },

            onMouseUp(e) {
                if (!this.isActive || this.mode === 'button') return;

                const canvasOffset = this.getCanvasOffset();
                const endX = e.clientX - canvasOffset.x;
                const endY = e.clientY - canvasOffset.y;

                const x = Math.min(this.startX, endX);
                const y = Math.min(this.startY, endY);
                const width = Math.abs(endX - this.startX);
                const height = Math.abs(endY - this.startY);

                if (width > 10 && height > 10) { // Minimum size
                    this.captureRegion(x, y, width, height);
                }

                this.isActive = false;
                this.currentRect.style.display = 'none';
            },

            onClick(e) {
                if (this.mode !== 'button') return;

                const canvasOffset = this.getCanvasOffset();
                const x = e.clientX - canvasOffset.x;
                const y = e.clientY - canvasOffset.y;

                // Show visual marker
                const marker = document.createElement('div');
                marker.style.cssText = `
                    position: fixed;
                    left: ${e.clientX - 5}px;
                    top: ${e.clientY - 5}px;
                    width: 10px;
                    height: 10px;
                    background: red;
                    border: 2px solid white;
                    border-radius: 50%;
                    z-index: 999999;
                    pointer-events: none;
                `;
                document.body.appendChild(marker);
                setTimeout(() => marker.remove(), 1000);

                this.capturePoint(x, y);
            },

            captureRegion(x, y, width, height) {
                this.result = { x, y, width, height };
                this.destroy();
            },

            capturePoint(x, y) {
                this.result = { x, y };
                this.destroy();
            },

            setMode(mode) {
                this.mode = mode;
                const panel = document.getElementById('__coordinatePickerPanel');
                if (panel) {
                    this.updateInstructions(panel);
                }
            },

            cancel() {
                this.result = null;
                this.destroy();
            },

            destroy() {
                if (this.overlay) {
                    this.overlay.remove();
                    this.overlay = null;
                }
                const panel = document.getElementById('__coordinatePickerPanel');
                if (panel) {
                    panel.remove();
                }
                if (this.currentRect) {
                    this.currentRect.remove();
                    this.currentRect = null;
                }
                if (this.escHandler) {
                    document.removeEventListener('keydown', this.escHandler);
                    this.escHandler = null;
                }
                this.isActive = false;
            },

            waitForResult() {
                return new Promise((resolve) => {
                    const checkInterval = setInterval(() => {
                        if (this.result !== undefined) {
                            clearInterval(checkInterval);
                            const result = this.result;
                            this.result = undefined; // Reset for next use
                            resolve(result);
                        }
                    }, 100);
                });
            }
        };

        window.__coordinatePicker = picker;
        try {
            picker.init();
            return 'Picker initialized successfully';
        } catch (error) {
            console.error('Failed to initialize picker:', error);
            return 'Picker initialization failed: ' + error.message;
        }
    })();
    """

    def __init__(self, page: Page):
        """
        Initialize coordinate picker.

        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.is_active = False

    async def pick_table_region(self) -> Optional[Dict[str, int]]:
        """
        Pick table region (drag to select).

        Returns:
            Dictionary with x, y, width, height or None if cancelled
        """
        return await self._pick('table')

    async def pick_button_position(self) -> Optional[Dict[str, int]]:
        """
        Pick button position (click to capture).

        Returns:
            Dictionary with x, y or None if cancelled
        """
        return await self._pick('button')

    async def pick_timer_region(self) -> Optional[Dict[str, int]]:
        """Pick timer region (drag to select)."""
        return await self._pick('timer')

    async def pick_score_region(self) -> Optional[Dict[str, int]]:
        """Pick score region (drag to select)."""
        return await self._pick('score')

    async def _pick(self, mode: str) -> Optional[Dict[str, Any]]:
        """
        Start picking coordinates in specified mode.

        Args:
            mode: 'table', 'button', 'timer', or 'score'

        Returns:
            Captured coordinates dictionary or None if cancelled
        """
        if self.is_active:
            await self.stop_picking()

        self.is_active = True

        try:
            # Ensure page is loaded
            await self.page.wait_for_load_state("domcontentloaded", timeout=5000)
            
            # Check if document.body exists
            body_exists = await self.page.evaluate("document.body !== null")
            if not body_exists:
                logger.error("Page body not found - cannot inject picker")
                raise Exception("Page body not found. Please ensure the page is fully loaded.")

            # Inject picker script
            init_result = await self.page.evaluate(self.PICKER_SCRIPT)
            logger.info(f"Picker script injected: {init_result}")

            # Verify picker was created
            picker_exists = await self.page.evaluate("window.__coordinatePicker !== undefined")
            if not picker_exists:
                logger.error("Picker was not created after injection")
                raise Exception("Failed to initialize coordinate picker. Please refresh the page and try again.")
            
            # Verify overlay is visible
            overlay_visible = await self.page.evaluate("""
                () => {
                    const overlay = document.getElementById('__coordinatePickerOverlay');
                    if (!overlay) return false;
                    const style = window.getComputedStyle(overlay);
                    return overlay.offsetParent !== null && 
                           style.display !== 'none' && 
                           style.visibility !== 'hidden' &&
                           style.opacity !== '0';
                }
            """)
            
            if not overlay_visible:
                logger.error("Overlay is not visible after creation")
                # Try to force it visible
                await self.page.evaluate("""
                    () => {
                        const overlay = document.getElementById('__coordinatePickerOverlay');
                        if (overlay) {
                            overlay.style.display = 'block';
                            overlay.style.visibility = 'visible';
                            overlay.style.opacity = '1';
                            overlay.style.zIndex = '999999';
                        }
                    }
                """)
                logger.info("Attempted to force overlay visibility")
            
            logger.info(f"Overlay visibility check: {overlay_visible}")

            # Set mode
            await self.page.evaluate(f"window.__coordinatePicker.setMode('{mode}')")
            logger.info(f"Picker mode set to: {mode}")

            # Wait for result (with timeout)
            result = await asyncio.wait_for(
                self.page.evaluate("""async () => {
                    return await window.__coordinatePicker.waitForResult();
                }"""),
                timeout=60.0  # 60 second timeout
            )

            logger.info(f"Picker result: {result}")
            return result

        except asyncio.TimeoutError:
            logger.warning("Coordinate picking timed out")
            await self.stop_picking()
            return None
        except Exception as e:
            logger.error(f"Error during coordinate picking: {e}")
            await self.stop_picking()
            return None
        finally:
            self.is_active = False

    async def stop_picking(self):
        """Stop picking and clean up."""
        if not self.is_active:
            return

        try:
            await self.page.evaluate("""
                if (window.__coordinatePicker) {
                    window.__coordinatePicker.destroy();
                }
            """)
        except Exception as e:
            logger.error(f"Error stopping picker: {e}")

        self.is_active = False
