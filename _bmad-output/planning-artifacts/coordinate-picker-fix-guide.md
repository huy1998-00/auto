# Coordinate Picker Fix Guide - Step by Step

## Problem Summary

**Issue:** Coordinate picker overlay not appearing when "Pick Table Region" button is clicked.

**Root Cause:** Playwright async `Page` objects are bound to their original event loop. When we create a new event loop in a thread (`asyncio.new_event_loop()`), we cannot use the page object from the original loop. All `await page.evaluate()` calls hang indefinitely.

**Evidence:**
- Execution stops at `page.evaluate("document.body !== null")` 
- No errors thrown - call hangs indefinitely
- Page object exists and is valid, but can't be used in different event loop

---

## Solution Overview

**Approach:** Use the same event loop that created the page object instead of creating a new one.

**Method:** 
1. Store reference to the original event loop when browser opens
2. Keep the loop running with a background task
3. Use `asyncio.run_coroutine_threadsafe()` to schedule coroutines in the original loop

**Files to Modify:**
- `mini-game-automation/src/automation/main.py`
- `mini-game-automation/src/automation/ui/main_window.py`

---

## Step-by-Step Implementation

### Step 1: Add Event Loop Storage Variable

**File:** `mini-game-automation/src/automation/main.py`

**Location:** In `AutomationApp.__init__()` method, around line 90

**Action:** Add event loop storage variable

**Code to Add:**
```python
# Around line 90, after self.ui_window initialization, add:
self.browser_event_loop: Optional[asyncio.AbstractEventLoop] = None
```

**Full Context:**
```python
# State
self._is_running = False
self.ui_window: Optional[MainWindow] = None
self._ui_thread: Optional[threading.Thread] = None
self.browser_event_loop: Optional[asyncio.AbstractEventLoop] = None  # ADD THIS LINE
```

**Verification:** Check that `Optional` is imported from `typing` (should already be imported).

---

### Step 2: Store Event Loop When Browser Opens

**File:** `mini-game-automation/src/automation/main.py`

**Location:** In `_on_ui_open_browser()` method, around line 358

**Action:** Modify the `open_thread()` function to store the loop reference and keep it running

**Find This Code:**
```python
def open_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(self._open_browser_only())
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        if self.ui_window:
            self.ui_window.root.after(0, lambda: self.ui_window._on_browser_error(str(e)))

threading.Thread(target=open_thread, daemon=True).start()
```

**Replace With:**
```python
def open_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # STORE THE LOOP REFERENCE
    self.browser_event_loop = loop
    
    try:
        # Run browser initialization
        loop.run_until_complete(self._open_browser_only())
        
        # Keep loop running so we can schedule coroutines to it later
        # Create a background task that keeps the loop alive
        async def keepalive():
            while True:
                await asyncio.sleep(1)
        
        loop.create_task(keepalive())
        
        # Run loop forever (until thread is killed)
        loop.run_forever()
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        if self.ui_window:
            self.ui_window.root.after(0, lambda: self.ui_window._on_browser_error(str(e)))
    finally:
        loop.close()
        self.browser_event_loop = None

threading.Thread(target=open_thread, daemon=True).start()
```

**Key Changes:**
1. Store loop: `self.browser_event_loop = loop`
2. Create keepalive task after browser initialization
3. Use `loop.run_forever()` instead of letting thread finish
4. Clean up loop reference in `finally` block

---

### Step 3: Add Method to Get Event Loop

**File:** `mini-game-automation/src/automation/main.py`

**Location:** In `start_ui()` method, around line 339 (right after `get_browser_page`)

**Action:** Add method to get browser event loop

**Find This Code:**
```python
# Add method to get browser page for coordinate picker
self.ui_window.get_browser_page = lambda: self.browser_manager.page if self.browser_manager else None
```

**Add After It:**
```python
# Add method to get browser event loop for coordinate picker
self.ui_window.get_browser_event_loop = lambda: self.browser_event_loop
```

**Full Context:**
```python
# Add method to get browser page for coordinate picker
self.ui_window.get_browser_page = lambda: self.browser_manager.page if self.browser_manager else None

# Add method to get browser event loop for coordinate picker
self.ui_window.get_browser_event_loop = lambda: self.browser_event_loop
```

---

### Step 4: Modify pick_thread() to Use Original Event Loop

**File:** `mini-game-automation/src/automation/ui/main_window.py`

**Location:** In `_pick_table_region()` method, the `pick_thread()` function around line 1177

**Action:** Replace the entire `pick_thread()` function to use `run_coroutine_threadsafe()` instead of creating a new event loop

