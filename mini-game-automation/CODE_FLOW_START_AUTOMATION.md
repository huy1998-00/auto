# Code Flow: Start Automation Button Click

This document traces the complete code execution path when the user clicks the "Start Automation" button.

## Step-by-Step Execution Flow

### 1. User Clicks "Start Automation" Button

**File:** `src/automation/ui/main_window.py`  
**Line:** 138-144

```138:144:src/automation/ui/main_window.py
        self.start_button = ttk.Button(
            control_frame,
            text="Start Automation",
            command=self._on_start_clicked,
            state=tk.DISABLED,
        )
```

The button's `command` parameter is set to `self._on_start_clicked`, which is called when clicked.

---

### 2. UI Handler: `_on_start_clicked()`

**File:** `src/automation/ui/main_window.py`  
**Lines:** 428-475

**Execution Path:**
- **Line 428:** Method `_on_start_clicked()` is called
- **Lines 430-440:** Validates browser is opened
- **Lines 443-453:** Shows confirmation dialog
- **Lines 456-464:** Checks if tables are configured
- **Line 466:** Sets `self.is_running = True`
- **Lines 467-470:** Updates UI button states
- **Line 471:** Logs "Starting automation..."
- **Line 474:** Calls `self.on_start()` callback

```428:475:src/automation/ui/main_window.py
    def _on_start_clicked(self):
        """Handle start button click."""
        if not self.browser_opened:
            messagebox.showwarning(
                "Warning",
                "Please open browser first!\n\n"
                "1. Enter Game URL\n"
                "2. Click 'Open Browser'\n"
                "3. Manually navigate, login, and set up the page\n"
                "4. Configure tables and patterns\n"
                "5. Then start automation"
            )
            return

        # Confirm user has completed manual setup
        response = messagebox.askyesno(
            "Ready to Start Automation?",
            "Before starting, please confirm:\n\n"
            "✓ You have navigated to the game page\n"
            "✓ You have logged in (if required)\n"
            "✓ The game page is fully loaded\n"
            "✓ Tables are visible on the page\n\n"
            "Have you completed the manual setup?"
        )
        if not response:
            return

        # Check if tables are configured
        if not self._check_tables_configured():
            response = messagebox.askyesno(
                "No Tables Configured",
                "No tables are configured yet.\n\n"
                "Do you want to start anyway?\n"
                "(You can add tables later)"
            )
            if not response:
                return

        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.open_browser_button.config(state=tk.DISABLED)
        self.configure_tables_button.config(state=tk.DISABLED)
        self.log("Starting automation...")

        if self.on_start:
            self.on_start()
```

---

### 3. Main App Callback: `_on_ui_start()`

**File:** `src/automation/main.py`  
**Lines:** 470-478

**Execution Path:**
- **Line 470:** Method `_on_ui_start()` is called
- **Lines 473-476:** Creates a new thread with a new event loop
- **Line 476:** Runs `_start_automation_after_config()` in the thread

```470:478:src/automation/main.py
    def _on_ui_start(self):
        """Handle UI start button click (automation starts after configuration)."""
        # Start automation in background thread
        def start_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._start_automation_after_config())
        
        threading.Thread(target=start_thread, daemon=True).start()
```

**Note:** The callback `on_start` is set during UI initialization at line 331:
```329:335:src/automation/main.py
            self.ui_window = MainWindow(
                on_open_browser=self._on_ui_open_browser,
                on_start=self._on_ui_start,
                on_stop=self._on_ui_stop,
                on_pattern_update=self._on_pattern_update,
                on_coordinates_update=self._on_coordinates_update,
            )
```

---

### 4. Main Automation Initialization: `_start_automation_after_config()`

**File:** `src/automation/main.py`  
**Lines:** 480-597

**Execution Path:**

#### 4.1 Browser Validation (Lines 491-495)
- **Line 492:** Checks if browser_manager exists and is initialized
- **Line 494:** Logs error if browser not opened

#### 4.2 Canvas Wait (Lines 498-515)
- **Line 499:** Logs "Waiting for canvas element..."
- **Line 501:** Waits for canvas element with 30 second timeout
- **Lines 502-514:** Shows warning if canvas not found

#### 4.3 Page Monitor Initialization (Lines 518-520)
- **Line 519:** Creates PageMonitor if not exists
- **Line 520:** Starts page monitoring

