# Epic 4: Desktop Control Interface - Coordinate Picker Implementation Flow

## Current Scope Implementation - Step by Step

This document traces the complete flow of the coordinate picker feature, showing which files are used and which lines of code are called.

---

## Issue Summary

⚠️ **Coordinate picker overlay not appearing** - Green overlay not visible when picker is activated  
⚠️ **Test coordinate picker not working** - Standalone HTML test file needs debugging

---

## Complete Implementation Flow

### **STEP 1: User Initiates Coordinate Picker**

**File:** `mini-game-automation/src/automation/ui/main_window.py`  
**Method:** `_pick_table_region()`  
**Line:** 1128

**Code Reference:**
```1128:1151:mini-game-automation/src/automation/ui/main_window.py
def _pick_table_region(self):
    """Pick table region using visual picker."""
    if not self.browser_page:
        messagebox.showwarning(...)
        return

    # Show info message
    self.window.after(0, lambda: messagebox.showinfo(
        "Coordinate Picker",
        "Coordinate picker will appear in the browser window.\n\n"
        "Instructions:\n"
        "1. Look at the browser window\n"
        "2. You'll see a green overlay\n"
        "3. Drag to select the table region\n"
        "4. Release mouse to capture coordinates\n\n"
        "Press ESC to cancel."
    ))
```

**What happens:**
- Checks if `self.browser_page` exists (Playwright Page object)
- Shows info dialog to user
- Proceeds to create picker thread

---

### **STEP 2: Thread Creation for Async Operations**

**File:** `mini-game-automation/src/automation/ui/main_window.py`  
**Method:** `_pick_table_region()` → `pick_thread()`  
**Line:** 1153-1188

**Code Reference:**
```1153:1188:mini-game-automation/src/automation/ui/main_window.py
def pick_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Check if page is still valid
        try:
            # Test if page is accessible
            loop.run_until_complete(self.browser_page.evaluate("document.title"))
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror(...))
            return

        picker = CoordinatePicker(self.browser_page)
        result = loop.run_until_complete(picker.pick_table_region())
        
        if result:
            self.window.after(0, lambda: self._apply_table_region(result))
        else:
            self.window.after(0, lambda: messagebox.showinfo("Cancelled", "Coordinate picking cancelled"))
    except Exception as e:
        # Error handling...
    finally:
        loop.close()

threading.Thread(target=pick_thread, daemon=True).start()
```

**What happens:**
- Creates new asyncio event loop (required for Playwright async operations)
- Tests if browser page is accessible
- Creates `CoordinatePicker` instance
- Calls `picker.pick_table_region()` and waits for result
- Applies result to UI form fields

---

### **STEP 3: CoordinatePicker Class Initialization**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Class:** `CoordinatePicker`  
**Method:** `__init__()`  
**Line:** 335-343

**Code Reference:**
```335:343:mini-game-automation/src/automation/ui/coordinate_picker.py
def __init__(self, page: Page):
    """
    Initialize coordinate picker.

    Args:
        page: Playwright Page instance
    """
    self.page = page
    self.is_active = False
```

**What happens:**
- Stores Playwright Page reference
- Initializes `is_active` flag to False

---

### **STEP 4: Pick Table Region Method Called**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Method:** `pick_table_region()`  
**Line:** 345-352

**Code Reference:**
```345:352:mini-game-automation/src/automation/ui/coordinate_picker.py
async def pick_table_region(self) -> Optional[Dict[str, int]]:
    """
    Pick table region (drag to select).

    Returns:
        Dictionary with x, y, width, height or None if cancelled
    """
    return await self._pick('table')
```

**What happens:**
- Calls internal `_pick()` method with mode='table'

---

### **STEP 5: Internal Pick Method - Main Logic**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Method:** `_pick()`  
**Line:** 371-461

**Code Reference:**
```371:461:mini-game-automation/src/automation/ui/coordinate_picker.py
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
```

**What happens:**
1. Checks if picker is already active, stops if needed
2. Sets `is_active = True`
3. Waits for page DOM to load (5 second timeout)
4. Verifies `document.body` exists
5. **Injects PICKER_SCRIPT JavaScript** (line 397)
6. Verifies picker object was created
7. **Checks overlay visibility** (line 407-417) ⚠️ **ISSUE POINT**
8. If not visible, attempts to force visibility (line 422-432)
9. Sets picker mode to 'table'
10. Waits for user interaction (60 second timeout)
11. Returns result or None

