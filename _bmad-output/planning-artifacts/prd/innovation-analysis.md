# Innovation Analysis

### Pattern-Based Decision Making

**Innovation:** Intelligent pattern recognition system that learns from round history and makes automated decisions based on user-defined pattern rules.

**Value:** Enables users to automate complex decision logic without manual intervention, maximizing efficiency and consistency.

**Implementation Approach:**
- Pattern matching algorithm with priority-based matching (first match wins)
- Learning phase ensures sufficient history before making decisions
- Pattern format validation ensures correctness

### Multi-Table Parallel Processing

**Innovation:** Simultaneous automation of up to 6 game tables with independent state management and decision logic.

**Value:** Maximizes automation throughput and efficiency, enabling users to scale their automation efforts.

**Implementation Approach:**
- Parallel processing using threading or asyncio
- Independent state trackers per table
- Region-only screenshots for efficient resource usage
- Thread-safe data structures for concurrent access

### Adaptive Performance Optimization

**Innovation:** Dynamic screenshot frequency adjustment based on game phase and system resource usage.

**Value:** Optimizes resource usage while capturing critical moments, ensuring efficient operation under varying conditions.

**Implementation Approach:**
- Multiple screenshot frequency strategies (fastest timer, slowest timer, fixed, majority rule, per-table independent)
- CPU usage monitoring with auto-throttling
- Phase-based frequency selection (clickable phase: 200ms, countdown phase: 100ms, result phase: 1s)

### Resilient Error Recovery

**Innovation:** Multi-layer error handling with automatic recovery from common failure scenarios.

**Value:** Ensures continuous operation without manual intervention, maximizing uptime and user satisfaction.

**Implementation Approach:**
- Try → Retry (3x) → Fallback → Alert User → Pause strategy
- Page refresh detection with auto-resume
- Exponential backoff retry logic
- OCR fallback for template matching failures
- Stuck state detection with automatic table pausing