**Find This Code:**
```python
def pick_thread():
    print("DEBUG: pick_thread() started")
    logger.info("DEBUG: pick_thread() started")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Check if page is still valid
        # NOTE: Temporarily skipping accessibility check due to event loop conflict
        # The page object was created in a different event loop, causing deadlock
        print("DEBUG: Skipping page accessibility check (known event loop issue)")
        print(f"DEBUG: browser_page object: {self.browser_page}")
        print(f"DEBUG: browser_page type: {type(self.browser_page)}")
        print(f"DEBUG: browser_page URL: {self.browser_page.url}")
        logger.info("DEBUG: Skipping page accessibility check - proceeding directly to picker")
        
        # TODO: Fix event loop conflict - page was created in different async context
        # For now, skip the check and proceed - if page is invalid, picker will fail gracefully

        print("DEBUG: Creating CoordinatePicker instance")
        logger.info("DEBUG: Creating CoordinatePicker instance")
        picker = CoordinatePicker(self.browser_page)
        print("DEBUG: Calling picker.pick_table_region()")
        logger.info("DEBUG: Calling picker.pick_table_region()")
        result = loop.run_until_complete(picker.pick_table_region())
        print(f"DEBUG: picker.pick_table_region() returned: {result}")
        logger.info(f"DEBUG: picker.pick_table_region() returned: {result}")
        
        if result:
            self.window.after(0, lambda: self._apply_table_region(result))
        else:
            self.window.after(0, lambda: messagebox.showinfo("Cancelled", "Coordinate picking cancelled"))
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in pick_thread(): {e}")
        print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
        error_msg = f"Failed to pick coordinates:\n{str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        self.window.after(0, lambda: messagebox.showerror(
            "Error",
            f"Failed to pick coordinates:\n{str(e)}\n\n"
            "Check logs for details. Make sure browser is open and on a valid page."
        ))
    finally:
        loop.close()

threading.Thread(target=pick_thread, daemon=True).start()
```

**Replace With:**
```python
def pick_thread():
    print("DEBUG: pick_thread() started")
    logger.info("DEBUG: pick_thread() started")
    
    # Get the original event loop instead of creating new one
    original_loop = None
    if hasattr(self, 'get_browser_event_loop'):
        original_loop = self.get_browser_event_loop()
    
    if not original_loop:
        print("DEBUG: ERROR - Browser event loop not available")
        logger.error("DEBUG: Browser event loop not available")
        self.window.after(0, lambda: messagebox.showerror(
            "Error",
            "Browser event loop not available. Please open browser first."
        ))
        return
    
    if not self.browser_page:
        print("DEBUG: ERROR - Browser page not available")
        logger.error("DEBUG: Browser page not available")
        self.window.after(0, lambda: messagebox.showwarning(
            "Browser Not Available",
            "Browser page not available.\n\n"
            "Please:\n"
            "1. Click 'Open Browser' in the main window\n"
            "2. Navigate to your game page\n"
            "3. Then try picking coordinates again"
        ))
        return
    
    try:
        print("DEBUG: Using original event loop for coordinate picker")
        print(f"DEBUG: Original loop: {original_loop}")
        logger.info("DEBUG: Using original event loop")
        
        print("DEBUG: Creating CoordinatePicker instance")
        logger.info("DEBUG: Creating CoordinatePicker instance")
        picker = CoordinatePicker(self.browser_page)
        
        print("DEBUG: Calling picker.pick_table_region() via run_coroutine_threadsafe")
        logger.info("DEBUG: Calling picker.pick_table_region() via run_coroutine_threadsafe")
        
        # Use run_coroutine_threadsafe to run in original loop
        future = asyncio.run_coroutine_threadsafe(
            picker.pick_table_region(),
            original_loop
        )
        
        # Wait for result (blocking call, but in separate thread)
        result = future.result(timeout=60.0)  # 60 second timeout
        
        print(f"DEBUG: picker.pick_table_region() returned: {result}")
        logger.info(f"DEBUG: picker.pick_table_region() returned: {result}")
        
        if result:
            self.window.after(0, lambda: self._apply_table_region(result))
        else:
            self.window.after(0, lambda: messagebox.showinfo("Cancelled", "Coordinate picking cancelled"))
            
    except asyncio.TimeoutError:
        print("DEBUG: ERROR - Coordinate picking timed out")
        logger.error("DEBUG: Coordinate picking timed out")
        self.window.after(0, lambda: messagebox.showerror(
            "Timeout",
            "Coordinate picking timed out after 60 seconds."
        ))
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in pick_thread(): {e}")
        print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
        error_msg = f"Failed to pick coordinates:\n{str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        self.window.after(0, lambda: messagebox.showerror(
            "Error",
            f"Failed to pick coordinates:\n{str(e)}\n\n"
            "Check logs for details. Make sure browser is open and on a valid page."
        ))

threading.Thread(target=pick_thread, daemon=True).start()
```

