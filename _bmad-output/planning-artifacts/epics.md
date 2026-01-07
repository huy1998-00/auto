---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: ["_bmad-output/analysis/brainstorming-session-2026-01-05-215146.md"]
lastUpdated: 2026-01-05
implementationStatus: 'in-progress'
---

# Mini-Game Website Automation & Pattern Tracking Tool - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Mini-Game Website Automation & Pattern Tracking Tool, decomposing the requirements from the brainstorming session and technical architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: The system must capture screenshots of specific game table regions using Playwright browser automation
FR2: The system must extract timer values from the orange countdown box using OpenCV template matching
FR3: The system must extract blue and red team scores from their respective display boxes using OpenCV template matching
FR4: The system must track round history per table (last 3 rounds encoded as B/P)
FR5: The system must implement a 3-round learning phase per table before making automated decisions
FR6: The system must match the last 3 rounds against user-defined patterns in format `BBP-P;BPB-B` (semicolon-separated)
FR7: The system must make click decisions based on pattern matches (B = Red team, P = Blue team)
FR8: The system must only click when timer value is greater than 6
FR9: The system must execute clicks in two phases: (1) choose team (blue/red button), (2) confirm (✓ tick) or cancel (✗ tick), accounting for canvas transform (17px offset)
FR10: The system must detect new rounds by monitoring timer reset (jump from low to high) and score changes
FR11: The system must detect winner by comparing score changes after timer reaches 0
FR12: The system must support up to 6 tables running in parallel
FR13: The system must create date-based session folders (`YYYY-MM-DD_HH-MM-SS`) on tool startup
FR14: The system must save round data to per-table JSON files (table_1.json through table_6.json) after each round
FR15: The system must maintain in-memory cache of all table data and flush to JSON files every round
FR16: The system must provide a desktop UI (Tkinter/PyQt) for monitoring and control
FR17: The system must display real-time status for all tables (timer, last 3 rounds, pattern match, decision, status)
FR18: The system must provide pattern editor UI with validation for pattern format
FR19: The system must provide history viewer showing last 20-50 rounds per table with success/failure indicators
FR20: The system must provide global start/stop controls for all tables
FR21: The system must provide individual pause/resume controls per table
FR22: The system must monitor yellow scoreboard section
FR23: The system must stop automation when target score is reached
FR24: The system must use adaptive screenshot frequency (200ms when timer > 6, 100ms when timer ≤ 6)
FR25: The system must detect page refreshes and auto-resume after reload
FR26: The system must implement retry logic with exponential backoff (3 attempts: 1s, 2s, 4s) for failed screenshots
FR27: The system must implement template matching fallback to OCR if OpenCV fails 3 times
FR28: The system must lock browser window to fixed size and validate canvas position periodically
FR29: The system must detect stuck states (3 consecutive timeouts) and pause affected table
FR30: The system must implement thread-safe JSON file writing for parallel table processing
FR31: The system must provide resource monitoring (CPU/memory) in UI
FR32: The system must auto-throttle screenshot frequency if CPU usage exceeds 80%
FR33: The system must implement license key validation system (Phase 4)

### NonFunctional Requirements

NFR1: The system must process all 6 tables simultaneously using parallel processing (threading/asyncio)
NFR2: The system must maintain screenshot capture latency under 500ms for normal monitoring
NFR3: The system must maintain screenshot capture latency under 200ms when timer > 6
NFR4: The system must maintain screenshot capture latency under 100ms when timer ≤ 6
NFR5: The system must handle a single Playwright browser instance displaying all 6 tables on one page
NFR6: The system must recover gracefully from page refreshes without losing round history
NFR7: The system must handle network lag and slow page loads with timeout-based retry (5 second timeout)
NFR8: The system must provide thread-safe operations for all shared data structures
NFR9: The system must update UI every 500ms for real-time monitoring
NFR10: The system must validate pattern format using regex: `^[BP]{3}-[BP](;[BP]{3}-[BP])*$`
NFR11: The system must persist all round data to JSON files with no data loss
NFR12: The system must support unlimited round history writing (continuous writing until tool closes)
NFR13: The system must implement file locking for thread-safe JSON writes
NFR14: The system must provide error logging with screenshots for debugging template matching failures
NFR15: The system must implement anti-bot measures (random delays 50-200ms, human-like timing variations)
NFR16: The system must validate license keys on startup and block tool if invalid (Phase 4)
NFR17: The system must support offline license validation (no internet required) (Phase 4)

### Additional Requirements

- **Technology Stack:**
  - Browser Automation: Playwright (Python)
  - Image Processing: OpenCV + PIL
  - OCR Fallback: Tesseract (pytesseract) or EasyOCR
  - UI Framework: Tkinter (built-in) or PyQt5/PySide6 for advanced features
  - Data Storage: JSON files (Python json module)
  - Threading: Python threading or asyncio

- **Data Storage Architecture:**
  - Date-based folder structure: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
  - Per-table JSON files: `table_1.json` through `table_6.json`
  - Session config JSON: `session_config.json` with global settings
  - Continuous writing: Save every round until tool closes
  - In-memory cache: Load all tables on startup, update cache each round, flush to JSON

- **Game Mechanics:**
  - Two teams: Red (B) and Blue (P)
  - Countdown timer: 15 or 25 seconds displayed in orange box
  - **Timer counts DOWN:** Starts at 15 or 25, counts down: 15 → 14 → 13 → ... → 1 → 0
  - When timer reaches 0, round ends and timer resets to 15 or 25 (new round starts)
  - Clickable only when timer > 6 (values 7-25 are clickable)
  - When timer ≤ 6 (values 6, 5, 4, 3, 2, 1, 0), it's countdown phase, not clickable
  - **Two-phase clicking process:**
    - Phase 1: Choose team (click blue or red button)
    - Phase 2: Confirm (click ✓ tick) or Cancel (click ✗ tick)
    - Delay between phases: 50-100ms (wait for confirmation UI to appear)
  - Pattern format: `[last 3 rounds]-[decision]` (e.g., "BBP-P")
  - Multiple patterns: Semicolon-separated (e.g., "BBP-P;BPB-B;BBB-P")

- **Error Handling Strategy:**
  - Try → Retry (3x) → Fallback → Alert User → Pause
  - Page refresh detection: Monitor URL/DOM, pause, wait for reload, auto-resume
  - Window locking: Fixed size (e.g., 1920x1080), disable resizing
  - Canvas validation: Validate position every 10-20 rounds

