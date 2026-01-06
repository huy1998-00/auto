---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-01-06'
inputDocuments: ["_bmad-output/planning-artifacts/prd.md", "_bmad-output/planning-artifacts/prd/executive-summary.md", "_bmad-output/planning-artifacts/prd/success-criteria.md", "_bmad-output/planning-artifacts/prd/product-scope.md", "_bmad-output/planning-artifacts/prd/user-journeys.md", "_bmad-output/planning-artifacts/prd/domain-requirements.md", "_bmad-output/planning-artifacts/prd/innovation-analysis.md", "_bmad-output/planning-artifacts/prd/project-type-requirements.md", "_bmad-output/planning-artifacts/prd/functional-requirements.md", "_bmad-output/planning-artifacts/prd/non-functional-requirements.md", "_bmad-output/planning-artifacts/prd/technical-constraints.md", "_bmad-output/planning-artifacts/prd/assumptions-and-dependencies.md", "_bmad-output/planning-artifacts/prd/out-of-scope.md", "_bmad-output/planning-artifacts/prd/success-metrics-and-validation.md", "_bmad-output/planning-artifacts/prd/next-steps.md", "_bmad-output/planning-artifacts/epics.md"]
workflowType: 'architecture'
project_name: 'New folder'
user_name: 'Huy'
date: '2026-01-06'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

The project has 33 functional requirements organized into 6 major categories:

1. **Game State Capture and Analysis (FR1-FR11, FR24)**: Screenshot capture using Playwright, timer/score extraction via OpenCV template matching, pattern matching algorithm, click execution with two-phase process, round detection and winner identification
2. **Multi-Table Parallel Processing (FR12, FR30)**: Support for up to 6 tables running simultaneously with thread-safe operations
3. **Data Persistence and History (FR13-FR15)**: Date-based session folders, per-table JSON files, in-memory cache with periodic flushing
4. **Desktop User Interface (FR16-FR23, FR31-FR32)**: Real-time status monitoring, pattern editor with validation, history viewer, global and individual controls, resource monitoring
5. **Error Recovery and Resilience (FR25-FR29)**: Page refresh detection, retry logic with exponential backoff, OCR fallback, stuck state detection
6. **Licensing (FR33)**: Phase 4 feature, deferred implementation

**Non-Functional Requirements:**

17 NFRs that will drive architectural decisions:

- **Performance**: Parallel processing requirements (NFR1), strict latency targets (100-500ms) (NFR2-NFR4, NFR9), CPU-based auto-throttling (NFR32)
- **Reliability**: Single browser instance constraint (NFR5), page refresh recovery without data loss (NFR6), network resilience (NFR7), continuous data persistence (NFR11-NFR12)
- **Thread Safety and Concurrency**: Thread-safe operations for all shared data structures (NFR8), file locking for JSON writes (NFR13)
- **Data Validation and Quality**: Pattern format validation using regex (NFR10)
- **Error Handling and Debugging**: Error logging with screenshots (NFR14), anti-bot measures (NFR15)
- **Security and Licensing**: License key validation (NFR16-NFR17, Phase 4)

**Scale & Complexity:**

- **Primary domain**: Desktop automation application with browser automation and computer vision
- **Complexity level**: Medium-High
- **Estimated architectural components**: 8-10 major components
  - Browser automation layer (Playwright)
  - Image processing engine (OpenCV + OCR fallback)
  - Pattern matching engine
  - Multi-table orchestration layer
  - Data persistence layer
  - Desktop UI framework
  - Error recovery system
  - Resource monitoring system

### Technical Constraints & Dependencies

**Technology Stack Constraints:**

- **Browser Automation**: Playwright (Python) - single Chromium instance, fixed 1920x1080 window
- **Image Processing**: OpenCV (primary) + Tesseract/EasyOCR (fallback)
- **UI Framework**: Tkinter (built-in) or PyQt5/PySide6 (optional)
- **Data Storage**: JSON files (no database)
- **Concurrency**: Python threading or asyncio

**Platform Requirements:**

- Cross-platform desktop application (Windows, macOS, Linux)
- Python 3.8+ runtime
- Playwright browser binaries
- OpenCV and PIL libraries
- Optional OCR libraries

**Performance Constraints:**

- Hard limit: Maximum 6 tables
- Single browser instance (all tables on one page)
- Region-only screenshots (not full page)
- Adaptive screenshot frequency (100ms-200ms based on game phase)
- CPU-based auto-throttling at 80% usage

**Data Constraints:**

- Date-based session folders: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- Per-table JSON files (table_1.json through table_6.json)
- Continuous writing until tool closes
- Thread-safe file operations required

### Cross-Cutting Concerns Identified

1. **Thread Safety and Concurrency**: Parallel table processing requires thread-safe data structures, file locking, and coordinated state management
2. **Error Isolation**: Failures in one table must not cascade to others; per-table error recovery mechanisms
3. **Resource Management**: CPU/memory monitoring with adaptive throttling; efficient screenshot capture strategy
4. **State Persistence**: Round history must persist across page refreshes and errors; in-memory cache synchronization
5. **Coordinate Management**: Canvas transform offsets (17px), region-relative button coordinates, periodic validation
6. **Pattern Validation**: Regex validation (`^[BP]{3}-[BP](;[BP]{3}-[BP])*$`) across UI and processing layers
7. **Real-Time UI Updates**: 500ms refresh rate for status display; non-blocking UI operations
8. **Browser Lifecycle Management**: Single instance management, page refresh detection, canvas element monitoring

## Starter Template Evaluation

### Primary Technology Domain

Desktop automation application (Python-based) with browser automation, computer vision, and desktop UI requirements.

### Technical Preferences Discovery

From the PRD, the technology stack is already well-defined:

**Technology Stack (Already Defined):**
- **Language**: Python 3.8+
- **Browser Automation**: Playwright (Python)
- **Image Processing**: OpenCV + PIL (Pillow)
- **OCR Fallback**: Tesseract (pytesseract) or EasyOCR
- **UI Framework**: Tkinter (built-in) or PyQt5/PySide6 (optional)
- **Data Storage**: JSON files (Python json module)
- **Concurrency**: Python threading or asyncio

**Key Decisions Needed:**
1. UI Framework: Tkinter (built-in, no dependencies) vs PyQt5/PySide6 (more features)
2. Concurrency Model: Threading vs asyncio
3. Dependency Management: requirements.txt vs Poetry vs pipenv
4. Project Structure: Standard Python package layout

### Starter Options Considered

For Python desktop applications, there aren't traditional "starter templates" like web frameworks. Instead, we'll establish a project structure and organization pattern.

**Option 1: Standard Python Package Structure**
- Simple, conventional layout
- Easy to understand and maintain
- No external tooling required
- Works with pip/requirements.txt

**Option 2: Modern Python Project Template (Cookiecutter)**
- Uses cookiecutter for project generation
- Includes testing, linting, documentation setup
- More opinionated structure
- Requires cookiecutter installation

**Recommendation**: Standard Python Package Structure, since:
- Technology stack is already well-defined in PRD
- Simplicity aligns with desktop automation needs
- No need for complex scaffolding
- Easier for AI agents to understand and implement consistently