#### 4.4 Session Manager Initialization (Lines 523-525)
- **Line 524:** Creates SessionManager if not exists
- **Line 525:** Creates a new session

#### 4.5 Cache Manager Initialization (Lines 527-532)
- **Line 529:** Creates JSONWriter
- **Lines 529-532:** Creates CacheManager with session_manager and json_writer

#### 4.6 Resource Monitor Initialization (Lines 534-535)
- **Line 535:** Creates ResourceMonitor if not exists

#### 4.7 Multi-Table Manager Initialization (Lines 538-560)
- **Lines 539-541:** Creates ScreenshotScheduler
- **Lines 543-544:** Creates TemplateMatcher and loads templates
- **Line 545:** Creates OCRFallback
- **Lines 546-549:** Creates ImageExtractor
- **Line 551:** Creates ErrorRecovery
- **Lines 553-560:** Creates MultiTableManager with all components

#### 4.8 Configuration Loading (Line 563)
- **Line 563:** Loads configuration from YAML files

#### 4.9 Add Tables from Config (Lines 566-572)
- **Line 566:** Gets tables configuration
- **Lines 568-572:** Loops through each table and adds it
  - **Line 569:** Calls `add_table_from_config(table_id)`
  - **Line 572:** Logs "Added table {table_id}"

#### 4.10 Start All Tables (Lines 590-594)
- **Line 591:** Calls `multi_table_manager.start_all()`
- **Lines 592-594:** Logs success message

#### 4.11 Start Automation Loop (Line 597)
- **Line 597:** Calls `run_automation_loop()`

```480:597:src/automation/main.py
    async def _start_automation_after_config(self):
        """
        Start automation after browser is opened and user has completed manual setup.
        
        This is called when user clicks "Start Automation" button.
        User should have already:
        1. Opened browser
        2. Manually navigated and logged in
        3. Set up the page
        4. Configured tables and patterns
        """
        # Browser should already be open
        if not self.browser_manager or not self.browser_manager.is_initialized:
            if self.ui_window:
                self.ui_window.log("Error: Browser not opened. Please open browser first.")
            return

        # Wait for canvas to be ready (user should have navigated to game page)
        if self.ui_window:
            self.ui_window.log("Waiting for canvas element...")
        
        if not await self.browser_manager.wait_for_canvas(timeout=30000):
            if self.ui_window:
                self.ui_window.log("Warning: Canvas not found. Make sure you're on the game page.")
                # Show warning in UI thread
                from tkinter import messagebox
                self.ui_window.root.after(0, lambda: messagebox.showwarning(
                    "Canvas Not Found",
                    "Canvas element (#layaCanvas) not found.\n\n"
                    "Please make sure:\n"
                    "1. You're logged in\n"
                    "2. You're on the game page\n"
                    "3. The game has loaded\n\n"
                    "Then click 'Start Automation' again."
                ))
            return

        # Initialize page monitor (now that canvas is ready)
        if not self.page_monitor:
            self.page_monitor = PageMonitor(self.browser_manager)
            await self.page_monitor.start_monitoring()

        # Initialize remaining components
        if not self.session_manager:
            self.session_manager = SessionManager()
            self.session_manager.create_session()

        if not self.cache_manager:
            json_writer = JSONWriter()
            self.cache_manager = CacheManager(
                session_manager=self.session_manager,
                json_writer=json_writer,
            )

        if not self.resource_monitor:
            self.resource_monitor = ResourceMonitor()

        # Initialize multi-table manager if not exists
        if not self.multi_table_manager:
            screenshot_scheduler = ScreenshotScheduler(
                resource_monitor=self.resource_monitor,
            )

            template_matcher = TemplateMatcher()
            template_matcher.load_templates()
            ocr_fallback = OCRFallback(lazy_load=True)
            image_extractor = ImageExtractor(
                template_matcher=template_matcher,
                ocr_fallback=ocr_fallback,
            )

            error_recovery = ErrorRecovery()

            self.multi_table_manager = MultiTableManager(
                browser_manager=self.browser_manager,
                session_manager=self.session_manager,
                cache_manager=self.cache_manager,
                image_extractor=image_extractor,
                screenshot_scheduler=screenshot_scheduler,
                error_recovery=error_recovery,
            )

        # Load configuration
        self.load_config()

        # Add tables from configuration
        tables_config = self.table_regions_config.get("tables", {})
        tables_added = 0
        for table_id in tables_config.keys():
            if self.add_table_from_config(table_id):
                tables_added += 1
                if self.ui_window:
                    self.ui_window.log(f"Added table {table_id}")

        if tables_added == 0:
            if self.ui_window:
                self.ui_window.log("Warning: No tables configured. Please configure tables first.")
                from tkinter import messagebox
                self.ui_window.root.after(0, lambda: messagebox.showwarning(
                    "No Tables Configured",
                    "No tables are configured.\n\n"
                    "Please:\n"
                    "1. Click 'Configure Tables'\n"
                    "2. Use visual picker to set table coordinates\n"
                    "3. Save configuration\n"
                    "4. Then click 'Start Automation' again"
                ))
            return

        # Start all tables
        if self.multi_table_manager:
            self.multi_table_manager.start_all()
            if self.ui_window:
                self.ui_window.log(f"✓ Automation started with {tables_added} table(s)")
                self.ui_window.log("Automation is now running. Monitor status in the UI.")

        # Start automation loop
        await self.run_automation_loop()
```

