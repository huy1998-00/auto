# Unit Tests for Mini-Game Automation

This directory contains unit tests for Epics 1-2 of the Mini-Game Website Automation & Pattern Tracking Tool.

## Test Coverage

### Epic 1: Single-Table Automation

#### Pattern Matching (`tests/pattern_matching/`)
- **test_pattern_validator.py**: Pattern format validation
  - Valid/invalid pattern strings
  - Pattern parsing and formatting
  - Error message generation
  
- **test_pattern_matcher.py**: Priority-based pattern matching
  - Pattern matching algorithm
  - Decision mapping (B→red, P→blue)
  - Priority order (first match wins)

#### Coordinate Utilities (`tests/utils/`)
- **test_coordinate_utils.py**: Coordinate calculations
  - Canvas offset handling (17px)
  - Absolute coordinate calculation
  - Region and point operations
  - Canvas drift validation

#### Table Tracker (`tests/orchestration/`)
- **test_table_tracker.py**: Table state management
  - Round history tracking (last 3 rounds)
  - Learning phase (first 3 rounds)
  - Score tracking and winner detection
  - Decision making

### Epic 2: Multi-Table Parallel Processing

#### Data Persistence (`tests/data/`)
- **test_session_manager.py**: Session folder management
  - Date-based session creation
  - Table registration
  - Session configuration

- **test_json_writer.py**: Thread-safe JSON writing
  - File locking with portalocker
  - Concurrent write safety
  - Round data persistence
  - Statistics updates

#### Multi-Table Manager (`tests/orchestration/`)
- **test_multi_table_manager.py**: Parallel table processing
  - Table addition/removal
  - MAX_TABLES limit enforcement
  - Thread management
  - Status tracking

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Module
```bash
pytest tests/pattern_matching/test_pattern_validator.py
```

### Run with Coverage
```bash
pytest tests/ --cov=src/automation --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/pattern_matching/test_pattern_validator.py::TestPatternValidator
```

### Run Specific Test Method
```bash
pytest tests/pattern_matching/test_pattern_validator.py::TestPatternValidator::test_valid_single_pattern
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Detailed Output
```bash
pytest tests/ -vv
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`:
- `temp_session_dir`: Temporary session directory
- `sample_table_region`: Sample table coordinates
- `sample_patterns`: Sample pattern string
- `sample_round_history`: Sample round history
- `mock_screenshot`: Mock screenshot image
- `sample_table_state`: Sample table state
- `sample_round_data`: Sample round data
- `mock_canvas_box`: Mock canvas bounding box
- `sample_button_coords`: Sample button coordinates

## Test Structure

Each test file follows this structure:
1. **Imports**: Test dependencies and modules under test
2. **Test Classes**: Grouped by functionality
3. **Test Methods**: Individual test cases with descriptive names
4. **Assertions**: Clear assertions for expected behavior

## Writing New Tests

When adding new tests:

1. **Follow naming convention**: `test_<functionality>.py`
2. **Use descriptive test names**: `test_<what>_<expected_behavior>`
3. **Use fixtures**: Reuse common fixtures from `conftest.py`
4. **Test edge cases**: Include boundary conditions and error cases
5. **Keep tests isolated**: Each test should be independent
6. **Use appropriate assertions**: `assert`, `pytest.raises()`, etc.

## Example Test

```python
def test_pattern_validation_valid_pattern():
    """Test validation of valid pattern."""
    validator = PatternValidator()
    assert validator.is_valid("BBP-P") is True
```

## Continuous Integration

Tests should pass before committing:
```bash
pytest tests/ -v
```

## Coverage Goals

- **Epic 1**: >80% coverage for core modules
- **Epic 2**: >80% coverage for threading and data persistence
- **Overall**: >75% code coverage
