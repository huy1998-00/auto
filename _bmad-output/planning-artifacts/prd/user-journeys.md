# User Journeys

### Journey 1: First-Time Setup and Single Table Automation

**User:** New user discovering the tool for the first time

**Steps:**
1. User downloads and launches the tool
2. User sees desktop UI with empty table slots
3. User configures game URL and table region coordinates (or uses defaults)
4. User enters pattern rules (e.g., "BBP-P;BPB-B")
5. User clicks "Start" for table 1
6. System opens browser, navigates to game URL, waits for canvas load
7. System begins learning phase (observes first 3 rounds)
8. UI shows "Learning" status with rounds_watched counter
9. After 3 rounds, system transitions to active decision-making
10. System captures screenshots, extracts timer/scores, matches patterns, executes clicks
11. UI updates in real-time showing timer, last 3 rounds, pattern match, decision
12. User monitors automation and reviews history

**Success:** User successfully automates one table with pattern-based decisions

**Pain Points Addressed:**
- Manual clicking eliminated
- Pattern-based decisions applied consistently
- Real-time visibility into automation status

### Journey 2: Multi-Table Parallel Automation

**User:** Power user maximizing automation efficiency

**Steps:**
1. User has successfully run single table automation
2. User adds additional tables (up to 6) with their region coordinates
3. User configures patterns for each table (can be same or different)
4. User clicks "Start All" to begin parallel automation
5. System processes all active tables simultaneously
6. Each table maintains independent state (round history, learning phase, patterns)
7. System captures region screenshots for each active table in parallel
8. Each table analyzes its own screenshot and makes independent decisions
9. UI displays real-time status for all 6 tables
10. User can pause individual tables while others continue
11. System saves round data to separate JSON files per table
12. User reviews history viewer showing all tables' performance

**Success:** User runs 6 tables simultaneously with independent pattern matching and decision logic

**Pain Points Addressed:**
- Manual management of multiple tables eliminated
- Maximum automation throughput achieved
- Independent control per table maintained

### Journey 3: Error Recovery and System Resilience

**User:** User experiencing common error scenarios

**Steps:**
1. User is running automation on multiple tables
2. Page refresh occurs (game website auto-refreshes)
3. System detects page refresh by monitoring URL/DOM
4. System pauses all tables and saves current state to JSON
5. System waits for game to reload (canvas element available)
6. System auto-resumes all tables after reload
7. System restores state from JSON (round history, patterns)
8. Automation continues seamlessly

**Alternative Scenario:**
1. Network lag causes screenshot timeout for one table
2. System retries with exponential backoff (1s, 2s, 4s)
3. If retries fail, system falls back to OCR for that table
4. Other tables continue processing normally
5. Failed table is automatically paused if 3 consecutive timeouts occur
6. User is notified via UI with error details
7. User can manually resume the paused table

**Success:** System automatically recovers from errors without user intervention or data loss

**Pain Points Addressed:**
- Manual recovery from page refreshes eliminated
- Network issues handled gracefully
- Error isolation prevents cascade failures

### Journey 4: Pattern Performance Analysis

**User:** User analyzing pattern effectiveness

**Steps:**
1. User has run automation for multiple sessions
2. User opens history viewer in desktop UI
3. User selects table and date range
4. UI displays last 20-50 rounds with success/failure indicators
5. User reviews pattern matches, decisions made, and outcomes
6. User sees statistics: total_rounds, correct_decisions, accuracy percentage
7. User identifies patterns with low accuracy
8. User edits patterns in pattern editor UI
9. User validates pattern format (regex validation)
10. User saves updated patterns
11. User restarts automation with improved patterns
12. User monitors improved accuracy in real-time

**Success:** User optimizes patterns based on historical performance data

**Pain Points Addressed:**
- Pattern effectiveness analysis enabled
- Data-driven pattern optimization supported
- Historical performance visibility provided