**Key Changes:**
1. Remove `loop = asyncio.new_event_loop()` - don't create new loop
2. Get original loop via `get_browser_event_loop()`
3. Check if loop is available, show error if not
4. Use `asyncio.run_coroutine_threadsafe()` instead of `loop.run_until_complete()`
5. Use `future.result(timeout=60.0)` to wait for result
6. Remove `loop.close()` in finally (we don't own this loop)

---

### Step 5: Remove Debug Logging (Optional Cleanup)

**File:** `mini-game-automation/src/automation/ui/main_window.py`

**Location:** In `_pick_table_region()` method, before `pick_thread()` definition

**Action:** Remove or comment out excessive debug print statements (optional, but recommended for production)

**Note:** You can keep the logger.info() statements but remove print() statements if desired.

---

### Step 6: Remove Debug Logging from CoordinatePicker (Optional Cleanup)

**File:** `mini-game-automation/src/automation/ui/coordinate_picker.py`

**Action:** Remove debug print statements added during investigation (optional)

**Note:** Keep logger statements, but remove print() calls if you want cleaner code.

---

## Testing Steps

### Test 1: Basic Functionality

1. **Start the application**
2. **Open browser** (click "Open Browser" button)
3. **Wait for browser to open** (should navigate to test_coordinate_picker.html)
4. **Open "Configure Tables" window**
5. **Click "📐 Pick Table Region" button**
6. **Expected Result:**
   - Info dialog appears: "Coordinate picker will appear in the browser window"
   - Green overlay appears in browser window
   - Can drag to select region
   - Coordinates are captured and displayed in form fields

### Test 2: Error Handling

1. **Start application**
2. **DO NOT open browser**
3. **Open "Configure Tables" window**
4. **Click "📐 Pick Table Region" button**
5. **Expected Result:**
   - Error message: "Browser event loop not available. Please open browser first."

### Test 3: Cancellation

1. **Follow Test 1 steps 1-5**
2. **Press ESC key** when overlay appears
3. **Expected Result:**
   - Overlay disappears
   - Message: "Coordinate picking cancelled"

### Test 4: Multiple Tables

1. **Follow Test 1**
2. **After picking first table region, pick another**
3. **Expected Result:**
   - Each pick works independently
   - No conflicts or hanging

---

## Verification Checklist

After implementation, verify:

- [ ] Code compiles without errors
- [ ] No linting errors
- [ ] Browser opens successfully
- [ ] Event loop is stored when browser opens
- [ ] Event loop stays running (check thread is alive)
- [ ] "Pick Table Region" button works
- [ ] Overlay appears in browser
- [ ] Can drag to select region
- [ ] Coordinates are captured correctly
- [ ] Error handling works (no browser case)
- [ ] ESC key cancels picker
- [ ] No hanging or infinite waits
- [ ] Console shows appropriate debug logs
- [ ] No exceptions in logs

---

## Troubleshooting

### Issue: "Browser event loop not available" error

**Cause:** Browser not opened yet, or loop wasn't stored properly.

**Fix:** 
- Ensure browser is opened before clicking "Pick Table Region"
- Check that `self.browser_event_loop` is set in `open_thread()`
- Verify loop is still running (check thread status)

### Issue: Overlay still doesn't appear

**Cause:** Event loop might have stopped, or page object issue.

**Fix:**
- Check console logs for errors
- Verify `run_coroutine_threadsafe()` is being called
- Check if `future.result()` completes or times out
- Verify page object is valid

### Issue: Application hangs

**Cause:** Event loop might be blocked or deadlocked.

**Fix:**
- Check that keepalive task is running
- Verify `loop.run_forever()` is executing
- Check for blocking operations in the loop

### Issue: Thread doesn't finish

**Cause:** `loop.run_forever()` keeps thread alive (this is expected).

**Fix:** This is correct behavior - the thread should stay alive to keep the loop running.

---

## Code Summary

**Total Changes:**
- **File 1 (main.py):** 3 modifications, ~20 lines added/changed
- **File 2 (main_window.py):** 1 modification, ~40 lines changed
- **Total:** ~60 lines changed across 2 files

**Risk Level:** Low - Focused changes, preserves existing architecture

**Breaking Changes:** None - Backward compatible

---

## Implementation Order

1. ✅ Step 1: Add event loop storage variable
2. ✅ Step 2: Store event loop when browser opens
3. ✅ Step 3: Add method to get event loop
4. ✅ Step 4: Modify pick_thread() to use original loop
5. ⚠️ Step 5: Remove debug logging (optional)
6. ⚠️ Step 6: Clean up CoordinatePicker debug logs (optional)
7. ✅ Test all scenarios
8. ✅ Verify checklist

---

## Expected Outcome

After implementing these changes:
- ✅ Coordinate picker overlay appears correctly
- ✅ No hanging or infinite waits
- ✅ Proper error handling
- ✅ Clean execution flow
- ✅ All functionality works as expected

---

**Document Version:** 1.0  
**Created:** 2026-01-07  
**Based on:** Root cause analysis from brainstorming session