- **Performance Requirements:**
  - Maximum 6 tables (hard limit)
  - Single Playwright browser instance with all 6 tables displayed on one page
  - **Region-only screenshots:** Individual screenshots taken directly for each table's region (not full page)
  - Inactive/paused tables are skipped (no screenshot taken)
  - Table regions identified by coordinates (x, y, width, height) for direct screenshot capture
  - Two-phase clicking: (1) choose team button, (2) confirm (✓) or cancel (✗) button
  - Sequential clicks with 10-20ms delay between clicks within a table's two-phase sequence
  - Delay between Phase 1 and Phase 2: 50-100ms (wait for confirmation UI to appear)
  - Sequential clicks with 10-20ms delay between different tables' click sequences
  - Resource monitoring: Show CPU/memory usage in UI
  - Auto-throttling: Reduce screenshot frequency if CPU > 80%

- **Licensing System (Phase 4):**
  - Simple license key validation: Check if key exists in valid keys list/file
  - Offline validation: No internet required, validates against local valid keys
  - Manual license management: Administrator can add/delete keys manually
  - Validation: Check on startup, block tool if key is invalid or not found
  - No automated payment processing or billing integration

### FR Coverage Map

FR1: Epic 1 - Screenshot capture using Playwright
FR2: Epic 1 - Timer extraction using OpenCV template matching
FR3: Epic 1 - Score extraction using OpenCV template matching
FR4: Epic 1 - Round history tracking per table
FR5: Epic 1 - 3-round learning phase implementation
FR6: Epic 1 - Pattern matching against user-defined patterns
FR7: Epic 1 - Click decision making based on pattern matches
FR8: Epic 1 - Timer-based click validation (> 6)
FR9: Epic 1 - Two-phase click execution (choose team, then confirm/cancel) with canvas transform offset
FR10: Epic 1 - New round detection via timer reset and score changes
FR11: Epic 1 - Winner detection by comparing score changes
FR12: Epic 2 - Multi-table parallel processing (up to 6 tables)
FR13: Epic 3 - Date-based session folder creation
FR14: Epic 3 - Per-table JSON file storage
FR15: Epic 3 - In-memory cache with JSON flushing
FR16: Epic 4 - Desktop UI framework (Tkinter/PyQt)
FR17: Epic 4 - Real-time status display for all tables
FR18: Epic 4 - Pattern editor UI with validation
FR19: Epic 4 - History viewer with success/failure indicators
FR20: Epic 4 - Global start/stop controls
FR21: Epic 4 - Individual pause/resume controls per table
FR22: Epic 4 - Yellow scoreboard monitoring
FR23: Epic 4 - Target score stop functionality
FR24: Epic 1 - Adaptive screenshot frequency based on timer
FR25: Epic 5 - Page refresh detection and auto-resume
FR26: Epic 5 - Retry logic with exponential backoff
FR27: Epic 5 - Template matching fallback to OCR
FR28: Epic 5 - Browser window locking and canvas validation
FR29: Epic 5 - Stuck state detection and table pausing
FR30: Epic 2 - Thread-safe JSON file writing
FR31: Epic 4 - Resource monitoring (CPU/memory) in UI
FR32: Epic 4 - Auto-throttling based on CPU usage
FR33: Epic 6 - License key validation system (Phase 4)

## Epic List

### Epic 1: Single Table Automation
Enable users to automate one game table with pattern-based decision making, including screenshot capture, game state extraction, pattern matching, and automated clicking.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR11, FR24

**User Outcome:** Users can automate a single game table that observes rounds, learns patterns, and makes automated click decisions based on user-defined pattern rules.

**Implementation Notes:**
- Foundation epic that enables all other automation features
- Uses Playwright for browser automation
- **Table region configuration:** Manual configuration during development, fixed positions in production
- **Region-only screenshots:** Screenshots taken directly for each table's region using coordinates (not full page)
- OpenCV template matching for timer/score extraction per table region
- Pattern format: `BBP-P;BPB-B` (semicolon-separated)
- 3-round learning phase before making decisions (per table)
- Adaptive screenshot frequency: Multiple strategies available (see Story 1.13)
- Button coordinates are relative to table region, not absolute to page
- Two-phase clicking: (1) choose team button, (2) confirm (✓) or cancel (✗) button

**Note:** Epic 1 includes table region configuration (Story 1.2) to support multi-table architecture from the start. Screenshots are taken directly for each table's region, not from a full page screenshot.

### Epic 2: Multi-Table Parallel Processing
Enable users to run up to 6 game tables simultaneously in parallel, maximizing automation efficiency and throughput.

**FRs covered:** FR12, FR30

**User Outcome:** Users can run multiple game tables at the same time, each operating independently with its own pattern matching and decision logic.

**Implementation Notes:**
- Builds upon Epic 1 (Single Table Automation)
- All 6 tables displayed on the same page in a single browser instance
- **Region-only screenshots:** Individual screenshots taken directly for each table's region using coordinates
- Each table has its own state tracker and pattern matcher
- Parallel processing of table analysis from individual region screenshots
- Inactive/paused tables are skipped (no screenshot taken, saving resources)
- Thread-safe JSON file writing for concurrent data persistence

### Epic 3: Game History & Data Persistence
Enable users to track and review their game history with persistent data storage across sessions.

**FRs covered:** FR13, FR14, FR15

**User Outcome:** Users can view their complete game history, analyze pattern performance, and have all data automatically saved and organized by session.

**Implementation Notes:**
- Date-based folder structure: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- Per-table JSON files (table_1.json through table_6.json)
- In-memory cache for fast access, flushed to JSON every round
- Continuous writing until tool closes
- Works with both single and multi-table scenarios

### Epic 4: Desktop Control Interface
Enable users to monitor and control automation through a desktop user interface with real-time status updates, pattern editing, and history viewing.

**FRs covered:** FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR31, FR32

**User Outcome:** Users can monitor all tables in real-time, edit patterns, view history, start/stop automation, and control individual tables through an intuitive desktop interface.

**Implementation Notes:**
- Desktop UI using Tkinter (built-in) or PyQt5/PySide6 for advanced features
- Real-time updates every 500ms
- Pattern editor with format validation (regex: `^[BP]{3}-[BP](;[BP]{3}-[BP])*$`)
- History viewer showing last 20-50 rounds with success/failure indicators
- Global and individual table controls
- Resource monitoring (CPU/memory) with auto-throttling
- Scoreboard monitoring and target score stop functionality

