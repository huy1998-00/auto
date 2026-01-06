# Mini-Game Website Automation & Pattern Tracking Tool

A desktop automation application that automates pattern-based game decisions using Playwright browser automation and OpenCV image processing.

## Features

- **Single Table Automation**: Automated screenshot capture, timer/score extraction, and click execution
- **Multi-Table Support**: Up to 6 tables running in parallel
- **Pattern Matching**: Priority-based pattern matching with user-defined rules
- **Data Persistence**: Session-based JSON storage with continuous writing
- **Error Recovery**: Automatic retry logic and OCR fallback

## Requirements

- Python 3.8+
- Playwright browser binaries
- OpenCV for image processing
- EasyOCR for fallback text extraction

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install Python packages
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### 2. Configure Application (All in UI!)

**No file editing needed!** Everything can be configured in the UI:

- **Game URL**: Enter in UI field → Click "Open Browser" (automatically saved to `.env`)
- **Table Coordinates**: Use visual coordinate picker in UI (drag/click to select)
- **Betting Patterns**: Enter in UI pattern editor (with real-time validation)

**OR** configure manually via files if preferred.

### 3. Run Application

```bash
python -m automation.main --url https://your-game-url.com
```

**For detailed installation instructions, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**

## Usage

### With Desktop UI (Recommended)

Simply run:
```bash
python -m automation.main
```

The UI window will open with:
- **Game URL input** - Set your game URL directly in the UI
- **Pattern Editor** - Configure betting patterns with validation
- **Table Configuration** - Visual editor for table coordinates with step-by-step guide
- **Real-time Status** - Monitor all tables with live updates
- **Resource Monitor** - CPU and memory usage display
- **Application Logs** - Real-time log viewer

**See [UI_USAGE_GUIDE.md](UI_USAGE_GUIDE.md) for detailed UI instructions.**

### Command Line Options

```bash
# Specify game URL
python -m automation.main --url https://your-game-url.com

# Run without UI (command line only)
python -m automation.main --no-ui --url https://your-game-url.com

# Run in headless mode
python -m automation.main --headless

# Debug logging
python -m automation.main --log-level DEBUG
```

### Stop Application

**With UI:** Click "Stop Automation" button or close the window

**Without UI:** Press `Ctrl+C` to stop gracefully

## Project Structure

```
mini-game-automation/
├── src/automation/
│   ├── browser/          # Browser automation (Playwright)
│   ├── image_processing/ # OpenCV template matching & OCR
│   ├── pattern_matching/ # Pattern validation and matching
│   ├── data/            # JSON persistence and caching
│   ├── ui/              # Desktop UI (Tkinter)
│   ├── utils/           # Shared utilities
│   └── orchestration/   # Multi-table coordination
├── tests/               # Test suite (mirrors src structure)
├── config/              # Configuration files
├── data/sessions/       # Session data storage
└── logs/               # Application logs
```

## Configuration

### Using the UI (Recommended)

**Game URL:**
- Enter URL in the main window's "Game URL" field
- Click "Save URL" button

**Betting Patterns:**
- Use the Pattern Editor in the UI
- Select table (1-6)
- Enter patterns with validation
- Click "Save Pattern"

**Table Coordinates:**
- Click "Configure Tables" button
- Read the Guide tab for instructions
- Enter coordinates in Configuration tab
- Click "Validate" then "Save"

**See [UI_USAGE_GUIDE.md](UI_USAGE_GUIDE.md) for detailed instructions.**

### Manual Configuration (Alternative)

**Table Regions (`config/table_regions.yaml`):**

Define table region coordinates for screenshot capture:

```yaml
tables:
  1:
    x: 100
    y: 200
    width: 300
    height: 250
```

**Patterns (`config/default_patterns.yaml`):**

Define default patterns for automation:

```yaml
default_patterns: "BBP-P;BPB-B;BBB-P"
```

## Pattern Format

Patterns use the format `[last 3 rounds]-[decision]`:
- `B` = Red team
- `P` = Blue team

Example: `BBP-P` means "if last 3 rounds were Red, Red, Blue, then bet on Blue"

Multiple patterns are separated by semicolons: `BBP-P;BPB-B;BBB-P`

## Development

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src/automation tests/
```

## License

See LICENSE file for details.
