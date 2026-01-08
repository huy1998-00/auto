# Visual Coordinate Picker - Complete Usage Guide

**How to use the Visual Coordinate Configuration feature on a real game website**

---

## Overview

The Visual Coordinate Picker allows you to configure table regions, button positions, and score/timer areas **without any technical knowledge** or manual coordinate entry. Simply click buttons and drag/click on the browser window!

**No DevTools needed!** ✅  
**No manual coordinate entry!** ✅  
**Visual drag-and-click interface!** ✅

---

## Prerequisites

Before using the coordinate picker:

1. ✅ **Application is running** - Desktop UI window is open
2. ✅ **Browser is opened** - Click "1. Open Browser" in the main window
3. ✅ **Game website is loaded** - Browser shows your game page with all tables visible
4. ✅ **Game is ready** - All game elements (tables, buttons, timers) are visible

**Important:** The coordinate picker works **directly on the opened browser window**. Make sure the browser is open and showing your game before starting!

---

## Step-by-Step Workflow

### Step 1: Open Browser and Navigate to Game

1. In the **main application window**, enter your game URL:
   ```
   Example: https://your-game-website.com/game
   ```

2. Click **"1. Open Browser"** button
   - Browser window opens automatically
   - Browser navigates to your game URL
   - Wait for game to fully load

3. Verify browser status shows **"✓ Opened"**

4. **Position the browser window** so you can see both:
   - The browser window (with your game)
   - The desktop application window (with configuration buttons)

---

### Step 2: Open Table Configuration Window

1. In the **main application window**, click **"Configure Tables"** button
   - This button is only enabled after browser is opened

2. A new window opens with two tabs:
   - **Guide Tab**: Instructions (read this first!)
   - **Configuration Tab**: Where you'll pick coordinates

3. Switch to the **"Configuration"** tab

---

### Step 3: Select a Table

1. In the **Configuration** tab, find the **"Select Table"** dropdown
2. Select **Table 1** (start with the first table)
3. You'll configure all coordinates for this table

---

### Step 4: Pick Table Region (Drag to Select)

**What this does:** Defines the area where the entire table is located

1. Click the **"📐 Pick Table Region"** button

2. **An info dialog appears** - Click "OK"

3. **Look at the browser window** - You'll see:
   - ✅ Green tinted overlay covering the entire browser
   - ✅ White instruction panel in top-left corner
   - ✅ Crosshair cursor

4. **Drag to select the table area:**
   - Click and hold mouse button at the **top-left corner** of the table
   - Drag mouse to the **bottom-right corner** of the table
   - You'll see a **bright green rectangle** showing your selection
   - Release mouse button when you've selected the entire table

5. **Coordinates are automatically captured!**
   - The overlay disappears
   - Form fields are automatically filled with: `x`, `y`, `width`, `height`

**Example:** If your table is in the top-left area, drag from top-left to bottom-right of that table.

---

### Step 5: Pick Button Positions (Click to Capture)

**What this does:** Defines where the game buttons are located (Blue, Red, Confirm, Cancel)

#### Pick Blue Button:

1. Click **"🔵 Pick Blue"** button
2. **Look at the browser window** - Green overlay appears
3. **Click directly on the Blue button** in the game
4. **Red marker appears** briefly - coordinates captured!
5. Form fields `blue_x` and `blue_y` are automatically filled

#### Pick Red Button:

1. Click **"🔴 Pick Red"** button
2. Click directly on the **Red button** in the browser
3. Coordinates captured automatically

#### Pick Confirm Button:

1. Click **"✓ Pick Confirm"** button
2. Click directly on the **Confirm (✓) button** in the browser
3. Coordinates captured automatically

#### Pick Cancel Button:

1. Click **"✗ Pick Cancel"** button
2. Click directly on the **Cancel (✗) button** in the browser
3. Coordinates captured automatically