### Selected Starter: Standard Python Package Structure

**Rationale for Selection:**

1. Technology stack is already defined in the PRD - no need for framework selection
2. Desktop automation tools benefit from straightforward structure
3. No complex web framework conventions needed
4. Easier for AI agents to implement consistently
5. Standard Python layout is familiar and maintainable

**Initialization Approach:**

Since this is a Python desktop application with a defined stack, we'll establish the project structure manually rather than using a CLI starter. The structure will follow Python best practices:

```bash
# Project structure will be created as:
mini-game-automation/
├── src/
│   └── automation/
│       ├── __init__.py
│       ├── browser/
│       ├── image_processing/
│       ├── pattern_matching/
│       ├── data/
│       └── ui/
├── tests/
├── data/
│   └── sessions/
├── requirements.txt
├── README.md
└── main.py
```

**Architectural Decisions Provided by This Structure:**

**Language & Runtime:**
- Python 3.8+ (as specified in PRD)
- Standard library where possible
- External dependencies via requirements.txt

**Project Organization:**
- `src/automation/` - Main application code organized by domain (browser, image_processing, pattern_matching, data, ui)
- `tests/` - Test files mirroring source structure
- `data/sessions/` - Date-based session folders for JSON storage
- `main.py` - Application entry point

**Dependency Management:**
- `requirements.txt` for dependency tracking
- Standard pip installation workflow
- Clear separation of core dependencies vs optional (OCR libraries)

**Development Experience:**
- Standard Python development workflow
- No build step required (Python is interpreted)
- Direct execution via `python main.py`
- Testing with pytest (standard Python testing)

**UI Framework Decision:**
- Start with Tkinter (built-in, no dependencies) for MVP
- Architecture allows switching to PyQt5/PySide6 later if needed
- UI code isolated in `src/automation/ui/` module

**Concurrency Model Decision:**
- Use threading for parallel table processing (simpler for Playwright integration)
- Thread-safe operations for shared data structures
- File locking for concurrent JSON writes

**Note:** Project structure initialization should be the first implementation story, creating the directory structure and basic module files.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- UI Framework selection (Tkinter confirmed)
- Concurrency model (Threading confirmed)
- Browser automation patterns (Single instance, synchronous capture)
- Data persistence patterns (File locking strategy)

**Important Decisions (Shape Architecture):**
- Error handling strategy (Exponential backoff, per-table isolation)
- Image processing patterns (Shared templates, EasyOCR fallback)
- Pattern matching implementation (Priority-based, in-memory)

**Deferred Decisions (Post-MVP):**
- PyQt5/PySide6 migration (architecture supports future switch)
- Advanced analytics features (Phase 3)
- License key validation system (Phase 4)

### UI Framework Architecture

**Decision:** Tkinter (built-in) for MVP, with architecture supporting PyQt5/PySide6 migration

**Rationale:**
- Tkinter is built into Python, requiring no external dependencies
- Sufficient for MVP requirements (real-time status display, pattern editor, history viewer)
- Architecture isolates UI code in `src/automation/ui/` module, enabling framework swap
- PyQt5/PySide6 remains optional for advanced features if needed later

**Implementation Impact:**
- UI components designed with abstraction layer for framework independence
- All UI code contained in `src/automation/ui/` module
- UI updates use non-blocking operations to maintain 500ms refresh rate
- Pattern editor includes regex validation (`^[BP]{3}-[BP](;[BP]{3}-[BP])*$`)

**Affects:** Epic 4 (Desktop Control Interface)

### Concurrency Model

**Decision:** Threading for parallel table processing

**Rationale:**
- Simpler integration with Playwright (synchronous API)
- Straightforward parallel processing for up to 6 tables
- Thread-safe operations required for shared data structures
- File locking needed for concurrent JSON writes

**Implementation Details:**
- Each table runs in its own thread
- Thread-safe data structures for shared state (round history, patterns)
- File locking using portalocker library for cross-platform JSON writes
- Thread-safe queue for UI updates from worker threads

**Affects:** Epic 2 (Multi-Table Parallel Processing), Epic 3 (Data Persistence)

### Error Handling Strategy

**Decision:** Exponential backoff retry with per-table isolation and screenshot capture

**Rationale:**
- Exponential backoff (1s, 2s, 4s) handles transient network issues effectively
- Per-table isolation prevents cascade failures across tables
- Screenshot capture on failures enables debugging template matching issues

**Error Handling Flow:**
1. **Try**: Initial operation attempt
2. **Retry**: Up to 3 attempts with exponential backoff (1s, 2s, 4s delays)
3. **Fallback**: OCR fallback if template matching fails 3 times
4. **Alert User**: UI notification with error details
5. **Pause**: Affected table paused if recovery fails

**Per-Table Isolation:**
- Errors in one table do not affect other tables
- Each table maintains independent error state
- Failed table can be manually resumed via UI

**Affects:** Epic 5 (Error Recovery & System Resilience)

### Browser Automation Patterns

**Decision:** Single shared browser instance with synchronous capture and polling-based monitoring

**Rationale:**
- PRD specifies single browser instance constraint (NFR5)
- All 6 tables displayed on same page in single browser instance
- Synchronous capture simpler with threading model
- Polling-based canvas monitoring sufficient for game state detection

**Browser Instance Management:**
- Single Playwright browser instance shared across all tables
- Fixed window size (1920x1080) with resizing disabled
- Canvas element (`#layaCanvas`) monitored via polling
- Page refresh detection by monitoring URL/DOM changes

**Screenshot Capture Strategy:**
- Region-only screenshots using coordinates (x, y, width, height)
- Direct screenshot capture from canvas at specified regions
- Synchronous capture per table in parallel threads
- Inactive/paused tables skipped (no screenshot taken)

**Affects:** Epic 1 (Single Table Automation), Epic 2 (Multi-Table Parallel Processing)

### Image Processing Patterns

**Decision:** Shared templates with EasyOCR fallback and 3-failure threshold

**Rationale:**
- Shared templates (numbers 0-9) sufficient for timer and score extraction
- EasyOCR simpler setup than Tesseract (no system installation required)
- 3 consecutive failures threshold balances reliability with performance

**Template Matching:**
- Shared number templates (0-9) for timer and score extraction
- OpenCV template matching as primary method
- Timer extraction from orange countdown box
- Score extraction from blue and red team display boxes