---

### 5. Add Table from Config: `add_table_from_config()`

**File:** `src/automation/main.py`  
**Lines:** 218-251

**Execution Path:**
- **Line 228:** Gets tables configuration
- **Line 229:** Gets specific table config
- **Lines 231-233:** Returns False if table config not found
- **Line 236:** Gets default patterns
- **Lines 238-251:** Calls `multi_table_manager.add_table()` with all configuration

```218:251:src/automation/main.py
    def add_table_from_config(self, table_id: int) -> bool:
        """
        Add a table using configuration.

        Args:
            table_id: Table ID to add (1-6)

        Returns:
            True if added successfully
        """
        tables_config = self.table_regions_config.get("tables", {})
        table_config = tables_config.get(table_id)

        if not table_config:
            logger.error(f"No configuration found for table {table_id}")
            return False

        # Get default patterns
        default_patterns = self.default_patterns_config.get("default_patterns", "")

        return self.multi_table_manager.add_table(
            table_id=table_id,
            table_region={
                "x": table_config["x"],
                "y": table_config["y"],
                "width": table_config["width"],
                "height": table_config["height"],
            },
            button_coords=table_config.get("buttons", {}),
            timer_region=table_config.get("timer", {}),
            blue_score_region=table_config.get("blue_score", {}),
            red_score_region=table_config.get("red_score", {}),
            patterns=default_patterns,
        )
```

---

### 6. Multi-Table Manager: `add_table()`

**File:** `src/automation/orchestration/multi_table_manager.py`  
**Lines:** 106-169

**Execution Path:**
- **Line 131:** Acquires global lock
- **Lines 133-135:** Checks table limit (max 6)
- **Lines 138-140:** Checks if table already exists
- **Lines 143-147:** Creates TableTracker instance
- **Lines 150-156:** Stores table configuration
- **Line 159:** Creates per-table lock
- **Line 162:** Stores tracker in `_tables` dict
- **Line 165:** Initializes cache for table
- **Line 167:** Logs success

```106:169:src/automation/orchestration/multi_table_manager.py
    def add_table(
        self,
        table_id: int,
        table_region: Dict[str, int],
        button_coords: Dict[str, Dict[str, int]],
        timer_region: Dict[str, int],
        blue_score_region: Dict[str, int],
        red_score_region: Dict[str, int],
        patterns: Optional[str] = None,
    ) -> bool:
        """
        Add a table to management.

        Args:
            table_id: Table ID (1-6)
            table_region: Table region coordinates
            button_coords: Button coordinates dictionary
            timer_region: Timer region coordinates
            blue_score_region: Blue score region coordinates
            red_score_region: Red score region coordinates
            patterns: Optional pattern string

        Returns:
            True if added successfully, False otherwise
        """
        with self._global_lock:
            # Check table limit
            if len(self._tables) >= MAX_TABLES:
                logger.error(f"Maximum tables ({MAX_TABLES}) reached, cannot add table {table_id}")
                return False

            # Check if table already exists
            if table_id in self._tables:
                logger.warning(f"Table {table_id} already exists")
                return False

            # Create table tracker
            tracker = TableTracker(
                table_id=table_id,
                patterns=patterns,
                table_region=table_region,
            )

            # Store configuration
            self._table_configs[table_id] = {
                "table_region": table_region,
                "button_coords": button_coords,
                "timer_region": timer_region,
                "blue_score_region": blue_score_region,
                "red_score_region": red_score_region,
            }

            # Create per-table lock
            self._table_locks[table_id] = threading.Lock()

            # Store tracker
            self._tables[table_id] = tracker

            # Initialize cache
            self.cache_manager.initialize_table(table_id)

            logger.info(f"Added table {table_id}", extra={"table_id": table_id})

            return True
```