**Tip:** Make sure you click the exact center of each button for best accuracy!

---

### Step 6: Pick Timer Region (Drag to Select)

**What this does:** Defines the area where the countdown timer is displayed

1. Click **"⏱️ Pick Timer"** button
2. **Look at the browser window** - Green overlay appears
3. **Drag to select the timer area:**
   - Click and hold at the **top-left** of the timer display
   - Drag to the **bottom-right** of the timer display
   - Release mouse button
4. Form fields `timer_x`, `timer_y`, `timer_w`, `timer_h` are automatically filled

**Example:** The timer is usually displayed in an orange box. Select the entire orange box area.

---

### Step 7: Pick Blue Score Region (Drag to Select)

**What this does:** Defines the area where the Blue team score is displayed

1. Click **"🔵 Pick Blue Score"** button
2. **Look at the browser window** - Green overlay appears
3. **Drag to select the blue score area:**
   - Click and hold at the **top-left** of the blue score display
   - Drag to the **bottom-right** of the blue score display
   - Release mouse button
4. Form fields `blue_score_x`, `blue_score_y`, `blue_score_w`, `blue_score_h` are automatically filled

---

### Step 8: Pick Red Score Region (Drag to Select)

**What this does:** Defines the area where the Red team score is displayed

1. Click **"🔴 Pick Red Score"** button
2. **Look at the browser window** - Green overlay appears
3. **Drag to select the red score area:**
   - Click and hold at the **top-left** of the red score display
   - Drag to the **bottom-right** of the red score display
   - Release mouse button
4. Form fields `red_score_x`, `red_score_y`, `red_score_w`, `red_score_h` are automatically filled

---

### Step 9: Review and Validate

1. **Check all coordinate values** in the form fields
   - Make sure all fields are filled (no zeros unless intentional)
   - Verify coordinates look reasonable

2. Click **"Validate"** button
   - Checks for errors
   - Shows validation results

3. **Adjust manually if needed:**
   - You can edit coordinate values directly in the form fields
   - Re-pick if coordinates seem wrong

---

### Step 10: Save Configuration

1. Click **"Save"** button
2. Success message appears: "Coordinates saved for Table 1"
3. Coordinates are saved to `config/table_regions.yaml`

---

### Step 11: Repeat for Other Tables

1. Select **Table 2** from the dropdown
2. Repeat Steps 4-10 for Table 2
3. Continue for Tables 3, 4, 5, 6 as needed

**Tip:** Start with Table 1, test it works, then configure the rest!

---

## Visual Guide: What You'll See

### When Picker is Active:

```
┌─────────────────────────────────────────┐
│ Browser Window (with game)              │
│                                         │
│  ┌─────────────────────────────┐       │
│  │ 📍 Coordinate Picker        │  ← Instruction panel
│  │ Drag to select TABLE region │       │
│  │ Mode: TABLE                  │       │
│  │ • Drag to select area       │       │
│  │ • ESC to cancel             │       │
│  └─────────────────────────────┘       │
│                                         │
│  ┌──────────────┐                      │
│  │              │                      │
│  │   TABLE      │  ← Green overlay     │
│  │   AREA       │     covers entire    │
│  │              │     browser          │
│  └──────────────┘                      │
│                                         │
│  ┌──────────────┐                      │
│  │              │                      │
│  │  SELECTION   │  ← Bright green      │
│  │  RECTANGLE   │     rectangle shows   │
│  │              │     your selection    │
│  └──────────────┘                      │
└─────────────────────────────────────────┘
```

### After Selection:

- Overlay disappears
- Form fields are filled automatically
- You can see the captured coordinates

---

## Tips for Best Results

### ✅ DO:

1. **Start with Table 1** - Test one table first before configuring all 6
2. **Make sure game is fully loaded** - Wait for all elements to appear
3. **Select entire areas** - For regions, include some padding around the element
4. **Click button centers** - For buttons, click the exact center
5. **Save frequently** - Save after each table configuration
6. **Validate before saving** - Always click "Validate" first