### Epic 5: Error Recovery & System Resilience
Enable the system to handle failures gracefully and recover automatically from various error conditions without losing data or requiring manual intervention.

**FRs covered:** FR25, FR26, FR27, FR28, FR29

**User Outcome:** Users experience a robust system that automatically handles page refreshes, network issues, template matching failures, and stuck states without losing progress or requiring manual recovery.

**Implementation Notes:**
- Multi-layer error handling strategy: Try → Retry (3x) → Fallback → Alert User → Pause
- Page refresh detection with auto-resume after reload
- Retry logic with exponential backoff (1s, 2s, 4s delays)
- Template matching fallback to OCR if OpenCV fails 3 times
- Browser window locking (fixed size) and periodic canvas position validation
- Stuck state detection (3 consecutive timeouts) with automatic table pausing
- Error logging with screenshots for debugging

### Epic 6: License Key Validation (Phase 4)
Enable simple license key validation to control tool access. License keys are validated on startup, and manual license management allows deletion if payment is not received.

**FRs covered:** FR33

**User Outcome:** Tool access is controlled through license key validation. Valid keys allow tool usage. Invalid or expired keys block access. License management is manual (keys can be deleted if payment not received).

**Implementation Notes:**
- Simple license key validation system
- License key file or configuration-based validation
- Validation on tool startup
- Blocks tool if license is invalid or expired
- Manual license management (admin can delete/revoke keys)
- No automated payment processing or billing integration
- Implementation deferred to Phase 4 (after core tool is stable)

---

## Epic 1: Single Table Automation

Enable users to automate one game table with pattern-based decision making, including screenshot capture, game state extraction, pattern matching, and automated clicking.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR9, FR10, FR11, FR24

### Story 1.1: Browser Automation Setup and Region Screenshot Capture

As a user,
I want the system to open a browser and capture screenshots of individual table regions,
So that the system can analyze each table's game state efficiently.

**Acceptance Criteria:**

**Given** a game URL is provided
**When** the automation system starts
**Then** Playwright opens a Chromium browser instance with a fixed window size (1920x1080)
**And** the browser navigates to the game URL
**And** the system waits for the canvas element (`#layaCanvas`) to load
**And** the system can capture screenshots of specific regions using coordinates

**Given** the browser is open and game is loaded
**When** a screenshot is requested for a specific table region
**Then** the system captures a screenshot of only that table's region using stored coordinates (x, y, width, height)
**And** the screenshot is captured directly from the canvas at the specified region
**And** the screenshot includes that table's game elements (timer, scores, buttons, scoreboard)
**And** screenshots are captured as PIL Image objects for processing
**And** only active tables have screenshots taken (inactive/paused tables are skipped)

### Story 1.2: Table Region Configuration and Coordinate Management

As a user,
I want the system to manage table region coordinates,
So that screenshots can be taken directly for each table region.

**Acceptance Criteria:**

**Given** the system needs to configure table regions
**When** table region setup is requested
**Then** the system loads table region coordinates (x, y, width, height) from configuration
**And** during development, coordinates are manually configured and stored in config file
**And** in production, coordinates use fixed positions from configuration
**And** coordinates are stored per table_id for direct region screenshot capture

**Given** table region coordinates are configured
**When** a table is added
**Then** the system validates coordinates are within canvas bounds
**And** the system stores coordinates for that table_id
**And** coordinates are used for all subsequent region screenshots for that table
**And** the system can take screenshots directly at these coordinates without full page capture

### Story 1.3: Timer Extraction Using OpenCV Template Matching

As a user,
I want the system to extract the countdown timer value from the orange box for a specific table,
So that the system knows when clicks are allowed and when rounds end.

**Acceptance Criteria:**

**Given** a table region screenshot is captured for a specific table
**When** timer extraction is requested for that table
**Then** the system crops the orange timer region from the table region image
**And** the system uses OpenCV template matching to identify the timer number (0-25)
**And** the system returns the timer value as an integer for that table
**And** template matching handles numbers 0-9 correctly
**And** the system accounts for timer display variations (15 or 25 second rounds)

**Given** template matching fails to identify the timer
**When** 3 consecutive failures occur for a table
**Then** the system falls back to OCR (Tesseract) for timer extraction for that table only
**And** the failure is logged with table_id and screenshot for debugging
**And** other tables continue processing normally

### Story 1.4: Score Extraction Using OpenCV Template Matching

As a user,
I want the system to extract blue and red team scores from their display boxes for a specific table,
So that the system can detect winners and track game progress.

**Acceptance Criteria:**

**Given** a table region screenshot is captured for a specific table
**When** score extraction is requested for that table
**Then** the system crops the blue team score region from the table region image
**And** the system crops the red team score region from the table region image
**And** the system uses OpenCV template matching to extract both scores
**And** the system returns blue_score and red_score as integers for that table
**And** template matching correctly identifies score values (0-999+)

**Given** template matching fails for scores
**When** 3 consecutive failures occur for a table
**Then** the system falls back to OCR (Tesseract) for score extraction for that table only
**And** the failure is logged with table_id and screenshot for debugging
**And** other tables continue processing normally

### Story 1.5: Round History Tracking and State Management

As a user,
I want the system to track round history per table,
So that the system can match patterns against the last 3 rounds.

**Acceptance Criteria:**

**Given** a table is being tracked
**When** a round completes and a winner is detected
**Then** the system appends the winner to the round history (B for Red, P for Blue)
**And** the system maintains the last 3 rounds in memory
**And** the system can return the last 3 rounds as a string (e.g., "BBP")
**And** round history persists across automation cycles

**Given** a table has fewer than 3 rounds
**When** last 3 rounds are requested
**Then** the system returns None or empty string
**And** the system tracks the number of rounds watched

### Story 1.6: Learning Phase Implementation

As a user,
I want the system to observe the first 3 rounds before making decisions,
So that the system has enough history to match patterns.

**Acceptance Criteria:**

**Given** a new table is added to automation
**When** automation starts
**Then** the system sets learning_phase = True
**And** the system tracks rounds_watched counter starting at 0
**And** the system does not make click decisions during learning phase

**Given** a table is in learning phase
**When** a round completes
**Then** the system increments rounds_watched
**And** if rounds_watched >= 3, the system sets learning_phase = False
**And** the system transitions to active decision-making mode