**OCR Fallback:**
- EasyOCR triggered after 3 consecutive template matching failures
- Per-table fallback (doesn't affect other tables)
- Error logging with screenshots for debugging
- Fallback isolated to failed table only

**Affects:** Epic 1 (Single Table Automation), Epic 5 (Error Recovery)

### Pattern Matching Implementation

**Decision:** Priority-based matching with in-memory storage and regex validation at input

**Rationale:**
- Priority-based matching (first match wins) aligns with PRD requirements
- In-memory storage provides fast pattern matching performance
- Regex validation at input prevents invalid patterns from entering system

**Pattern Storage:**
- Patterns stored in memory per table
- Pattern format: `BBP-P;BPB-B` (semicolon-separated)
- Each pattern parsed as `{history: "BBP", decision: "P"}`

**Matching Algorithm:**
- Priority-based: First matching pattern wins
- Matches last 3 rounds against user-defined patterns
- Returns decision ("P" for Blue, "B" for Red) or None if no match
- Pattern validation using regex: `^[BP]{3}-[BP](;[BP]{3}-[BP])*$`

**Validation:**
- Regex validation at UI input (pattern editor)
- Validation prevents invalid patterns from being saved
- Error messages guide user to correct format

**Affects:** Epic 1 (Single Table Automation), Epic 4 (Desktop UI)

### Data Persistence Patterns

**Decision:** Cross-platform file locking with write-through cache and single session per instance

**Rationale:**
- Cross-platform file locking (portalocker) ensures thread-safe writes on all platforms
- Write-through cache provides immediate persistence (zero data loss)
- Single session per tool instance simplifies state management

**File Locking Strategy:**
- Portalocker library for cross-platform file locking
- Thread-safe JSON writes for parallel table processing
- Each table writes to its own JSON file (table_1.json through table_6.json)
- File locking prevents race conditions during concurrent writes

**Cache Synchronization:**
- Write-through strategy: Cache updated and immediately flushed to JSON
- In-memory cache loaded on startup for fast UI access
- Cache updated after each round completion
- Immediate persistence ensures zero data loss

**Session Management:**
- Single session per tool instance
- Date-based session folders: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- Session config JSON tracks global settings
- Continuous writing until tool closes

**Affects:** Epic 3 (Game History & Data Persistence), Epic 2 (Multi-Table Parallel Processing)

### Testing and Monitoring Considerations

**Resource Monitoring Testing Strategy:**

- **CPU Throttling Behavior**: When CPU usage exceeds 80%, screenshot frequency should be reduced proportionally (e.g., 200ms → 300ms, 100ms → 150ms)
- **Throttling Recovery**: System should return to normal frequency when CPU usage drops below 80%
- **UI Feedback**: Resource monitoring display should show throttling status and current CPU usage
- **Testing Requirements**: Verify throttling triggers correctly, recovers appropriately, and maintains automation functionality during throttling

**Coordinate Validation Testing:**

- **Canvas Transform Offset**: Validate 17px horizontal offset is correctly applied to all click coordinates
- **Region-Relative Coordinates**: Ensure button coordinates are correctly calculated relative to table region, not absolute page coordinates
- **Periodic Validation**: Canvas position validation every 10-20 rounds should detect coordinate drift (>5px threshold)
- **Testing Requirements**: Test click accuracy across all 6 table regions, verify offset calculations, validate coordinate recalibration if drift detected

**OCR Fallback Monitoring:**

- **Usage Tracking**: Monitor frequency of OCR fallback usage per table
- **Performance Impact**: Track OCR processing time vs template matching time
- **Failure Patterns**: Log when OCR fallback is triggered to identify systematic template matching issues
- **Bottleneck Detection**: Alert if OCR fallback usage exceeds threshold (e.g., >10% of extractions) indicating potential template matching degradation
- **Testing Requirements**: Test OCR fallback triggers correctly, measure performance impact, verify per-table isolation

**EasyOCR Performance Considerations:**

- **Fallback Performance**: EasyOCR is slower than template matching; monitor processing time impact
- **Concurrent OCR Usage**: If multiple tables trigger OCR simultaneously, ensure system handles concurrent OCR operations
- **Failure Escalation**: If OCR also fails consistently, system should pause affected table and alert user (per error handling strategy)
- **Testing Requirements**: Test concurrent OCR operations, measure performance degradation, verify graceful degradation when OCR fails

**Affects:** Epic 5 (Error Recovery), Epic 4 (Desktop UI), Epic 1 (Single Table Automation)

### Decision Impact Analysis

**Implementation Sequence:**

1. **Project Structure Setup** - Create directory structure and basic modules
2. **Browser Automation Layer** - Playwright setup with single instance management
3. **Image Processing Engine** - OpenCV template matching with EasyOCR fallback
4. **Pattern Matching Engine** - Priority-based matching with validation
5. **Data Persistence Layer** - File locking and cache management
6. **Multi-Table Orchestration** - Threading model with per-table isolation
7. **Error Recovery System** - Retry logic and fallback mechanisms
8. **Desktop UI Framework** - Tkinter implementation with real-time updates

**Cross-Component Dependencies:**

- **Browser Automation → Image Processing**: Screenshots feed into template matching
- **Image Processing → Pattern Matching**: Timer/scores enable pattern matching
- **Pattern Matching → Browser Automation**: Decisions trigger click execution
- **Data Persistence → All Components**: All components write to shared JSON files
- **Error Recovery → All Components**: Error handling wraps all operations
- **UI → All Components**: UI displays status from all components
- **Multi-Table Orchestration → All Components**: Coordinates parallel execution across tables

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**

5 major areas where AI agents could make different choices:
1. **Naming Conventions** - Module, class, function, variable naming
2. **Project Structure** - File organization and module layout
3. **Data Formats** - JSON structure, timestamps, error formats
4. **Communication Patterns** - Thread-to-UI communication, thread-safe data sharing
5. **Process Patterns** - Error handling, state management, resource cleanup

### Naming Patterns

**Python Code Naming Conventions:**

- **Modules**: `snake_case` (e.g., `browser_manager.py`, `pattern_matcher.py`)
- **Classes**: `PascalCase` (e.g., `BrowserManager`, `PatternMatcher`, `TableTracker`)
- **Functions/Methods**: `snake_case` (e.g., `capture_screenshot()`, `extract_timer()`, `match_pattern()`)
- **Variables**: `snake_case` (e.g., `table_id`, `round_history`, `timer_value`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TABLES = 6`, `DEFAULT_TIMEOUT = 5000`)
- **Private methods**: Prefix with single underscore `_private_method()` (e.g., `_calculate_coordinates()`)

**File Naming Conventions:**

- **Python files**: `snake_case.py` (e.g., `table_tracker.py`, `image_processor.py`)
- **Test files**: `test_<module_name>.py` (e.g., `test_pattern_matcher.py`, `test_browser_manager.py`)
- **Config files**: `snake_case.yaml` or `snake_case.json` (e.g., `session_config.json`, `table_regions.yaml`)

**Configuration Key Naming:**

- **JSON config keys**: `snake_case` (e.g., `session_start`, `table_id`, `round_history`)
- **Environment variables**: `UPPER_SNAKE_CASE` (e.g., `MAX_TABLES`, `SCREENSHOT_INTERVAL`)

**Thread/Queue Naming:**

- **Thread names**: Descriptive `snake_case` with table context (e.g., `table_1_processor`, `ui_updater`)
- **Queue names**: Descriptive purpose (e.g., `ui_update_queue`, `error_queue`)

### Structure Patterns

**Project Organization:**

- **Tests**: Separate `tests/` directory mirroring `src/` structure
  - `tests/browser/` - Browser automation tests
  - `tests/image_processing/` - Image processing tests
  - `tests/pattern_matching/` - Pattern matching tests
  - `tests/data/` - Data persistence tests
  - `tests/ui/` - UI tests
- **Utilities**: `src/automation/utils/` for shared utilities (e.g., `logger.py`, `validators.py`)
- **Configuration**: Root-level `config/` directory for config files
- **Data**: `data/sessions/YYYY-MM-DD_HH-MM-SS/` for session data (already defined in PRD)

**Module Organization within `src/automation/`:**

- `browser/` - Browser automation (Playwright)
  - `browser_manager.py` - Browser instance management
  - `screenshot_capture.py` - Screenshot capture logic
  - `click_executor.py` - Click execution with canvas offset
- `image_processing/` - OpenCV and OCR
  - `template_matcher.py` - OpenCV template matching
  - `ocr_fallback.py` - EasyOCR fallback implementation
  - `image_extractor.py` - Timer and score extraction
- `pattern_matching/` - Pattern matching engine
  - `pattern_matcher.py` - Pattern matching algorithm
  - `pattern_validator.py` - Regex validation
- `data/` - Data persistence and JSON handling
  - `session_manager.py` - Session folder and file management
  - `json_writer.py` - Thread-safe JSON writing
  - `cache_manager.py` - In-memory cache management
- `ui/` - Desktop UI (Tkinter)
  - `main_window.py` - Main UI window
  - `table_status_widget.py` - Per-table status display
  - `pattern_editor.py` - Pattern editor component
  - `history_viewer.py` - History viewer component
- `utils/` - Shared utilities
  - `logger.py` - Logging configuration
  - `validators.py` - Validation utilities
  - `coordinate_utils.py` - Coordinate calculation utilities

### Format Patterns

**JSON Session Data Structure:**

- **Keys**: All JSON keys use `snake_case` (e.g., `table_id`, `session_start`, `round_history`)
- **Timestamps**: Format `YYYY-MM-DD_HH-MM-SS` (e.g., `"2026-01-06_14-30-00"`)
  - Matches session folder naming convention
  - Used in session_start, session_end, round timestamps
- **Table JSON structure**: Consistent across all table files (table_1.json through table_6.json)
  ```json
  {
    "table_id": 1,
    "session_start": "2026-01-06_14-30-00",
    "patterns": "BBP-P;BPB-B",
    "rounds": [...],
    "statistics": {...}
  }
  ```
- **Round object structure**: Consistent format for all rounds
  ```json
  {
    "round_number": 1,
    "timestamp": "2026-01-06_14-30-00",
    "timer_start": 15,
    "blue_score": 0,
    "red_score": 0,
    "winner": "P",
    "decision_made": "blue",
    "pattern_matched": "BBP-P",
    "result": "correct"
  }
  ```

**Error Message Format:**

- **Structured error format**: 
  ```json
  {
    "error": {
      "type": "template_matching_failure",
      "message": "Failed to extract timer after 3 attempts",
      "table_id": 1,
      "timestamp": "2026-01-06_14-30-00",
      "context": {...}
    }
  }
  ```
- **Logging format**: `[LEVEL] [TIMESTAMP] [MODULE] [TABLE_ID] Message`
  - Example: `[ERROR] [2026-01-06_14-30-00] [image_processing] [1] Template matching failed`
- **Logging levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Error logging**: Always include table_id, timestamp, and error context

**Date/Time Formats:**

- **Session folders**: `YYYY-MM-DD_HH-MM-SS` (e.g., `2026-01-06_14-30-00`)
- **JSON timestamps**: `YYYY-MM-DD_HH-MM-SS` (e.g., `"2026-01-06_14-30-00"`)
- **Log timestamps**: `YYYY-MM-DD_HH-MM-SS` (consistent across all logging)

### Communication Patterns

**Thread-to-UI Communication:**

- **Queue type**: Use `queue.Queue` (thread-safe queue) for UI updates
- **Update message format**:
  ```python
  {
    "type": "status_update",  # or "error", "round_complete", etc.
    "table_id": 1,
    "data": {
      "timer": 15,
      "last_3_rounds": "BBP",
      "pattern_match": "BBP-P",
      "decision": "blue",
      "status": "active"
    },
    "timestamp": "2026-01-06_14-30-00"
  }
  ```
- **UI polling**: UI thread polls queue every 500ms (non-blocking)
- **Queue operations**: Worker threads use `queue.put()`, UI thread uses `queue.get_nowait()` to avoid blocking

**Thread-Safe Data Sharing:**

- **Lock mechanism**: Use `threading.Lock` for shared data structures
- **Lock granularity**: Per-table locks where possible (e.g., `table_locks[table_id]`)
- **File operations**: Use portalocker library for JSON file locking
- **Lock pattern**: Always use context manager (`with lock:`) for automatic release
  ```python
  with table_locks[table_id]:
      # Update table state
      table_state[table_id].update(...)
  ```

**Event/Notification Patterns:**

- **Event types**: Use string constants for event types (e.g., `EVENT_ROUND_COMPLETE`, `EVENT_ERROR`)
- **Event payload**: Consistent dictionary structure with `type`, `table_id`, `data`, `timestamp`
- **Event propagation**: Worker threads → Queue → UI thread (no direct UI updates from worker threads)

### Process Patterns

**Error Handling Pattern:**

- **Standard flow**: Try → Retry (3x with exponential backoff: 1s, 2s, 4s) → Fallback → Alert User → Pause
- **Per-table isolation**: Errors in one table do not affect other tables
- **Error logging**: Always log errors with screenshots on failures (for debugging)
- **Error recovery**: Automatic recovery where possible, manual intervention when needed
- **Error context**: Include table_id, timestamp, operation type, and error details

**State Management Pattern:**

- **Per-table state**: Each table has independent state object (`TableState`)
- **State updates**: Lock → Update → Unlock pattern (always use locks)
- **State persistence**: Write-through cache (update cache → immediately flush to JSON)
- **State restoration**: Load state from JSON on startup, restore after page refresh

**Resource Cleanup Pattern:**

- **Context managers**: Use context managers for browser resources (`with browser:`)
- **Cleanup in finally**: Always use `finally` blocks for guaranteed cleanup
- **Graceful shutdown**: 
  1. Stop all worker threads (set stop flag)
  2. Wait for threads to complete (with timeout)
  3. Save final state to JSON
  4. Close browser instance
  5. Exit application

**Retry Logic Pattern:**

- **Exponential backoff**: Delays of 1s, 2s, 4s for retry attempts
- **Retry count**: Maximum 3 retry attempts before fallback
- **Retry scope**: Per-table retry (doesn't affect other tables)
- **Retry logging**: Log each retry attempt with attempt number and delay

### Enforcement Guidelines

**All AI Agents MUST:**

- Follow Python naming conventions (snake_case for modules/functions/variables, PascalCase for classes)
- Use consistent JSON key naming (snake_case) across all data files
- Use timestamp format `YYYY-MM-DD_HH-MM-SS` for all timestamps
- Implement thread-safe operations using locks for shared data structures
- Use queue.Queue for thread-to-UI communication
- Follow error handling pattern: Try → Retry → Fallback → Alert → Pause
- Use context managers and finally blocks for resource cleanup
- Include table_id and timestamp in all error logs
- Mirror test directory structure matching source structure

**Pattern Enforcement:**

- **Code reviews**: Verify patterns are followed in all code changes
- **Linting**: Use Python linters (flake8, pylint) to enforce naming conventions
- **Documentation**: Document any pattern exceptions with rationale
- **Pattern updates**: Update this document when patterns evolve, notify all agents

### Pattern Examples

**Good Examples:**

**Naming:**
```python
# Module: browser_manager.py
class BrowserManager:
    MAX_TABLES = 6
    
    def capture_screenshot(self, table_id: int, region: dict) -> Image:
        """Capture screenshot for specific table region."""
        with self.table_locks[table_id]:
            # Thread-safe screenshot capture
            pass
```

**JSON Structure:**
```json
{
  "table_id": 1,
  "session_start": "2026-01-06_14-30-00",
  "rounds": [
    {
      "round_number": 1,
      "timestamp": "2026-01-06_14-30-15",
      "timer_start": 15,
      "winner": "P",
      "decision_made": "blue"
    }
  ]
}
```

**Thread Communication:**
```python
# Worker thread
ui_queue.put({
    "type": "status_update",
    "table_id": 1,
    "data": {"timer": 15, "status": "active"},
    "timestamp": "2026-01-06_14-30-00"
})

# UI thread (non-blocking)
try:
    update = ui_queue.get_nowait()
    update_ui(update)
except queue.Empty:
    pass  # No updates available
```

**Anti-Patterns:**

**Avoid:**
- ❌ Mixed naming conventions (`getUserData()` vs `get_user_data()`)
- ❌ Inconsistent timestamp formats (`2026-01-06T14:30:00Z` vs `2026-01-06_14-30-00`)
- ❌ Direct UI updates from worker threads (must use queue)
- ❌ Shared data access without locks
- ❌ camelCase in Python code (`tableId` should be `table_id`)
- ❌ Different JSON key formats (`tableId` vs `table_id`)
- ❌ Blocking queue operations in UI thread (`queue.get()` instead of `queue.get_nowait()`)

## Project Structure & Boundaries

### Complete Project Directory Structure

```
mini-game-automation/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── config/
│   ├── table_regions.yaml          # Table region coordinates configuration
│   └── default_patterns.yaml       # Default pattern configurations
├── src/
│   └── automation/
│       ├── __init__.py
│       ├── main.py                 # Application entry point
│       ├── browser/
│       │   ├── __init__.py
│       │   ├── browser_manager.py  # Single browser instance management
│       │   ├── screenshot_capture.py  # Region screenshot capture
│       │   ├── click_executor.py   # Two-phase click execution with canvas offset
│       │   └── page_monitor.py     # Page refresh detection, canvas monitoring
│       ├── image_processing/
│       │   ├── __init__.py
│       │   ├── template_matcher.py  # OpenCV template matching
│       │   ├── ocr_fallback.py      # EasyOCR fallback implementation
│       │   ├── image_extractor.py   # Timer and score extraction
│       │   └── templates/           # Number templates (0-9) for template matching
│       │       ├── 0.png
│       │       ├── 1.png
│       │       ├── ... (2-9)
│       │       └── 9.png
│       ├── pattern_matching/
│       │   ├── __init__.py
│       │   ├── pattern_matcher.py   # Priority-based pattern matching algorithm
│       │   └── pattern_validator.py # Regex validation for pattern format
│       ├── data/
│       │   ├── __init__.py
│       │   ├── session_manager.py   # Session folder creation and management
│       │   ├── json_writer.py       # Thread-safe JSON file writing
│       │   └── cache_manager.py     # In-memory cache with write-through strategy
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py       # Main Tkinter window
│       │   ├── table_status_widget.py  # Per-table status display component
│       │   ├── pattern_editor.py    # Pattern editor with validation
│       │   ├── history_viewer.py    # History viewer with filtering
│       │   └── resource_monitor.py  # CPU/memory monitoring display
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logger.py            # Logging configuration
│       │   ├── validators.py         # Validation utilities
│       │   ├── coordinate_utils.py   # Coordinate calculation utilities (17px offset)
│       │   └── resource_monitor.py   # CPU/memory monitoring utilities
│       └── orchestration/
│           ├── __init__.py
│           ├── table_tracker.py     # Per-table state tracking
│           ├── multi_table_manager.py  # Multi-table orchestration (up to 6 tables)
│           ├── error_recovery.py    # Error handling and retry logic
│           └── screenshot_scheduler.py  # Adaptive screenshot frequency management
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration and fixtures
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── test_browser_manager.py
│   │   ├── test_screenshot_capture.py
│   │   ├── test_click_executor.py
│   │   └── test_page_monitor.py
│   ├── image_processing/
│   │   ├── __init__.py
│   │   ├── test_template_matcher.py
│   │   ├── test_ocr_fallback.py
│   │   └── test_image_extractor.py
│   ├── pattern_matching/
│   │   ├── __init__.py
│   │   ├── test_pattern_matcher.py
│   │   └── test_pattern_validator.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── test_session_manager.py
│   │   ├── test_json_writer.py
│   │   └── test_cache_manager.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── test_main_window.py
│   │   ├── test_table_status_widget.py
│   │   └── test_pattern_editor.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── test_validators.py
│   │   └── test_coordinate_utils.py
│   └── orchestration/
│       ├── __init__.py
│       ├── test_table_tracker.py
│       ├── test_multi_table_manager.py
│       └── test_error_recovery.py
├── data/
│   └── sessions/                    # Date-based session folders
│       └── YYYY-MM-DD_HH-MM-SS/    # Example: 2026-01-06_14-30-00/
│           ├── table_1.json
│           ├── table_2.json
│           ├── ... (table_3.json through table_6.json)
│           └── session_config.json
└── logs/                            # Application logs
    └── automation.log
```

### Architectural Boundaries

**Module Boundaries:**

- **Browser Module** (`src/automation/browser/`): Handles all Playwright browser interactions, screenshot capture, and click execution. No direct image processing or pattern matching logic.
- **Image Processing Module** (`src/automation/image_processing/`): Handles OpenCV template matching and OCR fallback. Receives screenshots from browser module, returns extracted timer/scores.
- **Pattern Matching Module** (`src/automation/pattern_matching/`): Pure pattern matching logic. Receives round history, returns decisions. No browser or UI dependencies.
- **Data Module** (`src/automation/data/`): Handles all data persistence. Thread-safe JSON writing, cache management. No business logic dependencies.
- **UI Module** (`src/automation/ui/`): Desktop UI components. Receives updates via queue, displays status. No direct access to browser or processing modules.
- **Orchestration Module** (`src/automation/orchestration/`): Coordinates multi-table processing, error recovery, screenshot scheduling. Integrates all other modules.

**Communication Boundaries:**

- **Browser → Image Processing**: Screenshots passed as PIL Image objects
- **Image Processing → Pattern Matching**: Timer/scores passed as structured data
- **Pattern Matching → Browser**: Decisions passed as action commands
- **All Modules → Data**: Round data written via thread-safe JSON writer
- **Worker Threads → UI**: Status updates via thread-safe queue
- **UI → Worker Threads**: Control commands via thread-safe queue

**Data Boundaries:**

- **Session Data**: JSON files in `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- **Configuration**: YAML files in `config/` directory
- **Templates**: PNG image files in `src/automation/image_processing/templates/`
- **Logs**: Text files in `logs/` directory
- **No Database**: All data stored in JSON files (per PRD requirement)

### Requirements to Structure Mapping

**Epic 1: Single Table Automation**
- **Browser Automation**: `src/automation/browser/` (browser_manager.py, screenshot_capture.py, click_executor.py)
- **Image Processing**: `src/automation/image_processing/` (template_matcher.py, image_extractor.py)
- **Pattern Matching**: `src/automation/pattern_matching/` (pattern_matcher.py, pattern_validator.py)
- **Table Tracking**: `src/automation/orchestration/table_tracker.py`
- **Tests**: `tests/browser/`, `tests/image_processing/`, `tests/pattern_matching/`

**Epic 2: Multi-Table Parallel Processing**
- **Multi-Table Management**: `src/automation/orchestration/multi_table_manager.py`
- **Screenshot Scheduling**: `src/automation/orchestration/screenshot_scheduler.py`
- **Thread-Safe Operations**: `src/automation/data/json_writer.py` (file locking)
- **Tests**: `tests/orchestration/test_multi_table_manager.py`

**Epic 3: Game History & Data Persistence**
- **Session Management**: `src/automation/data/session_manager.py`
- **JSON Writing**: `src/automation/data/json_writer.py`
- **Cache Management**: `src/automation/data/cache_manager.py`
- **Data Storage**: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- **Tests**: `tests/data/`

**Epic 4: Desktop Control Interface**
- **Main UI**: `src/automation/ui/main_window.py`
- **Table Status**: `src/automation/ui/table_status_widget.py`
- **Pattern Editor**: `src/automation/ui/pattern_editor.py`
- **History Viewer**: `src/automation/ui/history_viewer.py`
- **Resource Monitor**: `src/automation/ui/resource_monitor.py`
- **Tests**: `tests/ui/`

**Epic 5: Error Recovery & System Resilience**
- **Error Recovery**: `src/automation/orchestration/error_recovery.py`
- **Page Monitoring**: `src/automation/browser/page_monitor.py`
- **OCR Fallback**: `src/automation/image_processing/ocr_fallback.py`
- **Cross-Module**: Error handling integrated into all modules
- **Tests**: `tests/orchestration/test_error_recovery.py`, `tests/browser/test_page_monitor.py`

**Epic 6: License Key Validation (Phase 4)**
- **License Module**: `src/automation/utils/license_validator.py` (future)
- **Configuration**: `config/license_keys.yaml` (future)

**Cross-Cutting Concerns:**

- **Logging**: `src/automation/utils/logger.py` (used by all modules)
- **Validation**: `src/automation/utils/validators.py` (pattern validation, coordinate validation)
- **Coordinate Utilities**: `src/automation/utils/coordinate_utils.py` (17px canvas offset calculations)
- **Resource Monitoring**: `src/automation/utils/resource_monitor.py` (CPU/memory monitoring)

### Integration Points

**Internal Communication:**

- **Thread-to-UI Queue**: `queue.Queue` for status updates from worker threads to UI thread
- **Thread-Safe Locks**: `threading.Lock` for shared data structures (per-table locks)
- **File Locking**: `portalocker` library for thread-safe JSON file writes
- **State Management**: Per-table state objects with thread-safe access patterns

**External Integrations:**

- **Playwright**: Browser automation library (single Chromium instance)
- **OpenCV**: Image processing and template matching
- **EasyOCR**: OCR fallback library (optional dependency)
- **Tkinter**: Desktop UI framework (built-in)
- **Portalocker**: Cross-platform file locking library

**Data Flow:**

1. **Browser Module** captures region screenshots → **Image Processing Module**
2. **Image Processing Module** extracts timer/scores → **Pattern Matching Module**
3. **Pattern Matching Module** returns decision → **Browser Module** (click execution)
4. **All Modules** write round data → **Data Module** (JSON persistence)
5. **Worker Threads** send status updates → **UI Queue** → **UI Module** (display)
6. **UI Module** sends control commands → **Control Queue** → **Orchestration Module**

### File Organization Patterns

**Configuration Files:**

- **Root Level**: `requirements.txt`, `.gitignore`, `.env.example`
- **Config Directory**: `config/table_regions.yaml`, `config/default_patterns.yaml`
- **Environment Variables**: `.env` file (not in git), `.env.example` (template)

**Source Organization:**

- **Domain-Driven**: Modules organized by domain (browser, image_processing, pattern_matching, data, ui)
- **Separation of Concerns**: Each module has clear responsibilities and boundaries
- **Utilities**: Shared utilities in `utils/` directory
- **Orchestration**: Cross-cutting coordination in `orchestration/` directory

**Test Organization:**

- **Mirror Structure**: Tests mirror source structure (`tests/browser/` mirrors `src/automation/browser/`)
- **Test Files**: `test_<module_name>.py` naming convention
- **Fixtures**: Shared fixtures in `tests/conftest.py`
- **Coverage**: Each module has corresponding test module

**Asset Organization:**

- **Templates**: Image templates in `src/automation/image_processing/templates/`
- **Session Data**: Date-based folders in `data/sessions/`
- **Logs**: Application logs in `logs/` directory
- **No Static Web Assets**: Desktop application, no web assets needed

### Development Workflow Integration

**Development Server Structure:**

- **Entry Point**: `src/automation/main.py` - Run with `python -m automation.main`
- **Development Mode**: Direct Python execution, no build step required
- **Hot Reload**: Not applicable (Python interpreted language)

**Build Process Structure:**

- **Dependencies**: `requirements.txt` for pip installation
- **No Build Step**: Python is interpreted, no compilation needed
- **Executable Creation**: Future: PyInstaller or similar for standalone executable

**Deployment Structure:**

- **Standalone Executable**: Future: Single executable file with all dependencies bundled
- **Cross-Platform**: Same codebase works on Windows, macOS, Linux
- **Data Persistence**: `data/sessions/` directory created at runtime
- **Configuration**: `config/` directory with default configurations

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**

All architectural decisions work together cohesively:

- **Technology Stack**: Python 3.8+, Playwright, OpenCV, EasyOCR, Tkinter, threading - all technologies are compatible and work together seamlessly
- **Concurrency Model**: Threading aligns perfectly with Playwright's synchronous API and enables parallel table processing
- **UI Framework**: Tkinter (built-in) reduces dependencies while architecture supports future PyQt5/PySide6 migration
- **Data Storage**: JSON files with portalocker file locking provides thread-safe persistence without database overhead
- **Image Processing**: OpenCV primary with EasyOCR fallback creates robust extraction pipeline
- **No Conflicts**: All technology choices complement each other without version conflicts or integration issues

**Pattern Consistency:**

Implementation patterns fully support architectural decisions:

- **Naming Conventions**: Python-standard snake_case/PascalCase aligns with technology stack
- **Structure Patterns**: Domain-driven organization (browser/, image_processing/, etc.) supports modular architecture
- **Communication Patterns**: Thread-safe queues and locks align with threading concurrency model
- **Format Patterns**: Consistent JSON structure and timestamp format (`YYYY-MM-DD_HH-MM-SS`) supports data persistence requirements
- **Process Patterns**: Error handling, retry logic, and resource cleanup patterns align with reliability requirements

**Structure Alignment:**

Project structure fully supports all architectural decisions:

- **Module Boundaries**: Clear separation of concerns (browser, image_processing, pattern_matching, data, ui, orchestration)
- **Integration Points**: Well-defined communication patterns between modules (queues, locks, file locking)
- **Technology Integration**: Structure accommodates all chosen technologies (Playwright, OpenCV, Tkinter, etc.)
- **Scalability**: Structure supports up to 6 tables with clear per-table isolation

### Requirements Coverage Validation ✅

**Epic Coverage:**

All 6 epics have complete architectural support:

- **Epic 1 (Single Table Automation)**: Fully supported by browser/, image_processing/, pattern_matching/ modules
- **Epic 2 (Multi-Table Parallel Processing)**: Supported by orchestration/multi_table_manager.py with threading model
- **Epic 3 (Data Persistence)**: Fully supported by data/ module with JSON persistence and cache management
- **Epic 4 (Desktop UI)**: Fully supported by ui/ module with Tkinter implementation
- **Epic 5 (Error Recovery)**: Supported by orchestration/error_recovery.py and cross-module error handling
- **Epic 6 (Licensing)**: Deferred to Phase 4, architecture supports future addition

**Functional Requirements Coverage:**

All 33 functional requirements are architecturally supported:

- **FR1-FR11, FR24 (Game State Capture)**: browser/screenshot_capture.py, image_processing/image_extractor.py, pattern_matching/pattern_matcher.py
- **FR12, FR30 (Multi-Table)**: orchestration/multi_table_manager.py, data/json_writer.py (thread-safe)
- **FR13-FR15 (Data Persistence)**: data/session_manager.py, data/json_writer.py, data/cache_manager.py
- **FR16-FR23, FR31-FR32 (Desktop UI)**: ui/main_window.py, ui/table_status_widget.py, ui/pattern_editor.py, ui/history_viewer.py, ui/resource_monitor.py
- **FR25-FR29 (Error Recovery)**: orchestration/error_recovery.py, browser/page_monitor.py, image_processing/ocr_fallback.py
- **FR33 (Licensing)**: Deferred to Phase 4

**Non-Functional Requirements Coverage:**

All 17 NFRs are architecturally addressed:

- **NFR1 (Parallel Processing)**: Threading model with multi_table_manager.py
- **NFR2-NFR4, NFR9 (Performance)**: Adaptive screenshot frequency, 500ms UI updates, latency targets addressed
- **NFR5 (Single Browser Instance)**: browser/browser_manager.py enforces single instance
- **NFR6 (Page Refresh Recovery)**: browser/page_monitor.py with state restoration
- **NFR7 (Network Resilience)**: orchestration/error_recovery.py with retry logic
- **NFR8, NFR13 (Thread Safety)**: Thread-safe operations, portalocker file locking
- **NFR10 (Pattern Validation)**: pattern_matching/pattern_validator.py with regex
- **NFR11-NFR12 (Data Persistence)**: data/json_writer.py with continuous writing
- **NFR14 (Error Logging)**: utils/logger.py with screenshot capture on failures
- **NFR15 (Anti-Bot Measures)**: Random delays in click_executor.py
- **NFR16-NFR17 (Licensing)**: Deferred to Phase 4
- **NFR32 (CPU Throttling)**: utils/resource_monitor.py with auto-throttling

### Implementation Readiness Validation ✅

**Decision Completeness:**

All critical decisions are documented with sufficient detail:

- **Technology Versions**: Python 3.8+, all library choices specified
- **Architectural Patterns**: All major patterns documented with examples
- **Integration Points**: All communication patterns clearly defined
- **Performance Considerations**: CPU throttling, adaptive frequencies, latency targets addressed
- **Testing Strategy**: Testing patterns and monitoring requirements documented

**Structure Completeness:**

Project structure is complete and specific:

- **All Modules Defined**: browser/, image_processing/, pattern_matching/, data/, ui/, orchestration/, utils/
- **All Files Specified**: Complete file tree with specific file names and purposes
- **Integration Points Mapped**: Clear boundaries and communication patterns defined
- **Test Structure**: Complete test directory structure mirroring source
- **Configuration**: Config files and data directories fully specified

**Pattern Completeness:**

Implementation patterns are comprehensive:

- **Naming Conventions**: Complete coverage (modules, classes, functions, variables, constants, files)
- **Structure Patterns**: Project organization, file structure, test organization fully defined
- **Format Patterns**: JSON structure, timestamps, error formats, logging formats specified
- **Communication Patterns**: Thread-to-UI queues, thread-safe data sharing, event patterns documented
- **Process Patterns**: Error handling, state management, resource cleanup, retry logic fully specified
- **Examples Provided**: Good examples and anti-patterns documented for clarity

### Gap Analysis Results

**Critical Gaps:** None identified - all critical architectural decisions are complete

**Important Gaps:** None identified - architecture is comprehensive

**Nice-to-Have Enhancements:**

- **Development Tooling**: Could add pre-commit hooks for pattern enforcement (optional)
- **Documentation**: Could add API documentation generation (optional, not critical)
- **Monitoring**: Could add more detailed performance metrics collection (optional enhancement)

### Validation Issues Addressed

No critical or important issues found during validation. Architecture is coherent, complete, and ready for implementation.

### Architecture Completeness Checklist

**✅ Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed (Medium-High)
- [x] Technical constraints identified (Python, Playwright, OpenCV, Tkinter, threading, JSON)
- [x] Cross-cutting concerns mapped (8 major concerns identified)

**✅ Architectural Decisions**

- [x] Critical decisions documented with versions (Python 3.8+, all libraries specified)
- [x] Technology stack fully specified (Playwright, OpenCV, EasyOCR, Tkinter, portalocker)
- [x] Integration patterns defined (queues, locks, file locking)
- [x] Performance considerations addressed (CPU throttling, adaptive frequencies, latency targets)

**✅ Implementation Patterns**

- [x] Naming conventions established (snake_case, PascalCase, UPPER_SNAKE_CASE)
- [x] Structure patterns defined (domain-driven organization)
- [x] Communication patterns specified (thread-safe queues, locks)
- [x] Process patterns documented (error handling, retry logic, resource cleanup)

**✅ Project Structure**

- [x] Complete directory structure defined (all modules, files, tests specified)
- [x] Component boundaries established (clear module separation)
- [x] Integration points mapped (queues, locks, file operations)
- [x] Requirements to structure mapping complete (all epics mapped to modules)

**✅ Testing and Monitoring**

- [x] Testing patterns defined (mirror structure, pytest)
- [x] Monitoring requirements documented (CPU throttling, OCR fallback tracking)
- [x] Error logging strategy specified (screenshots on failures, structured logging)

### Architecture Readiness Assessment

**Overall Status:** ✅ READY FOR IMPLEMENTATION

**Confidence Level:** HIGH - Architecture is comprehensive, coherent, and all requirements are supported

**Key Strengths:**

1. **Complete Requirements Coverage**: All 33 FRs and 17 NFRs architecturally supported
2. **Clear Module Boundaries**: Well-defined separation of concerns enables parallel development
3. **Comprehensive Patterns**: Detailed implementation patterns prevent AI agent conflicts
4. **Technology Compatibility**: All chosen technologies work together seamlessly
5. **Thread Safety**: Robust concurrency model with proper isolation and locking
6. **Error Recovery**: Multi-layer error handling with per-table isolation
7. **Scalability**: Architecture supports up to 6 tables with clear performance targets

**Areas for Future Enhancement:**

1. **Development Tooling**: Pre-commit hooks for pattern enforcement (optional)
2. **Performance Monitoring**: Enhanced metrics collection beyond CPU/memory (optional)
3. **Documentation**: API documentation generation tools (optional)
4. **Executable Packaging**: PyInstaller configuration for standalone executables (post-MVP)

### Implementation Handoff

**AI Agent Guidelines:**

- **Follow Architectural Decisions**: All technology choices, patterns, and structure decisions must be followed exactly as documented
- **Use Implementation Patterns**: Apply naming conventions, structure patterns, and communication patterns consistently across all components
- **Respect Boundaries**: Maintain clear module boundaries and use defined integration points (queues, locks, file locking)
- **Reference Architecture**: Refer to this document for all architectural questions and decisions
- **Test Coverage**: Implement tests mirroring source structure, covering all major functionality
- **Error Handling**: Follow documented error handling patterns (Try → Retry → Fallback → Alert → Pause)

**First Implementation Priority:**

1. **Project Structure Setup**: Create complete directory structure as defined in Project Structure section
2. **Core Dependencies**: Set up requirements.txt with all dependencies (Playwright, OpenCV, EasyOCR, portalocker, etc.)
3. **Browser Module**: Implement browser_manager.py with single instance management
4. **Image Processing Module**: Implement template_matcher.py with OpenCV template matching
5. **Pattern Matching Module**: Implement pattern_matcher.py with priority-based matching
6. **Data Module**: Implement session_manager.py and json_writer.py with thread-safe operations
7. **Orchestration Module**: Implement multi_table_manager.py with threading model
8. **UI Module**: Implement main_window.py with Tkinter and real-time updates

**Implementation Sequence:**

Follow the implementation sequence defined in Decision Impact Analysis:
1. Project Structure Setup
2. Browser Automation Layer
3. Image Processing Engine
4. Pattern Matching Engine
5. Data Persistence Layer
6. Multi-Table Orchestration
7. Error Recovery System
8. Desktop UI Framework

**Critical Implementation Notes:**

- **Thread Safety**: Always use locks for shared data structures, portalocker for file operations
- **Error Isolation**: Ensure per-table error isolation - errors in one table must not affect others
- **Coordinate Management**: Always account for 17px canvas transform offset in click coordinates
- **Pattern Validation**: Validate all patterns using regex `^[BP]{3}-[BP](;[BP]{3}-[BP])*$` at input
- **Timestamp Format**: Use `YYYY-MM-DD_HH-MM-SS` format for all timestamps (matches session folders)
- **UI Updates**: Use non-blocking queue operations (`get_nowait()`) in UI thread
- **Resource Cleanup**: Always use context managers and finally blocks for resource cleanup

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2026-01-06
**Document Location:** _bmad-output/planning-artifacts/architecture.md

### Final Architecture Deliverables

**📋 Complete Architecture Document**

- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**🏗️ Implementation Ready Foundation**

- 7 major architectural decisions made (UI Framework, Concurrency, Error Handling, Browser Automation, Image Processing, Pattern Matching, Data Persistence)
- 5 implementation pattern categories defined (Naming, Structure, Format, Communication, Process)
- 8 architectural components specified (Browser, Image Processing, Pattern Matching, Data, UI, Orchestration, Utils, Tests)
- 50 requirements fully supported (33 FRs + 17 NFRs)

**📚 AI Agent Implementation Guide**

- Technology stack with verified versions (Python 3.8+, Playwright, OpenCV, EasyOCR, Tkinter, portalocker)
- Consistency rules that prevent implementation conflicts
- Project structure with clear boundaries
- Integration patterns and communication standards

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing Mini-Game Website Automation & Pattern Tracking Tool. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**

1. **Project Structure Setup** - Create complete directory structure as defined in Project Structure section
2. **Core Dependencies** - Set up requirements.txt with all dependencies (Playwright, OpenCV, EasyOCR, portalocker, etc.)
3. **Browser Module** - Implement browser_manager.py with single instance management
4. **Image Processing Module** - Implement template_matcher.py with OpenCV template matching
5. **Pattern Matching Module** - Implement pattern_matcher.py with priority-based matching
6. **Data Module** - Implement session_manager.py and json_writer.py with thread-safe operations
7. **Orchestration Module** - Implement multi_table_manager.py with threading model
8. **UI Module** - Implement main_window.py with Tkinter and real-time updates

**Development Sequence:**

1. Initialize project using documented project structure
2. Set up development environment per architecture (Python 3.8+, install dependencies)
3. Implement core architectural foundations (browser automation, image processing, pattern matching)
4. Build features following established patterns (multi-table processing, UI, error recovery)
5. Maintain consistency with documented rules (naming, structure, communication patterns)

### Quality Assurance Checklist

**✅ Architecture Coherence**

- [x] All decisions work together without conflicts
- [x] Technology choices are compatible (Python, Playwright, OpenCV, EasyOCR, Tkinter, threading)
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**

- [x] All 33 functional requirements are supported
- [x] All 17 non-functional requirements are addressed
- [x] Cross-cutting concerns are handled (8 major concerns identified)
- [x] Integration points are defined (queues, locks, file locking)

**✅ Implementation Readiness**

- [x] Decisions are specific and actionable (all versions and patterns documented)
- [x] Patterns prevent agent conflicts (comprehensive naming, structure, communication rules)
- [x] Structure is complete and unambiguous (all files and directories specified)
- [x] Examples are provided for clarity (good examples and anti-patterns documented)

### Project Success Factors

**🎯 Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction. The architecture balances simplicity (Tkinter for MVP) with scalability (support for PyQt5/PySide6 migration).

**🔧 Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly. Thread-safe operations, naming conventions, and communication patterns are all clearly defined.

**📋 Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs (6 epics) to technical implementation (8 modules). All 50 requirements (33 FRs + 17 NFRs) are addressed.

**🏗️ Solid Foundation**
The standard Python package structure and architectural patterns provide a production-ready foundation following current best practices. The architecture supports MVP development while enabling future enhancements.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein. Follow the implementation sequence defined in Decision Impact Analysis section.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation. The architecture serves as the single source of truth for all technical decisions.
