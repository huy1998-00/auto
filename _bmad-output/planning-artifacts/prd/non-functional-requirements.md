# Non-Functional Requirements

### Performance

**NFR1:** The system must process all 6 tables simultaneously using parallel processing (threading/asyncio)

**NFR2:** The system must maintain screenshot capture latency under 500ms for normal monitoring

**NFR3:** The system must maintain screenshot capture latency under 200ms when timer > 6

**NFR4:** The system must maintain screenshot capture latency under 100ms when timer ≤ 6

**NFR9:** The system must update UI every 500ms for real-time monitoring

**NFR32:** The system must auto-throttle screenshot frequency if CPU usage exceeds 80%

### Reliability and Resilience

**NFR5:** The system must handle a single Playwright browser instance displaying all 6 tables on one page

**NFR6:** The system must recover gracefully from page refreshes without losing round history

**NFR7:** The system must handle network lag and slow page loads with timeout-based retry (5 second timeout)

**NFR11:** The system must persist all round data to JSON files with no data loss

**NFR12:** The system must support unlimited round history writing (continuous writing until tool closes)

### Thread Safety and Concurrency

**NFR8:** The system must provide thread-safe operations for all shared data structures

**NFR13:** The system must implement file locking for thread-safe JSON writes

### Data Validation and Quality

**NFR10:** The system must validate pattern format using regex: `^[BP]{3}-[BP](;[BP]{3}-[BP])*$`

### Error Handling and Debugging

**NFR14:** The system must provide error logging with screenshots for debugging template matching failures

**NFR15:** The system must implement anti-bot measures (random delays 50-200ms, human-like timing variations)

### Security and Licensing (Phase 4)

**NFR16:** The system must validate license keys on startup and block tool if invalid (Phase 4)

**NFR17:** The system must support offline license validation (no internet required) (Phase 4)