### Story 1.7: Pattern Matching Algorithm Implementation

As a user,
I want the system to match the last 3 rounds against my defined patterns,
So that the system can make click decisions based on pattern rules.

**Acceptance Criteria:**

**Given** user-defined patterns in format `BBP-P;BPB-B;BBB-P`
**When** pattern matching is initialized
**Then** the system parses the pattern string by semicolon separator
**And** the system stores each pattern as {history: "BBP", decision: "P"}
**And** the system validates pattern format using regex: `^[BP]{3}-[BP](;[BP]{3}-[BP])*$`

**Given** a pattern matcher with patterns and last 3 rounds are available
**When** match() is called with last_3_rounds (e.g., "BBP")
**Then** the system checks each pattern in order
**And** if a match is found, the system returns the decision ("P" or "B")
**And** if no match is found, the system returns None
**And** first matching pattern wins (priority-based)

### Story 1.8: Click Decision Logic

As a user,
I want the system to make click decisions based on pattern matches,
So that the system automatically chooses the correct team to bet on.

**Acceptance Criteria:**

**Given** a table is not in learning phase and has pattern matcher configured
**When** get_decision() is called with last_3_rounds
**Then** the system checks if learning_phase is False
**And** the system calls pattern_matcher.match() with last_3_rounds
**And** if match returns "P", the system returns "blue" (click blue button)
**And** if match returns "B", the system returns "red" (click red button)
**And** if no match, the system returns None (no click)

**Given** a table is in learning phase
**When** get_decision() is called
**Then** the system returns False, None (should not click)

### Story 1.9: Timer-Based Click Validation

As a user,
I want the system to only click when the timer is greater than 6,
So that clicks are not wasted during the countdown phase.

**Acceptance Criteria:**

**Given** a click decision has been made (blue or red)
**When** the system checks if clicking is allowed
**Then** the system reads the current timer value (which counts DOWN from 15/25 to 0)
**And** if timer > 6 (values: 7, 8, 9, 10, 11, 12, 13, 14, 15, 25), the system allows the click
**And** if timer ≤ 6 (values: 6, 5, 4, 3, 2, 1, 0), the system waits for the next round
**And** the system does not attempt clicks during countdown phase (timer ≤ 6)
**And** the system recognizes that timer counts DOWN, so when timer = 6, it will soon reach 0

### Story 1.10: Two-Phase Click Execution with Canvas Transform Offset

As a user,
I want the system to execute clicks in two phases (choose team, then confirm/cancel) at the correct coordinates for a specific table,
So that clicks register on the game buttons accurately and complete the betting process.

**Acceptance Criteria:**

**Given** a click decision is made (blue or red) and timer > 6 for a specific table
**When** click execution is requested
**Then** the system executes Phase 1: Choose Team
**And** the system gets the canvas bounding box
**And** the system gets the table region coordinates (x, y) for that table
**And** button coordinates are relative to the table region
**And** the system calculates team button coordinates:
  - absolute_x = canvas_box['x'] + table_region['x'] + button_x + 17 (canvas transform offset)
  - absolute_y = canvas_box['y'] + table_region['y'] + button_y
**And** the system executes mouse.click() at the team button coordinates (blue or red)
**And** the system waits for confirmation UI to appear (brief delay, e.g., 50-100ms)

**Given** Phase 1 (choose team) is completed for a table
**When** confirmation UI appears
**Then** the system executes Phase 2: Confirm or Cancel
**And** the system calculates confirm button (✓ tick) coordinates relative to table region
**And** the system calculates cancel button (✗ tick) coordinates relative to table region
**And** the system clicks the confirm button (✓ tick) to finalize the bet
**And** the system does NOT click cancel (✗ tick) unless explicitly configured to cancel
**And** both clicks are logged with timestamp and table_id

**Given** a two-phase click sequence is executed for a table
**When** both phases complete
**Then** the click sequence is logged as complete with timestamp and table_id
**And** the system tracks that a bet was placed for that table
**And** clicks for different tables can execute independently (each table has its own two-phase sequence)

**Given** button coordinates (relative to table region) are provided for a table
**When** click_blue_button() or click_red_button() is called
**Then** the system executes Phase 1: clicks the team button (blue or red)
**And** the system executes Phase 2: clicks the confirm button (✓ tick)
**And** both clicks are logged with timestamp and table_id
**And** clicks for different tables can execute independently

### Story 1.11: New Round Detection

As a user,
I want the system to detect when a new round starts for a specific table,
So that the system can track rounds accurately and detect winners per table.

**Acceptance Criteria:**

**Given** the system is monitoring a specific table (with its own timer and scores)
**When** a new round begins for that table
**Then** the system detects timer reset for that table (timer jumps from 0 or low value 1-6 back to high value 15 or 25)
**And** the timer counts DOWN from 15/25 → 14 → 13 → ... → 1 → 0
**And** the system confirms with score change for that table (blue or red score increases)
**And** the system tracks timer direction per table (should always count DOWN, never up)
**And** the system logs the new round start with timestamp and table_id

**Given** a table's timer counts down and reaches 0
**When** score changes are detected for that table
**Then** the system identifies the winner for that table (team whose score increased)
**And** the system records the round as complete for that table
**And** the timer resets to 15 or 25 (starting new round)
**And** other tables continue their own round cycles independently

### Story 1.12: Winner Detection

As a user,
I want the system to detect the winner of each round for a specific table,
So that the system can update round history and track pattern accuracy per table.

**Acceptance Criteria:**

