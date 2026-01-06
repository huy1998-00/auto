# Project-Type Requirements

### Desktop Application Requirements

**Platform Support:**
- Windows, macOS, Linux (cross-platform desktop application)
- Python-based desktop UI using Tkinter (built-in) or PyQt5/PySide6

**Desktop Application Characteristics:**
- Standalone executable or Python script with dependencies
- No server infrastructure required
- Local data storage (JSON files)
- Real-time UI updates (500ms refresh rate)

**UI Framework Requirements:**
- Tkinter for basic UI (built-in, no external dependencies)
- PyQt5/PySide6 option for advanced features (optional)
- Real-time status display for all tables
- Pattern editor with validation
- History viewer with filtering
- Global and individual table controls
- Resource monitoring display

### Browser Automation Requirements

**Browser Automation Stack:**
- Playwright (Python) for browser automation
- Chromium browser instance
- Fixed window size (1920x1080)
- Window locking (disable resizing)
- Canvas element monitoring (`#layaCanvas`)

**Screenshot Requirements:**
- Region-only screenshots using coordinates (x, y, width, height)
- Direct screenshot capture from canvas at specified regions
- PIL Image objects for processing
- Screenshot frequency: Adaptive based on game phase (100ms-200ms)

### Image Processing Requirements

**Image Processing Stack:**
- OpenCV for template matching (primary method)
- PIL (Pillow) for image manipulation
- Tesseract (pytesseract) or EasyOCR for OCR fallback

**Template Matching Requirements:**
- Timer extraction from orange countdown box
- Score extraction from blue and red team display boxes
- Template matching for numbers 0-9
- Support for timer values 0-25
- Support for score values 0-999+

**OCR Fallback Requirements:**
- Triggered after 3 consecutive template matching failures
- Per-table fallback (doesn't affect other tables)
- Error logging with screenshots for debugging

### Data Persistence Requirements

**Storage Architecture:**
- Date-based folder structure: `data/sessions/YYYY-MM-DD_HH-MM-SS/`
- Per-table JSON files: `table_1.json` through `table_6.json`
- Session config JSON: `session_config.json` with global settings
- Continuous writing: Save every round until tool closes
- In-memory cache: Load all tables on startup, update cache each round, flush to JSON

**Data Schema:**
- Table JSON: table_id, session_start, patterns, rounds array, statistics
- Round object: round_number, timestamp, timer_start, blue_score, red_score, winner, decision_made, pattern_matched, result
- Session config: session_start, session_end, tables_active, global_patterns, settings

**Thread Safety:**
- File locking for thread-safe JSON writes
- Thread-safe operations for all shared data structures
- Concurrent write support for parallel table processing