---

### 7. Start All Tables: `start_all()`

**File:** `src/automation/orchestration/multi_table_manager.py`  
**Lines:** 452-457

**Execution Path:**
- **Line 454:** Loops through all tables
- **Line 455:** Calls `start_table(table_id)` for each
- **Line 456:** Sets `_is_running = True`
- **Line 457:** Logs "All tables started"

```452:457:src/automation/orchestration/multi_table_manager.py
    def start_all(self) -> None:
        """Start all tables."""
        for table_id in self._tables:
            self.start_table(table_id)
        self._is_running = True
        logger.info("All tables started")
```

---

### 8. Start Individual Table: `start_table()`

**File:** `src/automation/orchestration/multi_table_manager.py`  
**Lines:** 379-395

**Execution Path:**
- **Line 389:** Gets table tracker
- **Line 390:** Returns False if tracker not found
- **Line 393:** Calls `tracker.resume()` to activate table
- **Line 394:** Logs "Started table {table_id}"

```379:395:src/automation/orchestration/multi_table_manager.py
    def start_table(self, table_id: int) -> bool:
        """
        Start processing a specific table.

        Args:
            table_id: Table ID to start

        Returns:
            True if started, False otherwise
        """
        tracker = self._tables.get(table_id)
        if not tracker:
            return False

        tracker.resume()
        logger.info(f"Started table {table_id}", extra={"table_id": table_id})
        return True
```

---

### 9. Table Tracker Resume: `resume()`

**File:** `src/automation/orchestration/table_tracker.py`  
**Lines:** 375-381

**Execution Path:**
- **Line 377:** Checks if in learning phase
- **Line 378:** Sets status to LEARNING if in learning phase
- **Line 380:** Sets status to ACTIVE if not in learning phase
- **Line 381:** Logs "Table resumed"

```375:381:src/automation/orchestration/table_tracker.py
    def resume(self) -> None:
        """Resume table tracking."""
        if self.state.learning_phase:
            self.state.status = TableStatus.LEARNING
        else:
            self.state.status = TableStatus.ACTIVE
        logger.info(f"Table resumed", extra={"table_id": self.table_id})
```

---

### 10. Main Automation Loop: `run_automation_loop()`

**File:** `src/automation/main.py`  
**Lines:** 253-291

**Execution Path:**
- **Line 260:** Sets `_is_running = True`
- **Line 263:** Starts infinite loop
- **Line 265:** Checks for page refresh
- **Lines 266-275:** Handles page refresh if detected
- **Line 278:** Processes all tables in parallel
- **Line 281:** Gets dynamic screenshot interval
- **Line 284:** Sleeps before next iteration

```253:291:src/automation/main.py
    async def run_automation_loop(self) -> None:
        """
        Main automation loop.

        Continuously processes tables until stopped.
        """
        logger.info("Starting automation loop")
        self._is_running = True

        try:
            while self._is_running:
                # Check for page refresh
                if await self.page_monitor.check_page_refresh():
                    logger.warning("Page refresh detected, pausing tables")
                    self.multi_table_manager.pause_all()

                    # Wait for canvas to be ready
                    if await self.page_monitor.wait_for_canvas_ready():
                        logger.info("Canvas ready, resuming tables")
                        self.multi_table_manager.resume_all()
                    else:
                        logger.error("Canvas not ready after refresh")
                        continue

                # Process all tables
                results = await self.multi_table_manager.process_all_tables()

                # Get dynamic interval based on table states
                interval_ms = self.multi_table_manager.get_screenshot_interval()

                # Sleep before next iteration
                await asyncio.sleep(interval_ms / 1000)

        except asyncio.CancelledError:
            logger.info("Automation loop cancelled")
        except Exception as e:
            logger.error(f"Error in automation loop: {e}")
        finally:
            self._is_running = False
```