**Given** a round completes for a specific table (that table's timer reaches 0)
**When** winner detection is requested for that table
**Then** the system compares current scores with previous scores for that table
**And** if blue_score > previous_blue_score, the system returns "P" (Blue team won) for that table
**And** if red_score > previous_red_score, the system returns "B" (Red team won) for that table
**And** if no score change, the system returns None (round not complete yet for that table)

**Given** a winner is detected for a table
**When** the round result is processed
**Then** the system adds the winner to that table's round history
**And** the system updates statistics for that table (total rounds, correct/incorrect decisions)
**And** the system logs the round with decision made, pattern matched, and table_id
**And** other tables' winner detection continues independently

### Story 1.13: Adaptive Screenshot Frequency

As a user,
I want the system to adjust screenshot frequency based on game phase across all tables,
So that the system captures critical moments without wasting resources.

**Acceptance Criteria:**

**Given** the system is monitoring multiple tables (up to 6) on the same page
**When** screenshot frequency is determined
**Then** the system evaluates all active tables' timer values
**And** the system selects screenshot frequency based on the selected strategy (see options below)

**Screenshot Frequency Strategy Options:**

**Option A: Fastest Timer Strategy (Recommended)**
- If ANY table has timer ≤ 6 (countdown phase: timer counts down from 6 to 0), use 100ms interval (catch round completion when timer reaches 0)
- Otherwise, if ANY table has timer > 6 (clickable phase: timer counts down from 15/25 to 7), use 200ms interval
- If all tables are in result phase (timer = 0, waiting for reset), use 1 second interval

**Option B: Slowest Timer Strategy**
- Use the SLOWEST timer value across all tables (timer counts DOWN, so slowest = highest number)
- If slowest timer ≤ 6 (countdown phase), use 100ms (to catch timer = 0)
- If slowest timer > 6 (clickable phase), use 200ms
- If all in result phase (timer = 0), use 1 second

**Option C: Fixed Frequency Strategy**
- Use fixed 200ms interval regardless of table states
- Simpler but less optimal for catching round completions

**Option D: Majority Rule Strategy**
- Count tables in each phase (clickable, countdown, result)
- Use frequency based on majority phase
- If majority in countdown (≤6), use 100ms
- If majority in clickable (>6), use 200ms

**Option E: Per-Table Independent Frequency (Advanced)**
- Each table uses its own frequency based on its timer
- Table with timer ≤ 6: 100ms
- Table with timer > 6: 200ms
- Table in result phase: 1 second
- Screenshots taken independently per table at their own intervals
- More complex but most efficient

**Implementation Note:** User can configure which strategy to use in settings. Default: Option A (Fastest Timer). With region-only screenshots, Option E becomes more feasible.

**Given** the selected strategy is applied
**When** screenshots are taken
**Then** the system uses the calculated frequency
**And** region screenshots are taken for each active table
**And** inactive/paused tables are skipped (no screenshot taken)
**And** the system optimizes resource usage while capturing critical moments

---

## Epic 2: Multi-Table Parallel Processing

Enable users to run up to 6 game tables simultaneously in parallel, maximizing automation efficiency and throughput.

**FRs covered:** FR12, FR30

### Story 2.1: Multi-Table Manager Implementation

As a user,
I want the system to manage multiple game tables simultaneously,
So that I can automate multiple tables at once for maximum efficiency.

**Acceptance Criteria:**

**Given** the system is initialized
**When** add_table() is called with table_id and table_region_coordinates
**Then** the system creates a TableTracker instance for the table
**And** the system stores table region coordinates (x, y, width, height) for extracting table data from screenshot
**And** the system stores the tracker in the tables dictionary
**And** the system supports up to 6 tables maximum (hard limit)
**And** all 6 tables are displayed on the same page in a single browser instance

**Given** a single browser instance is open with the game page
**When** tables are added
**Then** the system uses the same browser instance for all tables
**And** the system identifies each table by its region coordinates on the page
**And** each table has its own TableTracker with independent state

**Given** 6 tables are already active
**When** add_table() is called for a 7th table
**Then** the system rejects the request with an error message
**And** the system maintains the 6-table limit

### Story 2.2: Multi-Table Processing with Region Screenshots

As a user,
I want all tables to process simultaneously using individual region screenshots,
So that automation runs efficiently across all active tables on the same page.

**Acceptance Criteria:**

**Given** multiple tables are added (up to 6) on the same page
**When** process_all_tables() is called
**Then** the system captures individual region screenshots for each active table using stored coordinates
**And** inactive/paused tables are skipped (no screenshot taken)
**And** the system processes all table region screenshots in parallel using threading or asyncio
**And** each table region screenshot is analyzed independently (timer, scores, state)
**And** all tables execute analysis → click decision cycles simultaneously
**And** no table blocks another table's processing

**Given** region screenshots are captured for active tables
**When** table processing occurs
**Then** each table's timer and scores are extracted from its own region screenshot
**And** each table maintains independent state (round history, learning phase, patterns)
**And** region screenshots are smaller files (faster processing, less memory)

**Given** tables are processing in parallel
**When** a table's region screenshot capture fails
**Then** the error is isolated to that table
**And** other tables continue processing normally with their own region screenshots
**And** the error is logged with table_id for debugging
**And** the failed table can retry independently

### Story 2.3: Thread-Safe JSON File Writing

As a user,
I want round data from all tables to be saved safely,
So that no data is lost or corrupted when multiple tables write simultaneously.

**Acceptance Criteria:**

**Given** multiple tables are writing round data in parallel
**When** a round completes and data needs to be saved
**Then** the system uses file locking for thread-safe JSON writes
**And** each table writes to its own JSON file (table_1.json through table_6.json)
**And** no race conditions occur during file writes
**And** all round data is persisted correctly

**Given** file locking is implemented
**When** two tables try to write simultaneously
**Then** one table waits for the lock to be released
**And** writes complete sequentially without data corruption
**And** all data is saved successfully

---

## Epic 3: Game History & Data Persistence

Enable users to track and review their game history with persistent data storage across sessions.

**FRs covered:** FR13, FR14, FR15

### Story 3.1: Date-Based Session Folder Creation

As a user,
I want my game sessions to be organized by date and time,
So that I can easily find and review historical game data.

**Acceptance Criteria:**

**Given** the tool starts
**When** a new session begins
**Then** the system creates a session folder: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
**And** the folder name uses the session start timestamp
**And** the folder is created if it doesn't exist
**And** the system stores the session folder path for later use

**Given** a session folder exists
**When** the tool starts
**Then** the system can identify the current session folder
**And** the system can create new session folders for new sessions

### Story 3.2: Per-Table JSON File Structure

As a user,
I want each table's data stored in separate JSON files,
So that I can easily access and analyze data for individual tables.

**Acceptance Criteria:**

**Given** a table is activated in a session
**When** the table starts automation
**Then** the system creates a JSON file: `table_{table_id}.json` in the session folder
**And** the JSON file follows the schema:
  - table_id: string
  - session_start: ISO timestamp
  - patterns: pattern string
  - rounds: array of round objects
  - statistics: object with total_rounds, correct_decisions, accuracy

**Given** a round completes
**When** round data is saved
**Then** the system appends the round object to the rounds array
**And** the round object includes: round_number, timestamp, timer_start, blue_score, red_score, winner, decision_made, pattern_matched, result
**And** the JSON file is updated with the new round data

### Story 3.3: Session Config JSON Creation

As a user,
I want global session settings stored separately,
So that I can track session-level configuration and active tables.

**Acceptance Criteria:**

**Given** a session starts
**When** session_config.json is created
**Then** the file includes:
  - session_start: ISO timestamp
  - session_end: null (until session closes)
  - tables_active: array of active table IDs
  - global_patterns: default pattern string
  - settings: object with max_tables, screenshot_interval_fast, screenshot_interval_normal

**Given** tables are added or removed
**When** session state changes
**Then** the system updates tables_active array in session_config.json
**And** the system persists the updated configuration

### Story 3.4: In-Memory Cache System

As a user,
I want fast access to table data during automation,
So that the UI can display real-time information without file I/O delays.

**Acceptance Criteria:**

**Given** the tool starts
**When** tables are loaded
**Then** the system loads all table JSON files into memory
**And** the system maintains an in-memory cache of all table data
**And** the cache is updated after each round completes

**Given** a round completes
**When** data needs to be saved
**Then** the system updates the in-memory cache first
**And** the system flushes the cache to JSON files every round
**And** the cache and JSON files remain synchronized
**And** UI reads from cache for fast display updates

### Story 3.5: Continuous Writing Until Tool Closes

As a user,
I want all round data saved continuously,
So that no data is lost even if the tool crashes.

**Acceptance Criteria:**

**Given** automation is running
**When** each round completes
**Then** the system immediately writes round data to JSON file
**And** the system continues writing every round until tool closes
**And** there is no limit on the number of rounds written
**And** data persists across tool restarts

**Given** the tool is closing
**When** shutdown is initiated
**Then** the system flushes all remaining cache data to JSON files
**And** the system updates session_config.json with session_end timestamp
**And** all data is safely persisted before exit

---

## Epic 4: Desktop Control Interface

Enable users to monitor and control automation through a desktop user interface with real-time status updates, pattern editing, and history viewing.

**FRs covered:** FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR31, FR32

### Story 4.1: Desktop UI Framework Setup

As a user,
I want a desktop application interface,
So that I can interact with the automation tool through a graphical interface.

**Acceptance Criteria:**

**Given** the tool starts
**When** the UI is initialized
**Then** the system creates a main window using Tkinter (or PyQt5/PySide6)
**And** the window has a title: "Game Automation Tool"
**And** the window is resizable and has appropriate default size
**And** the UI framework is ready for component addition

**Given** the UI is running
**When** the user interacts with the interface
**Then** the UI responds to user actions
**And** the UI can be closed gracefully

### Story 4.2: Real-Time Table Status Display

As a user,
I want to see real-time status for all tables,
So that I can monitor automation progress at a glance.

**Acceptance Criteria:**

**Given** tables are active
**When** the UI displays table status
**Then** each table shows: table_id, status (🟢 Active, 🟡 Learning, 🔴 Paused, ⚪ Stuck), timer value, last 3 rounds, pattern match, decision
**And** the UI updates every 500ms for real-time monitoring
**And** status indicators use color coding for quick visual feedback
**And** all 6 table slots are displayed (even if not all are active)

**Given** a table is in learning phase
**When** status is displayed
**Then** the UI shows "Learning" status with rounds_watched count
**And** the UI indicates when learning phase will complete

### Story 4.3: Pattern Editor UI with Validation

As a user,
I want to enter and edit patterns through the UI,
So that I can configure automation rules easily.

**Acceptance Criteria:**

**Given** the UI is displayed
**When** the user opens the pattern editor
**Then** the UI provides a text input field for pattern entry
**And** the UI displays current patterns for the selected table
**And** the UI validates pattern format using regex: `^[BP]{3}-[BP](;[BP]{3}-[BP])*$`

**Given** a user enters a pattern
**When** the pattern is submitted
**Then** the system validates the format
**And** if valid, the pattern is saved to the table's pattern matcher
**And** if invalid, the UI displays an error message with format requirements
**And** the UI provides a "Test Pattern" button to validate format before saving

### Story 4.4: History Viewer with Success/Failure Indicators

As a user,
I want to view game history with visual indicators,
So that I can analyze pattern performance and decision accuracy.

**Acceptance Criteria:**

**Given** game history exists
**When** the user opens the history viewer
**Then** the UI displays the last 20-50 rounds per table
**And** each round shows: table_id, round_number, pattern_matched, decision_made, result, timestamp
**And** successful decisions show ✓ indicator
**And** failed decisions show ✗ indicator
**And** the UI allows filtering by table and date range

**Given** history is displayed
**When** the user scrolls through history
**Then** the UI loads additional rounds as needed
**And** the UI shows statistics: total_rounds, correct_decisions, accuracy percentage

### Story 4.5: Global Start/Stop Controls

As a user,
I want to start and stop all tables at once,
So that I can quickly control the entire automation system.

**Acceptance Criteria:**

**Given** the UI is displayed
**When** the user clicks "Start All"
**Then** the system starts automation for all active tables
**And** all tables begin processing simultaneously
**And** the UI updates status indicators to "Active"

**Given** automation is running
**When** the user clicks "Stop All"
**Then** the system stops automation for all tables
**And** all tables pause their processing
**And** the UI updates status indicators to "Paused"
**And** current round data is saved before stopping

### Story 4.6: Individual Table Pause/Resume Controls

As a user,
I want to control individual tables separately,
So that I can pause problematic tables while others continue.

**Acceptance Criteria:**

**Given** multiple tables are running
**When** the user clicks "Pause" for a specific table
**Then** only that table stops processing
**And** other tables continue running normally
**And** the UI updates that table's status to "Paused"
**And** the table's current state is preserved

**Given** a table is paused
**When** the user clicks "Resume" for that table
**Then** the table resumes processing from where it paused
**And** the UI updates status to "Active"
**And** the table continues with its existing round history

### Story 4.7: Scoreboard Monitoring and Target Score Stop

As a user,
I want the system to monitor the scoreboard and stop when target is reached,
So that automation stops automatically at my desired score.

**Acceptance Criteria:**

**Given** a target score is configured
**When** automation is running
**Then** the system monitors the yellow scoreboard section (global scoreboard shared across all tables on the page)
**And** the system tracks the current score from the global scoreboard
**And** when target score is reached, the system automatically stops automation
**And** the UI displays a notification that target score was reached

**Given** target score stop is enabled
**When** the score reaches the target
**Then** all tables stop processing (since scoreboard is global, all tables share the same target)
**And** final statistics are displayed
**And** session data is saved with completion status

### Story 4.8: Resource Monitoring Display

As a user,
I want to see system resource usage,
So that I can monitor if the system is running efficiently.

**Acceptance Criteria:**

**Given** the UI is displayed
**When** resource monitoring is active
**Then** the UI displays CPU usage percentage
**And** the UI displays memory usage
**And** the UI updates these metrics every 500ms
**And** the UI shows visual indicators (e.g., green/yellow/red) based on usage levels

**Given** CPU usage exceeds 80%
**When** auto-throttling is enabled
**Then** the system reduces screenshot frequency automatically
**And** the UI displays a notification about throttling
**And** the system returns to normal frequency when CPU usage drops

---

## Epic 5: Error Recovery & System Resilience

Enable the system to handle failures gracefully and recover automatically from various error conditions without losing data or requiring manual intervention.

**FRs covered:** FR25, FR26, FR27, FR28, FR29

### Story 5.1: Page Refresh Detection and Auto-Resume

As a user,
I want the system to detect page refreshes and resume automatically,
So that automation continues seamlessly after page reloads.

**Acceptance Criteria:**

**Given** automation is running with multiple tables on the same page
**When** a page refresh occurs
**Then** the system detects the refresh by monitoring page.url and page.is_closed()
**And** the system pauses automation for ALL tables (since they're on the same page)
**And** the system saves current state to JSON for ALL tables before refresh
**And** the system waits for the game to reload (canvas element available)
**And** the system auto-resumes automation for ALL tables after reload
**And** the system restores state from JSON for ALL tables after reload

**Given** a page refresh is detected
**When** auto-resume fails after 3 attempts
**Then** the system pauses ALL tables and alerts the user via UI
**And** the user can manually resume ALL tables via UI controls
**And** the system maintains table region coordinates after refresh (fixed positions)

### Story 5.2: Retry Logic with Exponential Backoff

As a user,
I want the system to retry failed operations automatically,
So that temporary network issues don't stop automation.

**Acceptance Criteria:**

**Given** a region screenshot capture fails for a specific table
**When** retry logic is triggered
**Then** the system retries up to 3 times for that table's region
**And** the system uses exponential backoff: 1s, 2s, 4s delays
**And** if all retries fail, the system triggers fallback mechanism for that table
**And** all failures are logged with timestamps and table_id
**And** other tables continue processing with their own region screenshots

**Given** network lag causes timeout for a region screenshot
**When** screenshot timeout occurs (5 seconds)
**Then** the system retries with exponential backoff for that table
**And** the system handles slow page loads gracefully
**And** if 3 consecutive timeouts occur for a table, the system detects stuck state for that table
**And** other tables are not affected

### Story 5.3: Template Matching Fallback to OCR

As a user,
I want the system to use OCR when template matching fails,
So that automation continues even if template matching has issues.

**Acceptance Criteria:**

**Given** OpenCV template matching fails 3 consecutive times
**When** fallback is triggered
**Then** the system attempts OCR (Tesseract or EasyOCR) for timer/score extraction
**And** the system logs the fallback with screenshot for debugging
**And** if OCR succeeds, automation continues normally
**And** if OCR also fails, the system alerts the user and pauses the table

**Given** template matching failures occur
**When** fallback to OCR is used
**Then** the system logs all failures with screenshots
**And** the system provides debugging information in error logs
**And** the user is notified via UI about the fallback usage

### Story 5.4: Browser Window Locking and Canvas Validation

As a user,
I want the browser window to stay fixed in size and position,
So that screenshot coordinates remain accurate.

**Acceptance Criteria:**

**Given** a browser instance is created
**When** the browser opens
**Then** the system locks window size to fixed dimensions (e.g., 1920x1080)
**And** the system disables window resizing in Playwright context
**And** the system stores reference canvas coordinates on startup

**Given** automation is running
**When** canvas validation is performed (every 10-20 rounds)
**Then** the system validates canvas position against reference coordinates
**And** if position drifts significantly (>5px), the system alerts the user
**And** the system can recalibrate coordinates if needed

### Story 5.5: Stuck State Detection and Automatic Pausing

As a user,
I want the system to detect when a table is stuck,
So that problematic tables don't waste resources indefinitely.

**Acceptance Criteria:**

**Given** automation is running with multiple tables
**When** a specific table's region screenshot capture fails 3 consecutive times
**Then** the system detects per-table stuck state for that specific table only
**And** the system automatically pauses only the affected table
**And** other tables continue processing normally with their own region screenshots
**And** the system alerts the user via UI with table_id and error details
**And** the system logs the stuck state with diagnostic information

**Given** automation is running with multiple tables
**When** a specific table's region analysis (timer/score extraction) fails 3 consecutive times (but screenshot succeeds)
**Then** the system detects per-table stuck state for that specific table only
**And** the system automatically pauses only the affected table
**And** other tables continue processing normally
**And** the system alerts the user via UI with table_id and error details
**And** the system logs the stuck state with diagnostic information

**Given** a table is in stuck state
**When** the user reviews the error
**Then** the user can manually resume the table via UI
**Or** the user can remove the table and add a new one
**And** the system provides error logs for debugging
**And** error isolation allows other tables to continue operating

---

## Epic 6: License Key Validation (Phase 4)

Enable simple license key validation to control tool access. License keys are validated on startup, and manual license management allows deletion if payment is not received.

**FRs covered:** FR33

### Story 6.1: License Key Validation on Startup

As a user,
I want the system to validate my license key on startup,
So that only authorized users can use the tool.

**Acceptance Criteria:**

**Given** the tool starts
**When** license validation is performed
**Then** the system checks for a valid license key (from file or configuration)
**And** the system validates the license key format and structure
**And** the system checks if the license key exists in the valid keys list
**And** if license is valid, the tool proceeds normally and allows usage
**And** if license is invalid or not found, the tool blocks startup with error message
**And** the error message instructs user to contact administrator for license key

**Given** a license key is provided
**When** validation occurs
**Then** the system can validate offline (no internet required)
**And** the system checks license key against a local valid keys list or file
**And** validation is fast and doesn't delay tool startup significantly

### Story 6.2: Manual License Management

As an administrator,
I want to manually manage license keys,
So that I can add valid keys and delete keys if payment is not received.

**Acceptance Criteria:**

**Given** license management access
**When** an administrator wants to add a license key
**Then** the system allows adding a new license key to the valid keys list/file
**And** the license key is stored securely (encrypted or in protected file)
**And** the new key becomes immediately valid for tool access

**Given** a user has not made payment
**When** an administrator wants to revoke access
**Then** the system allows deletion/removal of the license key from valid keys
**And** the deleted key becomes invalid immediately
**And** users with deleted keys cannot start the tool (will be blocked on next startup)
**And** license key management is manual (no automated payment processing)

**Given** license keys are managed
**When** keys are added or deleted
**Then** changes take effect on next tool startup
**And** the system maintains a log of license key changes (optional, for audit)

---

## Implementation Status Summary

**Status Legend:**
- ✅ **Implemented** - Code written and integrated
- 🧪 **Needs Testing** - Implemented but not yet verified through testing
- ⚠️ **Has Issues** - Implemented but has known bugs/problems
- ❌ **Not Started** - Not yet implemented

### ✅ Epic 1: Single Table Automation - IMPLEMENTED (Needs Testing)

**Status:** ✅ All stories implemented, 🧪 **NOT YET TESTED**

**Stories:**
- ✅ Story 1.1: Browser Automation Setup and Region Screenshot Capture
- ✅ Story 1.2: Table Region Configuration and Coordinate Management
- 🧪 Story 1.3: Timer Extraction Using OpenCV Template Matching
- 🧪 Story 1.4: Score Extraction Using OpenCV Template Matching
- 🧪 Story 1.5: Round History Tracking and State Management
- 🧪 Story 1.6: Learning Phase Implementation
- 🧪 Story 1.7: Pattern Matching Algorithm Implementation
- 🧪 Story 1.8: Click Decision Logic
- 🧪 Story 1.9: Timer-Based Click Validation
- 🧪 Story 1.10: Two-Phase Click Execution with Canvas Transform Offset
- 🧪 Story 1.11: New Round Detection
- 🧪 Story 1.12: Winner Detection
- 🧪 Story 1.13: Adaptive Screenshot Frequency

**Notes:** All core automation features implemented. Code written but functions not yet tested/verified.

---

### ✅ Epic 2: Multi-Table Parallel Processing - IMPLEMENTED (Needs Testing)

**Status:** ✅ All stories implemented, 🧪 **NOT YET TESTED**

**Stories:**
- 🧪 Story 2.1: Multi-Table Manager Implementation
- 🧪 Story 2.2: Multi-Table Processing with Region Screenshots
- 🧪 Story 2.3: Thread-Safe JSON File Writing

**Notes:** Parallel processing code implemented. Functions not yet tested/verified.

---

### ✅ Epic 3: Game History & Data Persistence - IMPLEMENTED (Needs Testing)

**Status:** ✅ All stories implemented, 🧪 **NOT YET TESTED**

**Stories:**
- 🧪 Story 3.1: Date-Based Session Folder Creation
- 🧪 Story 3.2: Per-Table JSON File Structure
- 🧪 Story 3.3: Session Config JSON Creation
- 🧪 Story 3.4: In-Memory Cache System
- 🧪 Story 3.5: Continuous Writing Until Tool Closes

**Notes:** Data persistence code implemented. Functions not yet tested/verified.

---

### ⚠️ Epic 4: Desktop Control Interface - IMPLEMENTED (Has Issues, Needs Testing)

**Status:** ✅ Code implemented, ⚠️ **HAS KNOWN ISSUES**, 🧪 **NOT YET TESTED**

**Stories:**
- ✅ Story 4.1: Desktop UI Framework Setup - **Setup complete, may need future changes**
- ✅ Story 4.2: Real-Time Table Status Display
- 🧪 Story 4.3: Pattern Editor UI with Validation
- 🧪 Story 4.4: History Viewer with Success/Failure Indicators
- 🧪 Story 4.5: Global Start/Stop Controls
- 🧪 Story 4.6: Individual Table Pause/Resume Controls
- 🧪 Story 4.7: Scoreboard Monitoring and Target Score Stop
- 🧪 Story 4.8: Resource Monitoring Display
- ⚠️ **Story 4.9: Visual Coordinate Picker** - **ISSUE: Overlay not appearing**


---

### ✅ Epic 5: Error Recovery & System Resilience - IMPLEMENTED (Needs Testing)

**Status:** ✅ All stories implemented, 🧪 **NOT YET TESTED**

**Stories:**
- 🧪 Story 5.1: Page Refresh Detection and Auto-Resume
- 🧪 Story 5.2: Retry Logic with Exponential Backoff
- 🧪 Story 5.3: Template Matching Fallback to OCR
- 🧪 Story 5.4: Browser Window Locking and Canvas Validation
- 🧪 Story 5.5: Stuck State Detection and Automatic Pausing

**Notes:** Error recovery code implemented. Functions not yet tested/verified.

---

### ❌ Epic 6: License Key Validation - NOT STARTED (0%)

**Status:** ❌ Deferred to Phase 4

**Stories:**
- ❌ Story 6.1: License Key Validation on Startup
- ❌ Story 6.2: Manual License Management

**Notes:** Licensing system deferred to Phase 4. Core automation features prioritized first.

---

## Overall Progress Summary

**Total Stories:** 42

**Implementation Status:**
- **Implemented:** 34 stories (81%)
- **Needs Testing:** 34 stories (81%) - All implemented features need testing
- **Has Issues:** 1 story (2%) - Coordinate picker overlay
- **Not Started:** 7 stories (17%) - Epic 6 (Phase 4) + coordinate picker fix

**Critical Blockers:**
1. Coordinate picker overlay visibility issue
2. Test coordinate picker debugging needed
3. Comprehensive testing not yet performed

**Next Actions:**

3. 🧪 Begin comprehensive testing of Epics 1-5
4. ✅ Complete Epic 1.1 and 1.2 (coordinate picker fixes)
5. ⏳ Begin Epic 6 (Phase 4 - Licensing)

**Testing Priority:**
1. Epic 1: Browser automation, screenshot capture, timer/score extraction, pattern matching, click execution
2. Epic 2: Multi-table parallel processing, thread safety
3. Epic 3: Data persistence, session management, JSON writing
4. Epic 4: UI features, coordinate picker (after fix), all controls
5. Epic 5: Error recovery, retry logic, OCR fallback
