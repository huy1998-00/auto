# Logical Conflicts and Questions - Epic Review

## Critical Conflicts Identified

### 1. **Epic 1 vs Multi-Table Architecture Conflict**

**Issue:** Epic 1 is titled "Single Table Automation" but Story 1.1 mentions "all 6 tables displayed on the same page". This creates confusion about whether Epic 1 handles single table logic or already assumes multi-table setup.

**Question:** Should Epic 1 focus on:
- Option A: Single table logic that works when only 1 table is active (even if page shows 6)?
- Option B: Table processing logic that works for any table (1-6), assuming multi-table architecture from start?

**Current State:** Story 1.1 says screenshot includes all 6 tables, but Epic 1 stories don't mention table region extraction.

---

### 2. **Screenshot Frequency Logic Conflict**

**Issue:** Story 1.12 (Adaptive Screenshot Frequency) says:
- 200ms when timer > 6
- 100ms when timer ≤ 6

But with all 6 tables on ONE page, we take ONE screenshot that contains all tables. Each table has its own timer, so they might be in different phases.

**Question:** How should screenshot frequency work?
- Option A: Use the FASTEST table's timer (if any table has timer ≤ 6, use 100ms; otherwise 200ms)?
- Option B: Use the SLOWEST table's timer?
- Option C: Fixed frequency regardless of individual table timers?
- Option D: Take separate screenshots per table region (but this contradicts single screenshot approach)?

**Current State:** Story 1.12 doesn't account for multi-table scenario.

---

### 3. **Table Region Extraction Missing in Epic 1**

**Issue:** 
- Story 1.1: Screenshot captures all 6 tables
- Story 1.2: Timer extraction from "orange timer region" - but which table?
- Story 1.3: Score extraction from "blue/red score regions" - but which table?

Epic 1 stories don't mention extracting table regions from the full screenshot.

**Question:** Should Epic 1 stories include:
- Table region coordinates (x, y, width, height) for each table?
- Region extraction logic (crop table region from full screenshot)?
- Or assume Epic 1 works on a pre-extracted table region?

**Current State:** Epic 1 assumes it works on a single table's data, but doesn't show how to extract that from multi-table screenshot.

---

### 4. **Click Execution Coordinate Calculation**

**Issue:** Story 1.9 says:
- `absolute_x = box['x'] + button_x + 17` (canvas transform offset)

But with 6 tables on one page, each table has its own button coordinates relative to its table region.

**Question:** Should click coordinates be:
- `absolute_x = canvas_box['x'] + table_region['x'] + button_x + 17`?
- Or are button coordinates already absolute to the page?

**Current State:** Story 1.9 doesn't account for table region offset.

---

### 5. **Page Refresh Affects All Tables**

**Issue:** Story 5.1 (Page Refresh Detection) says:
- "the system pauses automation for that table"
- "saves current state to JSON before refresh"

But if all 6 tables are on the same page, a page refresh affects ALL tables, not just one.

**Question:** Should Story 5.1:
- Pause ALL tables when page refresh detected?
- Save state for ALL tables before refresh?
- Or handle refresh per-table (but how if they're on same page)?

**Current State:** Story 5.1 treats refresh as per-table, which conflicts with single-page architecture.

---

### 6. **Timer Extraction Per Table**

**Issue:** Story 1.2 extracts timer from "orange timer region" but doesn't specify:
- Which table's timer?
- How to identify which timer belongs to which table?

**Question:** Should Story 1.2:
- Accept table_region as parameter and extract timer from that region?
- Or extract all 6 timers from the full screenshot and return array?

**Current State:** Story 1.2 doesn't specify table context.

---

### 7. **Winner Detection Timing**

**Issue:** Story 1.11 detects winner when "timer reaches 0", but with 6 tables:
- Each table has its own timer
- Tables might complete rounds at different times
- Need to track which table's timer reached 0

**Question:** Should winner detection:
- Be called per-table when that table's timer reaches 0?
- Or scan all tables and detect winners for any table that completed?

**Current State:** Story 1.11 doesn't specify multi-table context.

---

### 8. **Round Detection Per Table**

**Issue:** Story 1.10 detects "new round begins" by timer reset, but:
- Each table has independent rounds
- Tables might start new rounds at different times
- Need to track which table's round changed

**Question:** Should round detection:
- Be per-table (check each table's timer independently)?
- Or global (check all tables together)?

**Current State:** Story 1.10 doesn't specify multi-table context.

---

### 9. **Stuck State Detection Per Table**

**Issue:** Story 5.5 says "3 consecutive timeouts occur for a table", but:
- If screenshot fails, it affects ALL tables (single screenshot)
- Can individual tables be "stuck" if screenshot succeeds but their region extraction fails?

**Question:** Should stuck state be:
- Per-table (if that table's region extraction/analysis fails 3 times)?
- Or global (if screenshot fails 3 times, all tables are stuck)?

**Current State:** Story 5.5 implies per-table, but screenshot is global.

---

### 10. **Epic 1 vs Epic 2 Dependency**

**Issue:** Epic 1 stories assume single table processing, but architecture requires multi-table from start (all 6 tables on one page).

**Question:** Should Epic 1 be refactored to:
- Work with table regions from the start?
- Or keep Epic 1 as "single table logic" and Epic 2 adds "region extraction + multi-table coordination"?

**Current State:** Unclear separation between Epic 1 and Epic 2 responsibilities.

---

## Recommendations

1. **Clarify Epic 1 scope:** Should it handle table region extraction, or assume pre-extracted regions?

2. **Fix screenshot frequency:** Determine logic for multi-table scenario (fastest timer? fixed frequency?).

3. **Update all Epic 1 stories:** Add table_region parameter or table_id context to timer/score extraction, clicking, etc.

4. **Fix page refresh logic:** Handle as global event affecting all tables, not per-table.

5. **Clarify coordinate system:** Specify if button coordinates are relative to table region or absolute to page.

6. **Update error handling:** Distinguish between global errors (screenshot fails) vs per-table errors (region extraction fails).

---

## Questions for You

1. **Table Region Coordinates:** How are table regions identified? Manual configuration? Auto-detection? Fixed positions?

2. **Screenshot Frequency:** With 6 tables having different timers, what frequency should we use?

3. **Epic 1 Scope:** Should Epic 1 handle single table logic only, or include region extraction?

4. **Click Coordinates:** Are button coordinates relative to table region or absolute to page?

5. **Error Isolation:** Can one table fail while others continue, or does screenshot failure affect all?
