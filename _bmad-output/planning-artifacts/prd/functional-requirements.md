# Functional Requirements

### Game State Capture and Analysis

**FR1:** The system must capture screenshots of specific game table regions using Playwright browser automation

**FR2:** The system must extract timer values from the orange countdown box using OpenCV template matching

**FR3:** The system must extract blue and red team scores from their respective display boxes using OpenCV template matching

**FR4:** The system must track round history per table (last 3 rounds encoded as B/P)

**FR5:** The system must implement a 3-round learning phase per table before making automated decisions

**FR6:** The system must match the last 3 rounds against user-defined patterns in format `BBP-P;BPB-B` (semicolon-separated)

**FR7:** The system must make click decisions based on pattern matches (B = Red team, P = Blue team)

**FR8:** The system must only click when timer value is greater than 6

**FR9:** The system must execute clicks in two phases: (1) choose team (blue/red button), (2) confirm (✓ tick) or cancel (✗ tick), accounting for canvas transform (17px offset)

**FR10:** The system must detect new rounds by monitoring timer reset (jump from low to high) and score changes

**FR11:** The system must detect winner by comparing score changes after timer reaches 0

**FR24:** The system must use adaptive screenshot frequency (200ms when timer > 6, 100ms when timer ≤ 6)

### Multi-Table Parallel Processing

**FR12:** The system must support up to 6 tables running in parallel

**FR30:** The system must implement thread-safe JSON file writing for parallel table processing

### Data Persistence and History

**FR13:** The system must create date-based session folders (`YYYY-MM-DD_HH-MM-SS`) on tool startup

**FR14:** The system must save round data to per-table JSON files (table_1.json through table_6.json) after each round

**FR15:** The system must maintain in-memory cache of all table data and flush to JSON files every round

### Desktop User Interface

**FR16:** The system must provide a desktop UI (Tkinter/PyQt) for monitoring and control

**FR17:** The system must display real-time status for all tables (timer, last 3 rounds, pattern match, decision, status)

**FR18:** The system must provide pattern editor UI with validation for pattern format

**FR19:** The system must provide history viewer showing last 20-50 rounds per table with success/failure indicators

**FR20:** The system must provide global start/stop controls for all tables

**FR21:** The system must provide individual pause/resume controls per table

**FR22:** The system must monitor yellow scoreboard section

**FR23:** The system must stop automation when target score is reached

**FR31:** The system must provide resource monitoring (CPU/memory) in UI

**FR32:** The system must auto-throttle screenshot frequency if CPU usage exceeds 80%

### Error Recovery and Resilience

**FR25:** The system must detect page refreshes and auto-resume after reload

**FR26:** The system must implement retry logic with exponential backoff (3 attempts: 1s, 2s, 4s) for failed screenshots

**FR27:** The system must implement template matching fallback to OCR if OpenCV fails 3 times

**FR28:** The system must lock browser window to fixed size and validate canvas position periodically

**FR29:** The system must detect stuck states (3 consecutive timeouts) and pause affected table

### Licensing (Phase 4)

**FR33:** The system must implement license key validation system (Phase 4)