---

### **STEP 6: JavaScript Picker Script Injection**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Variable:** `PICKER_SCRIPT`  
**Line:** 27-333

**Code Reference:**
```27:333:mini-game-automation/src/automation/ui/coordinate_picker.py
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
            // ... panel styling and content ...
            document.body.appendChild(panel);

            // Create selection rectangle
            this.currentRect = document.createElement('div');
            this.currentRect.id = '__coordinatePickerRect';
            // ... rectangle styling ...
            document.body.appendChild(this.currentRect);

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
        // ... other methods ...
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
```

**What happens:**
1. Removes existing picker if present
2. Creates picker object with state variables
3. **Calls `init()` method** which:
   - Verifies `document.body` exists
   - **Creates overlay div** with green tint background (line 56-72)
   - **Appends overlay to document.body** (line 72)
   - Forces visibility styles (line 75-77)
   - Verifies overlay exists in DOM (line 80-84)
   - Creates instruction panel
   - Creates selection rectangle
   - Attaches event listeners
   - Sets up ESC key handler
4. Stores picker in `window.__coordinatePicker`
5. Returns success/failure message

---

### **STEP 7: Overlay Visibility Verification**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Method:** `_pick()` → Overlay visibility check  
**Line:** 407-432

**Code Reference:**
```407:432:mini-game-automation/src/automation/ui/coordinate_picker.py
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
```

**What happens:**
- Checks if overlay element exists
- Checks computed styles (display, visibility, opacity)
- Checks if `offsetParent !== null` (indicates element is rendered)
- If not visible, attempts to force visibility
- ⚠️ **ISSUE:** This check may pass but overlay still not visible to user

---

### **STEP 8: Mode Setting**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Method:** `_pick()` → Set mode  
**Line:** 437-439

**Code Reference:**
```437:439:mini-game-automation/src/automation/ui/coordinate_picker.py
# Set mode
await self.page.evaluate(f"window.__coordinatePicker.setMode('{mode}')")
logger.info(f"Picker mode set to: {mode}")
```

**What happens:**
- Calls JavaScript `setMode()` method
- Updates instruction panel text

---

### **STEP 9: Wait for User Interaction**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**Method:** `_pick()` → Wait for result  
**Line:** 441-447

**Code Reference:**
```441:447:mini-game-automation/src/automation/ui/coordinate_picker.py
# Wait for result (with timeout)
result = await asyncio.wait_for(
    self.page.evaluate("""async () => {
        return await window.__coordinatePicker.waitForResult();
    }"""),
    timeout=60.0  # 60 second timeout
)
```

**What happens:**
- Calls JavaScript `waitForResult()` method
- Polls every 100ms for result (see JavaScript code line 310-321)
- Returns when user drags/clicks or cancels
- Times out after 60 seconds

---

### **STEP 10: JavaScript waitForResult Method**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**JavaScript Method:** `waitForResult()`  
**Line:** 310-321

**Code Reference:**
```310:321:mini-game-automation/src/automation/ui/coordinate_picker.py
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
```

**What happens:**
- Creates Promise that resolves when `this.result` is set
- Polls every 100ms
- Resolves with result or null (if cancelled)

---

### **STEP 11: User Interaction - Mouse Events**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**JavaScript Methods:** `onMouseDown()`, `onMouseMove()`, `onMouseUp()`  
**Line:** 172-238

**Code Reference:**
```172:238:mini-game-automation/src/automation/ui/coordinate_picker.py
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
```

**What happens:**
- **onMouseDown:** Starts drag, shows green selection rectangle
- **onMouseMove:** Updates rectangle size as user drags
- **onMouseUp:** Captures region if size > 10x10 pixels

---

