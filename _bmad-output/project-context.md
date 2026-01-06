---
project_name: 'New folder'
user_name: 'Huy'
date: '2026-01-06'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 45
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Core Technologies:**
- **Python**: 3.8+ (runtime requirement)
- **Playwright**: Python library for browser automation (single Chromium instance)
- **OpenCV**: Primary image processing (template matching for numbers 0-9)
- **EasyOCR**: OCR fallback library (optional dependency, simpler setup than Tesseract)
- **Tkinter**: Built-in Python UI framework (MVP, architecture supports PyQt5/PySide6 migration)
- **portalocker**: Cross-platform file locking library (required for thread-safe JSON writes)
- **pytest**: Testing framework

**Key Dependencies:**
- **PIL/Pillow**: Image manipulation
- **pytesseract** or **EasyOCR**: OCR fallback (EasyOCR recommended for easier setup)

## Critical Implementation Rules

### Language-Specific Rules (Python)

**Naming Conventions (MANDATORY):**
- **Modules**: `snake_case` (e.g., `browser_manager.py`, `pattern_matcher.py`)
- **Classes**: `PascalCase` (e.g., `BrowserManager`, `PatternMatcher`)
- **Functions/Methods**: `snake_case` (e.g., `capture_screenshot()`, `extract_timer()`)
- **Variables**: `snake_case` (e.g., `table_id`, `round_history`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TABLES = 6`, `DEFAULT_TIMEOUT = 5000`)
- **Private methods**: Prefix with single underscore `_private_method()` (e.g., `_calculate_coordinates()`)

**Thread Safety (CRITICAL):**
- Always use `threading.Lock` for shared data structures
- Use context managers: `with lock:` for automatic release
- Use `queue.Queue` (thread-safe queue) for thread-to-UI communication
- Use `portalocker` library for cross-platform file locking (not fcntl/msvcrt)
- Per-table locks where possible (e.g., `table_locks[table_id]`)

**Error Handling Pattern (MANDATORY):**
- Follow exact flow: Try → Retry (3x with exponential backoff: 1s, 2s, 4s) → Fallback → Alert User → Pause
- Always use `finally` blocks for resource cleanup
- Use context managers (`with` statements) for browser resources
- Per-table error isolation (errors in one table must not affect others)

**Resource Management:**
- Always use context managers for browser resources (`with browser:`)
- Cleanup in `finally` blocks for guaranteed cleanup
- Graceful shutdown sequence: Stop all worker threads → Wait for completion → Save final state → Close browser → Exit

**JSON Data Format (MANDATORY):**
- All JSON keys use `snake_case` (e.g., `table_id`, `session_start`, `round_history`)
- Timestamps: Always use `YYYY-MM-DD_HH-MM-SS` format (e.g., `"2026-01-06_14-30-00"`)
- Consistent structure across all table files (table_1.json through table_6.json)

### Framework-Specific Rules

**Tkinter UI Rules:**
- **UI Thread Safety**: Never update UI directly from worker threads - always use `queue.Queue`
- **Non-Blocking Operations**: UI thread must use `queue.get_nowait()` (never `queue.get()`)
- **UI Update Frequency**: Poll queue every 500ms for real-time updates
- **UI Code Location**: All UI code in `src/automation/ui/` module
- **UI Abstraction**: Design with abstraction layer for future PyQt5/PySide6 migration

**Playwright Browser Rules:**
- **Single Browser Instance**: Only one Playwright browser instance for all 6 tables (hard constraint)
- **Fixed Window Size**: 1920x1080 with resizing disabled
- **Region Screenshots**: Region-only screenshots using coordinates (x, y, width, height), not full page
- **Synchronous Capture**: Synchronous capture per table in parallel threads
- **Inactive Tables**: Skip screenshots for inactive/paused tables (save resources)
- **Canvas Monitoring**: Monitor `#layaCanvas` element via polling (not event-based)
- **Page Refresh Detection**: Monitor URL/DOM changes, pause all tables, auto-resume after reload

**Click Execution (CRITICAL):**
- **Two-Phase Clicking**: (1) Choose team button (blue/red), (2) Confirm (✓ tick) or Cancel (✗ tick)
- **Canvas Transform Offset**: Always account for 17px horizontal offset in click coordinates
  - Formula: `absolute_x = canvas_box['x'] + table_region['x'] + button_x + 17`
  - Formula: `absolute_y = canvas_box['y'] + table_region['y'] + button_y`
- **Button Coordinates**: Relative to table region, NOT absolute to page
- **Phase Delay**: 50-100ms delay between Phase 1 and Phase 2 (wait for confirmation UI)
- **Timer Validation**: Only click when timer > 6 (values 7-25 are clickable)

**Threading Rules:**
- **Thread Management**: Each table runs in its own thread (maximum 6 tables)
- **Per-Table Locks**: Use per-table locks for shared data structures
- **Thread Communication**: Worker threads use `queue.put()`, UI thread uses `queue.get_nowait()`
- **Thread Isolation**: Errors in one thread must not affect other threads

**Image Processing Rules:**
- **Template Matching**: Shared number templates (0-9) for timer and score extraction
- **OCR Fallback**: Triggered after 3 consecutive template matching failures (per-table)
- **Fallback Isolation**: OCR fallback only affects the failed table, not others
- **Error Logging**: Always log failures with screenshots for debugging

**Pattern Matching Rules:**
- **Pattern Format**: `BBP-P;BPB-B` (semicolon-separated, format: `[last 3 rounds]-[decision]`)
- **Pattern Validation**: Use regex `^[BP]{3}-[BP](;[BP]{3}-[BP])*$` at input (before saving)
- **Matching Algorithm**: Priority-based (first match wins)
- **Storage**: In-memory storage per table (fast performance)
- **Decision Logic**: B = Red team, P = Blue team

**Data Persistence Rules:**
- **Session Folders**: Date-based format `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- **File Locking**: Use portalocker for cross-platform thread-safe JSON writes
- **Write-Through Cache**: Update cache → immediately flush to JSON (zero data loss)
- **Per-Table Files**: Each table writes to its own JSON file (table_1.json through table_6.json)
- **Continuous Writing**: Save every round until tool closes (no batching)

### Testing Rules

**Test Structure:**
- Tests mirror source structure: `tests/browser/`, `tests/image_processing/`, etc.
- Test files: `test_<module_name>.py` (e.g., `test_pattern_matcher.py`)
- Shared fixtures in `tests/conftest.py`

**Test Coverage Requirements:**
- Each module must have corresponding test module
- Test thread safety for all shared data structures
- Test error handling patterns (retry logic, fallback mechanisms)
- Test coordinate calculations (17px canvas offset)
- Test per-table isolation for error scenarios

**Test Patterns:**
- Use pytest fixtures for test setup
- Mock Playwright browser for browser tests
- Mock OpenCV for image processing tests
- Test error isolation (errors in one table don't affect others)

### Code Quality & Style Rules

**Naming Conventions (MANDATORY):**
- Python: snake_case for modules/functions/variables, PascalCase for classes
- JSON keys: Always snake_case (`table_id`, not `tableId`)
- Files: snake_case.py (e.g., `browser_manager.py`)

**Code Organization:**
- Domain-driven structure: `browser/`, `image_processing/`, `pattern_matching/`, `data/`, `ui/`, `orchestration/`, `utils/`
- Utilities in `utils/` directory
- Configuration in `config/` directory
- Tests mirror source structure

**Documentation Requirements:**
- Include docstrings for all classes and public methods
- Document thread safety requirements in docstrings
- Include table_id and timestamp in all error logs

**Format Rules (MANDATORY):**
- Timestamps: Always use `YYYY-MM-DD_HH-MM-SS` format (e.g., `"2026-01-06_14-30-00"`)
- JSON structure: Consistent across all table files
- Pattern validation: Use regex `^[BP]{3}-[BP](;[BP]{3}-[BP])*$` at input

### Development Workflow Rules

**Project Structure:**
- Follow exact directory structure as defined in architecture document
- Create all modules and files as specified in project structure section
- Maintain clear module boundaries (no cross-module dependencies except via defined interfaces)

**Implementation Sequence:**
1. Project Structure Setup
2. Browser Automation Layer
3. Image Processing Engine
4. Pattern Matching Engine
5. Data Persistence Layer
6. Multi-Table Orchestration
7. Error Recovery System
8. Desktop UI Framework

### Critical Don't-Miss Rules

**Thread Safety Violations (CRITICAL - DO NOT VIOLATE):**
- ❌ Direct UI updates from worker threads (must use queue)
- ❌ Shared data access without locks
- ❌ Blocking queue operations in UI thread (`queue.get()` instead of `queue.get_nowait()`)
- ❌ File operations without portalocker locking

**Naming Violations:**
- ❌ Mixed naming conventions (`getUserData()` vs `get_user_data()`)
- ❌ camelCase in Python code (`tableId` should be `table_id`)
- ❌ Different JSON key formats (`tableId` vs `table_id`)

**Format Violations:**
- ❌ Inconsistent timestamp formats (`2026-01-06T14:30:00Z` vs `2026-01-06_14-30-00`)
- ❌ Missing 17px canvas transform offset in click coordinates
- ❌ Pattern validation not using correct regex

**Error Handling Violations:**
- ❌ Errors in one table affecting other tables (must isolate per-table)
- ❌ Missing error logging with screenshots on failures
- ❌ Not following retry pattern (Try → Retry → Fallback → Alert → Pause)

**Edge Cases to Handle:**
- **Coordinate Management**: Validate canvas position every 10-20 rounds, recalibrate if drift >5px
- **Pattern Matching**: Handle no-match scenarios (return None), first match wins
- **Error Recovery**: Per-table error isolation, OCR fallback only for affected table
- **Page Refresh**: Pause all tables, save state, wait for reload, auto-resume

**Performance Gotchas:**
- CPU throttling: Reduce screenshot frequency if CPU > 80%
- EasyOCR is slower than template matching - monitor fallback usage
- Concurrent OCR operations: Ensure system handles multiple tables triggering OCR simultaneously

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**
- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

**Last Updated:** 2026-01-06
