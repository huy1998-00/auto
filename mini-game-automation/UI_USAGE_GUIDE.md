# UI Usage Guide

Complete guide for using the Desktop UI to configure and run the automation tool.

---

## Starting the Application

### With UI (Default)

Simply run:
```bash
python -m automation.main
```

The UI window will open automatically.

### Without UI (Command Line Only)

```bash
python -m automation.main --no-ui --url https://your-game-url.com
```

---

## Main Window Overview

The main window has three main sections:

1. **Top Section**: Configuration and Controls
2. **Left Panel**: Pattern Editor and Table Status
3. **Right Panel**: Resource Monitor and Logs

---

## Step 1: Set Game URL and Open Browser

1. In the **Configuration** section at the top
2. Enter your game URL in the "Game URL" field
3. Click **"1. Open Browser"** button
4. Browser will open and navigate to your game URL
5. Wait for browser status to show "✓ Opened"

**Example:**
```
Game URL: https://your-game-website.com/game
```

**Important:** All automation logic happens in this opened browser. Keep it open!

---

## Step 2: Configure Table Coordinates

### Opening the Configuration Window

**Prerequisite:** Browser must be opened first (Step 1)

1. Click **"Configure Tables"** button in the Configuration section
   - Button is enabled only after browser is opened
2. A new window opens with two tabs:
   - **Guide**: Step-by-step instructions (updated for opened browser)
   - **Configuration**: Coordinate editor

### Using the Guide Tab

The Guide tab provides detailed instructions for configuring coordinates:
- **Visual Coordinate Picker** - Easy drag-and-click method (NO DevTools needed!)
- Manual entry method (if you prefer)
- Troubleshooting tips

**Read this guide first** before configuring coordinates!

**Tip:** Use the visual picker buttons - just click "Pick" and drag/click on the browser!

### Configuring Coordinates

1. Go to the **"Configuration"** tab
2. Select a table (1-6) from the dropdown
3. **Use Visual Coordinate Picker** (EASIEST METHOD!):

   **📐 Pick Table Region:**
   - Click "📐 Pick Table Region" button
   - Visual overlay appears on browser
   - Drag mouse to select entire table area
   - Release mouse - coordinates auto-filled!

   **Button Positions:**
   - Click "🔵 Pick Blue" → Click blue button in browser
   - Click "🔴 Pick Red" → Click red button in browser
   - Click "✓ Pick Confirm" → Click confirm button in browser
   - Click "✗ Pick Cancel" → Click cancel button in browser
   - Red marker appears - coordinates auto-filled!

   **Timer & Score Regions:**
   - Click "⏱️ Pick Timer" → Drag to select timer area
   - Click "🔵 Pick Blue Score" → Drag to select blue score area
   - Click "🔴 Pick Red Score" → Drag to select red score area
   - Coordinates auto-filled!

4. **Review & Adjust**: Check captured coordinates, adjust manually if needed
5. Click **"Validate"** to check coordinates
6. Click **"Save"** to save changes
7. Repeat for each table (1-6)

### Manual Entry (Alternative Method)