---

### 11. Process All Tables: `process_all_tables()`

**File:** `src/automation/orchestration/multi_table_manager.py`  
**Lines:** 350-377

**Execution Path:**
- **Line 358:** Gets tables to capture from scheduler
- **Lines 363-368:** Creates async tasks for each table
- **Lines 370-375:** Waits for all tasks to complete
- **Line 377:** Returns results dictionary

```350:377:src/automation/orchestration/multi_table_manager.py
    async def process_all_tables(self) -> Dict[int, bool]:
        """
        Process all active tables in parallel.

        Returns:
            Dictionary mapping table_id to success status
        """
        # Get tables to process
        tables_to_process = self.screenshot_scheduler.get_tables_to_capture(
            list(self._tables.values())
        )

        # Process in parallel using asyncio
        results = {}
        tasks = []

        for tracker in tables_to_process:
            task = asyncio.create_task(self.process_table(tracker.table_id))
            tasks.append((tracker.table_id, task))

        for table_id, task in tasks:
            try:
                results[table_id] = await task
            except Exception as e:
                logger.error(f"Task failed for table {table_id}: {e}")
                results[table_id] = False

        return results
```

---

### 12. Process Single Table: `process_table()`

**File:** `src/automation/orchestration/multi_table_manager.py`  
**Lines:** 212-348

**Execution Path:**

#### 12.1 Get Tracker and Config (Lines 225-233)
- **Line 225:** Gets table tracker
- **Line 226:** Gets table config
- **Lines 228-233:** Returns False if not found or not active

#### 12.2 Capture Screenshot (Lines 237-250)
- **Line 237:** Captures screenshot of table region
- **Lines 242-250:** Handles screenshot failure

#### 12.3 Extract Game State (Lines 253-270)
- **Line 253:** Extracts game state from screenshot
- **Lines 262-270:** Handles extraction failure

#### 12.4 Update Tracker State (Lines 277-318)
- **Line 279:** Detects new round
- **Lines 281-291:** Records round result if new round detected
- **Lines 294-307:** Persists round to cache
- **Line 309:** Sends round complete update
- **Line 312:** Updates timer
- **Lines 315-318:** Updates scores

#### 12.5 Make Decision and Click (Lines 321-335)
- **Line 321:** Checks if should make decision
- **Line 322:** Gets decision from tracker
- **Line 324:** Checks if timer is clickable
- **Line 326:** Gets canvas box
- **Lines 328-335:** Executes two-phase click

#### 12.6 Send Status Update (Line 338)
- **Line 338:** Sends status update to UI

