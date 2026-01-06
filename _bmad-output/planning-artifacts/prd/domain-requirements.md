# Domain Requirements

### Game Mechanics Domain

**Game Rules:**
- Two teams: Red (encoded as "B") and Blue (encoded as "P")
- Countdown timer: 15 or 25 seconds displayed in orange box
- Timer counts DOWN: Starts at 15 or 25, counts down to 0
- When timer reaches 0, round ends and timer resets to 15 or 25 (new round starts)
- Clickable only when timer > 6 (values 7-25 are clickable)
- When timer ≤ 6 (values 6, 5, 4, 3, 2, 1, 0), it's countdown phase, not clickable
- Two-phase clicking process:
  - Phase 1: Choose team (click blue or red button)
  - Phase 2: Confirm (click ✓ tick) or Cancel (click ✗ tick)
  - Delay between phases: 50-100ms (wait for confirmation UI to appear)
- Pattern format: `[last 3 rounds]-[decision]` (e.g., "BBP-P")
- Multiple patterns: Semicolon-separated (e.g., "BBP-P;BPB-B;BBB-P")

**Domain Constraints:**
- Canvas transform offset: 17px horizontal offset must be accounted for in click coordinates
- Button coordinates are relative to table region, not absolute to page
- All 6 tables displayed on same page in single browser instance
- Global scoreboard (yellow section) shared across all tables

### Automation Domain

**Automation Rules:**
- 3-round learning phase per table before making decisions
- Pattern matching: Match last 3 rounds against user-defined patterns
- Decision logic: B = Red team, P = Blue team
- Timer validation: Only click when timer > 6
- Adaptive screenshot frequency based on game phase
- Region-only screenshots: Individual screenshots taken directly for each table's region
- Inactive/paused tables are skipped (no screenshot taken)

**Domain Constraints:**
- Maximum 6 tables (hard limit)
- Single Playwright browser instance
- Thread-safe operations required for parallel processing
- Continuous data writing until tool closes