### ❌ DON'T:

1. **Don't pick while game is animating** - Wait for stable state
2. **Don't select overlapping areas** - Make sure table regions don't overlap
3. **Don't skip validation** - Always validate before saving
4. **Don't close browser** - Keep browser open while configuring

---

## Troubleshooting

### Problem: Overlay doesn't appear

**Solutions:**
- ✅ Make sure browser is opened first (click "1. Open Browser")
- ✅ Check browser status shows "✓ Opened"
- ✅ Make sure game page is fully loaded
- ✅ Try clicking the pick button again

### Problem: Coordinates seem wrong

**Solutions:**
- ✅ Re-pick the coordinates (click the pick button again)
- ✅ Make sure you're selecting the correct area
- ✅ Check that game elements are visible
- ✅ Adjust manually in form fields if needed

### Problem: Button clicks miss the target

**Solutions:**
- ✅ Re-pick button coordinates (click center of button)
- ✅ Make sure you clicked the exact button, not nearby
- ✅ Check button coordinates in form fields

### Problem: Timer/Score extraction fails

**Solutions:**
- ✅ Re-pick timer/score regions (include entire display area)
- ✅ Make sure region includes all digits
- ✅ Add some padding around the numbers

### Problem: Picker closes immediately

**Solutions:**
- ✅ This was fixed in latest version - make sure you have latest code
- ✅ If still happens, try clicking pick button again
- ✅ Check browser console for errors (F12)

---

## Keyboard Shortcuts

- **ESC** - Cancel coordinate picking (closes overlay)
- **F12** - Open browser DevTools (for debugging, not needed for picking)

---

## What Happens Behind the Scenes

When you use the coordinate picker:

1. **JavaScript overlay is injected** into the browser page
2. **Green overlay appears** covering the entire browser
3. **Your mouse interactions** are captured:
   - For regions: Mouse drag creates selection rectangle
   - For buttons: Mouse click captures point coordinates
4. **Coordinates are calculated** relative to the canvas element
5. **Form fields are updated** automatically
6. **Overlay is removed** after capture

**You don't need to understand this** - it all happens automatically! Just drag and click! 🎯

---

## Example Workflow Summary

```
1. Open Application
   ↓
2. Enter Game URL → Click "1. Open Browser"
   ↓
3. Browser Opens → Game Loads
   ↓
4. Click "Configure Tables"
   ↓
5. Select Table 1
   ↓
6. Click "📐 Pick Table Region" → Drag to select table
   ↓
7. Click "🔵 Pick Blue" → Click blue button
   ↓
8. Click "🔴 Pick Red" → Click red button
   ↓
9. Click "✓ Pick Confirm" → Click confirm button
   ↓
10. Click "✗ Pick Cancel" → Click cancel button
   ↓
11. Click "⏱️ Pick Timer" → Drag to select timer area
   ↓
12. Click "🔵 Pick Blue Score" → Drag to select blue score
   ↓
13. Click "🔴 Pick Red Score" → Drag to select red score
   ↓
14. Click "Validate" → Check for errors
   ↓
15. Click "Save" → Coordinates saved!
   ↓
16. Repeat for Tables 2-6
```

---

## Next Steps After Configuration

After configuring all coordinates:

1. ✅ **Set Betting Patterns** - Use Pattern Editor in main window
2. ✅ **Start Automation** - Click "Start Automation" button
3. ✅ **Monitor Status** - Watch table status display
4. ✅ **Review Logs** - Check application logs for any issues

---

## File Location

Coordinates are saved to:
```
mini-game-automation/config/table_regions.yaml
```

You can edit this file manually if needed, or use "Load from Config" to reload saved coordinates.

---

**Last Updated:** 2026-01-07  
**Status:** ✅ All coordinate picker features fully working!
