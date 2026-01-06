# Installation & Usage Guide

Complete step-by-step guide to install, configure, and run the Mini-Game Automation Tool.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher** installed
- **Windows, macOS, or Linux** operating system
- **Internet connection** (for downloading dependencies)

Check Python version:
```bash
python --version
# Should show Python 3.8.x or higher
```

---

## Step 1: Navigate to Project Directory

Open terminal/command prompt and navigate to the project folder:

```bash
cd "C:\Users\Development 2\Desktop\auto\mini-game-automation"
```

Or if you're already in the workspace:
```bash
cd mini-game-automation
```

---

## Step 2: Create Virtual Environment

Create an isolated Python environment to avoid conflicts:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verify activation:** You should see `(venv)` at the start of your command prompt.

---

## Step 3: Install Python Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- playwright (browser automation)
- opencv-python (image processing)
- pillow (image manipulation)
- easyocr (OCR fallback)
- portalocker (file locking)
- psutil (system monitoring)
- pyyaml (configuration)
- pytest (testing)

**Expected output:** Should show "Successfully installed..." for all packages.

---

## Step 4: Install Playwright Browser

Install Chromium browser for Playwright:

```bash
playwright install chromium
```

**Note:** This downloads ~200MB browser binaries. First-time installation may take a few minutes.

**Verify installation:**
```bash
playwright --version
```

---

## Step 5: Configure Application

### 5.1: Set Game URL

Edit `.env` file (or create from `.env.example`):

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
notepad .env
```

**macOS/Linux:**
```bash
cp .env.example .env
nano .env
```

Set your game URL:
```
GAME_URL=https://your-game-url.com
```

### 5.2: Configure Table Regions

Edit `config/table_regions.yaml` to match your game layout:

- Update `x`, `y`, `width`, `height` for each table (1-6)
- Update button coordinates (`blue`, `red`, `confirm`, `cancel`)
- Update timer and score region coordinates

**Note:** You may need to inspect the game page to get exact coordinates.

### 5.3: Set Default Patterns

Edit `config/default_patterns.yaml`:

```yaml
default_patterns: "BBP-P;BPB-B;BBB-P"
```

Pattern format: `[last 3 rounds]-[decision]`
- `B` = Red team (Banker)
- `P` = Blue team (Player)

---

## Step 6: Prepare Number Templates (Optional)

For template matching to work, you need number templates (0-9):

1. Capture screenshots of numbers 0-9 from the game
2. Save them as PNG files in `src/automation/image_processing/templates/`
3. Name them: `0.png`, `1.png`, `2.png`, ... `9.png`

**Note:** If templates are missing, the system will use OCR fallback automatically.

---

## Step 7: Run the Application

### Basic Run

```bash
python -m automation.main
```

### With Command Line Arguments

```bash
# Specify game URL
python -m automation.main --url https://your-game-url.com

# Run in headless mode (no browser window)
python -m automation.main --headless

# Set log level
python -m automation.main --log-level DEBUG

# Combine options
python -m automation.main --url https://your-game-url.com --log-level INFO
```

### Using Environment Variables

Set environment variable and run:
```bash
# Windows
set GAME_URL=https://your-game-url.com
python -m automation.main

# macOS/Linux
export GAME_URL=https://your-game-url.com
python -m automation.main
```

---

## Step 8: Monitor Application

### Console Output

The application will show:
- Initialization status
- Table registration
- Screenshot capture logs
- Pattern matches and decisions
- Round completions
- Error messages (if any)

### Log Files

Check `logs/automation.log` for detailed logs:
```bash
# Windows
type logs\automation.log

# macOS/Linux
tail -f logs/automation.log
```

### Session Data

Session data is saved in `data/sessions/YYYY-MM-DD_HH-MM-SS/`:
- `table_1.json` through `table_6.json` - Per-table round data
- `session_config.json` - Session configuration

---

## Step 9: Stop the Application

### Graceful Shutdown

Press `Ctrl+C` in the terminal to stop the application gracefully.

The application will:
- Stop all table processing
- Flush remaining data to JSON files
- Close browser instance
- Save session end timestamp

### Force Stop

If the application doesn't respond:
- Close the terminal window
- Or use Task Manager (Windows) / Activity Monitor (macOS) to kill Python process

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**
- Ensure Python is installed and in PATH
- Use `python3` instead of `python` on macOS/Linux
- Check: `python --version`

### Issue: "pip not found"

**Solution:**
- Install pip: `python -m ensurepip --upgrade`
- Or use: `python -m pip install -r requirements.txt`

### Issue: "Playwright browser not found"

**Solution:**
```bash
playwright install chromium
playwright install-deps chromium  # Install system dependencies
```

### Issue: "ModuleNotFoundError"

**Solution:**
- Ensure virtual environment is activated (`(venv)` in prompt)
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: "EasyOCR model download"

**Solution:**
- First run will download EasyOCR models (~100MB)
- Ensure internet connection
- Wait for download to complete

### Issue: "Canvas element not found"

**Solution:**
- Check game URL is correct
- Ensure game page is fully loaded
- Verify canvas selector `#layaCanvas` exists on page
- Check browser console for errors

### Issue: "Template matching fails"

**Solution:**
- Add number templates (0-9.png) to `src/automation/image_processing/templates/`
- System will automatically use OCR fallback if templates missing
- Check `error_screenshots/` folder for debugging images

### Issue: "Permission denied" (file locking)

**Solution:**
- Ensure no other instance is running
- Check file permissions on `data/sessions/` directory
- Close any file explorers viewing session folders

---

## Testing the Application

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/browser/test_browser_manager.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest --cov=src/automation tests/
```

### Manual Testing Checklist

1. ✅ Application starts without errors
2. ✅ Browser opens and navigates to game URL
3. ✅ Canvas element is detected
4. ✅ Tables are registered successfully
5. ✅ Screenshots are captured
6. ✅ Timer/score extraction works
7. ✅ Pattern matching returns decisions
8. ✅ Clicks are executed (if timer > 6)
9. ✅ Round data is saved to JSON
10. ✅ Application stops gracefully

---

## Quick Start Summary

```bash
# 1. Navigate to project
cd mini-game-automation

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install browser
playwright install chromium

# 5. Configure (edit .env and config files)
# Set GAME_URL in .env
# Update table_regions.yaml

# 6. Run application
python -m automation.main --url https://your-game-url.com

# 7. Stop with Ctrl+C
```

---

## Next Steps

After successful installation:

1. **Configure table regions** - Match coordinates to your game layout
2. **Add number templates** - Improve template matching accuracy
3. **Set patterns** - Define your betting patterns
4. **Test with one table** - Start with single table before adding more
5. **Monitor logs** - Check `logs/automation.log` for issues
6. **Review session data** - Check `data/sessions/` for round history

---

## Getting Help

If you encounter issues:

1. Check `logs/automation.log` for error details
2. Review error screenshots in `error_screenshots/` folder
3. Verify configuration files are correct
4. Ensure all dependencies are installed
5. Check Python version compatibility (3.8+)

---

## Common Commands Reference

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Deactivate virtual environment
deactivate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt

# Run application
python -m automation.main

# Run with debug logging
python -m automation.main --log-level DEBUG

# Run tests
pytest tests/

# Check Python version
python --version

# Check installed packages
pip list

# Check Playwright version
playwright --version
```

---

**Last Updated:** 2026-01-06