```212:348:src/automation/orchestration/multi_table_manager.py
    async def process_table(self, table_id: int) -> bool:
        """
        Process a single table iteration.

        Captures screenshot, extracts state, makes decisions,
        and executes clicks as needed.

        Args:
            table_id: Table ID to process

        Returns:
            True if processed successfully, False otherwise
        """
        tracker = self._tables.get(table_id)
        config = self._table_configs.get(table_id)

        if not tracker or not config:
            return False

        # Skip if not active
        if not tracker.is_active():
            return False

        try:
            # Capture screenshot
            screenshot = await self.screenshot_capture.capture_region(
                table_id=table_id,
                table_region=config["table_region"],
            )

            if screenshot is None:
                # Handle capture failure
                should_continue = self.error_recovery.handle_screenshot_failure(
                    table_id=table_id,
                    tracker=tracker,
                )
                if not should_continue:
                    self._send_error_update(table_id, "Screenshot capture failed")
                return False

            # Extract game state
            game_state = self.image_extractor.extract_game_state(
                table_image=screenshot,
                table_id=table_id,
                timer_region=config["timer_region"],
                blue_score_region=config["blue_score_region"],
                red_score_region=config["red_score_region"],
            )

            # Check extraction success
            if game_state.timer is None:
                should_continue = self.error_recovery.handle_extraction_failure(
                    table_id=table_id,
                    tracker=tracker,
                    failure_type="timer",
                )
                if not should_continue:
                    self._send_error_update(table_id, "Timer extraction failed")
                return False

            # Reset error counts on success
            self.error_recovery.reset_error_count(table_id, "screenshot")
            self.error_recovery.reset_error_count(table_id, "extraction")

            # Update tracker state
            with self._table_locks[table_id]:
                # Check for new round
                if tracker.detect_new_round(game_state.timer):
                    # Get winner from score change
                    winner = tracker.update_scores(
                        game_state.blue_score or 0,
                        game_state.red_score or 0,
                    )

                    if winner:
                        # Record round result
                        round_result = tracker.record_round_result(
                            winner=winner,
                            timer_start=game_state.timer,
                        )

                        # Persist to cache/JSON
                        self.cache_manager.append_round(
                            table_id=table_id,
                            round_data={
                                "round_number": round_result.round_number,
                                "timestamp": round_result.timestamp,
                                "timer_start": round_result.timer_start,
                                "blue_score": round_result.blue_score,
                                "red_score": round_result.red_score,
                                "winner": round_result.winner,
                                "decision_made": round_result.decision_made,
                                "pattern_matched": round_result.pattern_matched,
                                "result": round_result.result,
                            },
                        )

                        self._send_round_complete_update(table_id, round_result)

                # Update timer
                tracker.update_timer(game_state.timer)

                # Update scores
                tracker.update_scores(
                    game_state.blue_score or 0,
                    game_state.red_score or 0,
                )

                # Check for decision
                if tracker.should_make_decision():
                    decision = tracker.get_decision()

                    if decision and tracker.is_timer_clickable():
                        # Execute click
                        canvas_box = await self.browser_manager.get_canvas_box()
                        if canvas_box:
                            await self.click_executor.execute_two_phase_click(
                                table_id=table_id,
                                team=decision,
                                canvas_box=canvas_box,
                                table_region=config["table_region"],
                                button_coords=config["button_coords"],
                                confirm=True,
                            )

            # Send status update to UI
            self._send_status_update(table_id, tracker)

            return True

        except Exception as e:
            logger.error(
                f"Error processing table: {e}",
                extra={"table_id": table_id},
            )
            self._send_error_update(table_id, str(e))
            return False
```

---

## Summary Flow Diagram

```
User Clicks "Start Automation"
    ↓
main_window.py: _on_start_clicked() [Line 428]
    ↓
main_window.py: self.on_start() [Line 474]
    ↓
main.py: _on_ui_start() [Line 470]
    ↓ (creates thread)
main.py: _start_automation_after_config() [Line 480]
    ↓
    ├─→ Browser validation [Line 492]
    ├─→ Wait for canvas [Line 501]
    ├─→ Initialize PageMonitor [Line 519]
    ├─→ Initialize SessionManager [Line 524]
    ├─→ Initialize CacheManager [Line 529]
    ├─→ Initialize ResourceMonitor [Line 535]
    ├─→ Initialize MultiTableManager [Line 553]
    ├─→ Load config [Line 563]
    ├─→ add_table_from_config() [Line 569]
    │   └─→ multi_table_manager.add_table() [Line 238]
    │       └─→ Creates TableTracker [Line 143]
    ├─→ multi_table_manager.start_all() [Line 591]
    │   └─→ start_table() [Line 455]
    │       └─→ tracker.resume() [Line 393]
    └─→ run_automation_loop() [Line 597]
        └─→ process_all_tables() [Line 278]
            └─→ process_table() [Line 367]
                ├─→ Capture screenshot [Line 237]
                ├─→ Extract game state [Line 253]
                ├─→ Update tracker [Line 277]
                ├─→ Make decision [Line 321]
                └─→ Execute click [Line 328]
```

---

## Key Components Initialized

1. **PageMonitor** - Monitors page for refreshes
2. **SessionManager** - Manages session data
3. **CacheManager** - Manages caching and JSON writing
4. **ResourceMonitor** - Monitors CPU/memory usage
5. **MultiTableManager** - Orchestrates all tables
6. **TableTracker** - Tracks state for each table
7. **ScreenshotScheduler** - Schedules screenshot captures
8. **ImageExtractor** - Extracts game state from screenshots
9. **ErrorRecovery** - Handles errors and recovery

---

## Continuous Loop

After initialization, the automation runs in a continuous loop:

1. **Check for page refresh** (every iteration)
2. **Process all tables in parallel** (screenshot → extract → decide → click)
3. **Sleep** (dynamic interval based on table states)
4. **Repeat**

The loop continues until `_is_running` is set to `False` (when user clicks "Stop Automation").