### **STEP 12: Capture Region**

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`  
**JavaScript Method:** `captureRegion()`  
**Line:** 267-270

**Code Reference:**
```267:270:mini-game-automation/src/automation/ui/coordinate_picker.py
captureRegion(x, y, width, height) {
    this.result = { x, y, width, height };
    this.destroy();
},
```

**What happens:**
- Sets `this.result` with coordinates
- Calls `destroy()` to clean up overlay
- `waitForResult()` detects result and resolves Promise

---

### **STEP 13: Apply Result to UI**

**File:** `mini-game-automation/src/automation/ui/main_window.py`  
**Method:** `_apply_table_region()`  
**Line:** 1190-1197

**Code Reference:**
```1190:1197:mini-game-automation/src/automation/ui/main_window.py
def _apply_table_region(self, result: Dict[str, int]):
    """Apply picked table region to form."""
    self.coord_vars["x"].set(str(result.get("x", 0)))
    self.coord_vars["y"].set(str(result.get("y", 0)))
    self.coord_vars["width"].set(str(result.get("width", 0)))
    self.coord_vars["height"].set(str(result.get("height", 0)))
    self.status_var.set("✓ Table region captured")
    messagebox.showinfo("Success", "Table region captured! Review and save if correct.")
```

**What happens:**
- Updates form fields with captured coordinates
- Shows success message

---

## Test Coordinate Picker Flow

### **File:** `mini-game-automation/test_picker_standalone.html`  
**Line:** 255-264

**Code Reference:**
```255:264:mini-game-automation/test_picker_standalone.html
function testPicker() {
    try {
        const result = eval(PICKER_SCRIPT);
        console.log('Picker result:', result);
        document.getElementById('result').innerHTML = 'Picker initialized! Look for green overlay.';
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = 'Error: ' + error.message;
    }
}
```

**Issue:** Uses `eval()` which may have scoping issues. The script is wrapped in an IIFE (Immediately Invoked Function Expression) which should work, but the result handling is incomplete.

---

## Known Issues and Potential Causes

### **Issue 1: Overlay Not Appearing**

**Symptoms:**
- Overlay creation verified in JavaScript console
- Overlay exists in DOM
- Overlay visibility check passes
- But overlay not visible to user

**Potential Causes:**
1. **Z-index conflict:** Another element may have higher z-index
2. **CSS override:** Page CSS may override `!important` styles
3. **Iframe context:** If page uses iframes, overlay may be in wrong context
4. **Browser rendering:** Playwright may not render overlay correctly
5. **Timing issue:** Overlay created but removed before visible
6. **Body append issue:** Overlay appended but body not fully rendered

**Debugging Steps:**
- Check browser console for errors
- Inspect DOM to verify overlay exists
- Check computed styles in DevTools
- Verify z-index is actually 999999
- Check if overlay is behind other elements

### **Issue 2: Test Picker Not Working**

**Symptoms:**
- Clicking "Test Coordinate Picker" button doesn't show overlay
- JavaScript errors in console

**Potential Causes:**
1. **eval() scoping:** Result not accessible
2. **Script execution:** IIFE may not execute correctly
3. **Event listener timing:** Events attached before overlay ready

**Debugging Steps:**
- Check browser console for errors
- Verify script executes without errors
- Test overlay creation manually in console
- Check if event listeners are attached

---

## File Summary

| File | Purpose | Key Lines |
|------|---------|-----------|
| `main_window.py` | UI entry point | 1128-1188 |
| `coordinate_picker.py` | Core picker logic | 17-478 |
| `test_picker_standalone.html` | Standalone test | 1-267 |
| `test_coordinate_picker.html` | Alternative test page | 1-111 |

---

## Next Steps for Debugging

1. **Add more logging** to JavaScript init() method
2. **Check browser DevTools** for overlay element
3. **Test overlay creation** manually in browser console
4. **Verify z-index** is actually applied
5. **Check for CSS conflicts** from page styles
6. **Test in different browsers** (Chrome, Firefox)
7. **Add screenshot capture** to verify overlay state
8. **Test with simpler overlay** (solid color, no transparency)

---

## Related Files

- **Button Picker:** `_pick_button()` - Line 1199-1224 in `main_window.py`
- **Region Picker:** `_pick_region()` - Line 1239-1274 in `main_window.py`
- **Stop Picker:** `stop_picking()` - Line 463-477 in `coordinate_picker.py`

---

*Document generated: 2026-01-05*  
*Epic 4: Desktop Control Interface - Story 4.9: Visual Coordinate Picker*
