# Conflicts and Inconsistencies Check - Updated Review

## Date: 2026-01-05
## Status: After Region-Only Screenshot Update

---

## ✅ RESOLVED ISSUES (From Previous Review)

1. **Region-Only Screenshots**: ✅ RESOLVED
   - Document now consistently uses region-only screenshots
   - Story 1.1, 1.2, 2.2 all updated

2. **Table Region Extraction**: ✅ RESOLVED
   - Story 1.2 exists for table region configuration
   - Coordinates stored per table

3. **Click Coordinates**: ✅ RESOLVED
   - Story 1.10 specifies: `absolute_x = canvas_box['x'] + table_region['x'] + button_x + 17`
   - Button coordinates are relative to table region

4. **Page Refresh**: ✅ RESOLVED
   - Story 5.1 correctly states it affects ALL tables

5. **Screenshot Frequency**: ✅ RESOLVED
   - Story 1.13 provides 5 strategy options
   - User can choose (default: Option A)

6. **Per-Table Processing**: ✅ RESOLVED
   - Stories specify "for a specific table"
   - Independent processing per table

7. **Stuck State Detection**: ✅ RESOLVED
   - Story 5.5 distinguishes per-table vs global stuck state

8. **Timer Countdown**: ✅ RESOLVED
   - Document clearly states timer counts DOWN to 0
   - Consistent throughout

---

## ⚠️ REMAINING MINOR ISSUES

### 1. **FR1 Wording Inconsistency**

**Issue:** FR1 says "capture screenshots of the game canvas" but implementation uses region-only screenshots.

**Current FR1:**
```
FR1: The system must capture screenshots of the game canvas using Playwright browser automation
```

**Should be:**
```
FR1: The system must capture screenshots of specific game table regions using Playwright browser automation
```

**Impact:** Low - wording issue, not a logic conflict

**Recommendation:** Update FR1 to match implementation

---

### 2. **Scoreboard Monitoring Ambiguity**

**Issue:** Story 4.7 (Scoreboard Monitoring) doesn't specify:
- Is there one global scoreboard for all tables?
- Or per-table scoreboards?
- Which scoreboard is monitored?

**Current State:**
- Story 4.7 says "monitors the yellow scoreboard section"
- Says "all tables stop processing" when target reached
- Implies global scoreboard, but not explicitly stated

**Questions:**
- Is the scoreboard shared across all 6 tables?
- Or does each table have its own scoreboard?
- If shared, does it track combined score or individual table scores?

**Impact:** Medium - Could affect implementation

**Recommendation:** Clarify if scoreboard is global or per-table

---

### 3. **Canvas Validation with Region Screenshots**

**Issue:** Story 5.4 (Canvas Validation) mentions validating canvas position, but with region-only screenshots:
- Do we still need canvas validation?
- What exactly is being validated?

**Current State:**
- Story 5.4 validates canvas position every 10-20 rounds
- Checks if position drifts >5px
- With region-only screenshots, canvas position affects all table region coordinates

**Analysis:** ✅ This is actually CORRECT
- Canvas position drift would affect ALL table region coordinates
- Validation is still needed to ensure coordinates remain accurate
- If canvas moves, all table regions would be misaligned

**Impact:** None - logic is correct

---

### 4. **Epic 1 Title vs Content**

**Issue:** Epic 1 is titled "Single Table Automation" but stories work with table regions (multi-table ready).

**Current State:**
- Epic 1 title: "Single Table Automation"
- Stories work with table regions and can handle any table (1-6)
- Stories specify "for a specific table"

**Analysis:** ✅ This is actually CORRECT
- Epic 1 focuses on the LOGIC for processing ONE table
- Even if multiple tables exist, each table is processed independently
- The title means "automation logic for one table", not "only one table exists"

**Impact:** None - title is appropriate

---

### 5. **FR24 vs Story 1.13 Options**

**Issue:** FR24 says "adaptive screenshot frequency (200ms when timer > 6, 100ms when timer ≤ 6)" but Story 1.13 provides 5 different strategy options.

**Current State:**
- FR24: Specific implementation (200ms/100ms)
- Story 1.13: 5 strategy options (A, B, C, D, E)
- Default is Option A (matches FR24)

**Analysis:** ✅ This is actually CORRECT
- FR24 describes the DEFAULT behavior
- Story 1.13 provides implementation flexibility
- User can choose different strategies, but default matches FR24

**Impact:** None - FR describes default, story provides options

---

## 🔍 POTENTIAL LOGIC ISSUES

### 1. **Sequential Clicks with 10-20ms Delay**

**Issue:** Performance Requirements say "Sequential clicks with 10-20ms delay between clicks (across all tables)".

**Questions:**
- If 6 tables all want to click simultaneously, do they queue?
- Is the delay per-table or global?
- Can clicks from different tables happen in parallel?

**Current State:** Not explicitly addressed in stories

**Recommendation:** Clarify click execution strategy for multi-table scenarios

---

### 2. **Canvas Transform Offset (17px)**

**Issue:** Story 1.10 uses `+ 17` for canvas transform offset.

**Questions:**
- Is this offset constant for all tables?
- Does it apply to both X and Y coordinates?
- Is it relative to canvas or table region?

**Current State:**
- Story 1.10: `absolute_x = canvas_box['x'] + table_region['x'] + button_x + 17`
- Only applied to X coordinate
- Y coordinate: `absolute_y = canvas_box['y'] + table_region['y'] + button_y` (no offset)

**Analysis:** ✅ This seems intentional
- Only X coordinate has transform offset
- Y coordinate doesn't need offset

**Impact:** None - but should verify this is correct during implementation

---

### 3. **Learning Phase Per Table**

**Issue:** Story 1.6 (Learning Phase) is per-table, which is correct.

**Verification:** ✅ CORRECT
- Each table has independent learning phase
- 3 rounds per table before making decisions
- Stories correctly specify "for a specific table"

**Impact:** None

---

## 📋 SUMMARY

### Critical Issues: **0**
### Minor Issues: **2**
1. FR1 wording inconsistency (low impact)
2. Scoreboard monitoring ambiguity (medium impact)

### Verified Correct: **5**
1. Canvas validation with region screenshots ✅
2. Epic 1 title vs content ✅
3. FR24 vs Story 1.13 options ✅
4. Learning phase per table ✅
5. Canvas transform offset (X only) ✅

### Recommendations:

1. **Update FR1** to say "capture screenshots of specific game table regions"
2. **Clarify Story 4.7** to specify if scoreboard is global or per-table
3. **Consider adding** click execution strategy clarification (sequential vs parallel)

---

## ✅ OVERALL ASSESSMENT

**Document Status:** ✅ **MOSTLY CLEAR** - Only 2 minor issues remain

**Ready for Implementation:** ✅ **YES** (with minor clarifications)

**Main Concerns:**
- Scoreboard monitoring needs clarification (global vs per-table)
- FR1 wording should match implementation

**All major conflicts from previous review have been resolved.**