If you prefer manual entry or need to adjust:
- Enter `x`, `y`, `width`, `height` values directly in form fields
- Coordinates are relative to canvas (#layaCanvas)
- Button coordinates are relative to table region

### Loading from Config File

- Click **"Load from Config"** to load existing coordinates from `config/table_regions.yaml`
- Useful if you've already configured coordinates manually

---

## Step 3: Set Betting Patterns

### Pattern Editor

1. In the **Pattern Editor** section (left panel)
2. Select a table (1-6) from the dropdown
3. Enter your patterns in the text field

### Pattern Format

**Format:** `[last 3 rounds]-[decision]`

**Characters:**
- `B` = Red team (Banker)
- `P` = Blue team (Player)

**Examples:**
- `BBP-P` = If last 3 rounds were Red, Red, Blue → bet Blue
- `BPB-B` = If last 3 rounds were Red, Blue, Red → bet Red
- `PPP-B` = If last 3 rounds were Blue, Blue, Blue → bet Red

**Multiple Patterns:**
Separate with semicolons:
```
BBP-P;BPB-B;BBB-P;PPP-B
```

### Using the Pattern Editor

1. **Enter patterns** in the text field
2. Click **"Validate"** to check format
   - ✓ Green checkmark = Valid
   - ✗ Red error = Invalid (see error message)
3. Click **"Save Pattern"** to save for selected table
4. Click **"Help"** for detailed format explanation

### Pattern Matching Logic

- Patterns are matched **in order** (first match wins)
- System matches last 3 rounds against patterns
- If no pattern matches, no bet is placed
- Each table can have different patterns

---

## Step 4: Start Automation

### Starting

**Prerequisites:**
1. ✓ Browser is opened (Step 1)
2. ✓ At least one table is configured (Step 2)
3. ✓ Patterns are set (Step 3)

**Then:**
1. Click **"Start Automation"** button

The application will:
- Use the already-opened browser
- Add configured tables to automation
- Start tracking and processing
- Begin making click decisions based on patterns

**Note:** All logic (tracking, coordinate setup, click execution) happens in the opened browser window.

### Monitoring Status

**Table Status Display** (left panel):
- Shows status for all 6 tables
- Updates every 500ms
- Displays:
  - Status: 🟢 Active, 🟡 Learning, 🔴 Paused, ⚪ Stuck
  - Timer: Current countdown value
  - Last 3 Rounds: Recent round history (e.g., "BBP")
  - Pattern Match: Which pattern matched
  - Decision: What bet was made (blue/red)

**Resource Monitor** (right panel):
- CPU usage percentage
- Memory usage percentage
- Shows throttling status if CPU > 80%

**Application Logs** (right panel):
- Real-time log messages
- Errors and warnings
- Round completions
- Pattern matches

### Controlling Tables

**Per-Table Controls:**
- Click **"Pause"** to pause a specific table
- Click **"Resume"** to resume a paused table
- Other tables continue running independently

**Global Controls:**
- **"Stop Automation"**: Stops all tables and closes browser
- All data is saved before stopping

---

## Step 5: Stop Automation

### Stopping

1. Click **"Stop Automation"** button
2. Application will:
   - Stop all table processing
   - Save all data to JSON files
   - Close browser instance
   - Update session end timestamp

### Closing Window

- Click the X button or press Alt+F4
- If automation is running, you'll be prompted to stop first
- All data is saved automatically

---

## UI Features Summary

### Configuration Section
- ✅ Game URL input and save
- ✅ Start/Stop automation buttons
- ✅ Configure Tables button

### Pattern Editor
- ✅ Table selection (1-6)
- ✅ Pattern input with validation
- ✅ Real-time validation feedback
- ✅ Help button with format guide
- ✅ Save patterns per table

### Table Status Display
- ✅ Real-time status for all 6 tables
- ✅ Timer, rounds, pattern, decision display
- ✅ Per-table pause/resume controls
- ✅ Color-coded status indicators

### Table Configuration Window
- ✅ Step-by-step guide tab
- ✅ Coordinate editor tab
- ✅ Load from config file
- ✅ Validate coordinates
- ✅ Save coordinates per table

### Resource Monitor
- ✅ CPU usage display
- ✅ Memory usage display
- ✅ Throttling status indicator

### Application Logs
- ✅ Real-time log display
- ✅ Timestamped messages
- ✅ Scrollable log viewer

---

## Workflow Summary

**Correct Order:**
1. **Enter Game URL** → Click "1. Open Browser"
2. **Browser Opens** → Status shows "✓ Opened"
3. **Configure Tables** → Click "Configure Tables" → Enter coordinates → Save
4. **Set Patterns** → Select table → Enter patterns → Save Pattern
5. **Start Automation** → Click "Start Automation"
6. **Monitor** → Watch status display and logs
7. **Stop** → Click "Stop Automation" when done

**All automation happens in the opened browser window!**

## Quick Reference

### Pattern Format
```
BBP-P;BPB-B;BBB-P
```
- `B` = Red team
- `P` = Blue team
- Semicolon separates multiple patterns

### Status Indicators
- 🟢 **Active**: Table is running normally
- 🟡 **Learning**: Observing first 3 rounds
- 🔴 **Paused**: Manually paused
- ⚪ **Stuck**: Error recovery failed (3+ consecutive failures)
- ⚪ **Stopped**: Not running

### Keyboard Shortcuts
- **Ctrl+C**: Stop automation (if running)
- **Alt+F4**: Close window
- **F12**: Open browser DevTools (for finding coordinates)
- **Ctrl+Shift+C**: Select element tool in DevTools

---

## Troubleshooting

### UI Not Opening

**Problem:** Window doesn't appear when running

**Solutions:**
- Check if Tkinter is installed: `python -c "import tkinter"`
- On Linux, install: `sudo apt-get install python3-tk`
- Try running with `--no-ui` flag to test command-line mode

### Pattern Validation Fails

**Problem:** Pattern shows as invalid

**Solutions:**
- Check format: Must be `XXX-X` (3 chars, dash, 1 char)
- Only use `B` and `P` characters
- Multiple patterns separated by semicolons
- Click "Help" button for examples

### Coordinates Not Saving

**Problem:** Coordinates don't persist

**Solutions:**
- Check file permissions on `config/table_regions.yaml`
- Ensure you click "Save" button (not just Validate)
- Check application logs for error messages

### Status Not Updating

**Problem:** Table status doesn't refresh

**Solutions:**
- Ensure automation is started
- Check if tables are added (see logs)
- Verify browser is open and game is loaded
- Check application logs for errors

---

## Tips for Best Results

1. **Start with One Table**: Configure and test Table 1 first before adding more
2. **Use Guide Tab**: Read the coordinate guide before configuring
3. **Validate Patterns**: Always validate patterns before saving
4. **Monitor Logs**: Watch the log panel for errors and warnings
5. **Check Status**: Use status display to verify tables are working
6. **Save Frequently**: Save coordinates and patterns after each change

---

**Last Updated:** 2026-01-06
