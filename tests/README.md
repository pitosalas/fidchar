# Test Suite for fidchar

## Overview

This test suite covers the core business logic and report generation for the fidchar charitable donation analysis system.

## Test Files

### `test_analysis.py` (27 tests)
Tests for core analysis functions - **NOT tied to report structure**.

Tests:
- `analyze_by_category()` - Category aggregation
- `analyze_by_year()` - Yearly totals and counts
- `analyze_recurring_donations()` - Active recurring donations (2024-2025)
- `analyze_consistent_donors()` - 5-year consistent donors
- `get_top_charities_basic()` - Top N charities
- `analyze_donation_patterns()` - One-time vs stopped recurring

These tests verify:
- ✅ Calculation correctness
- ✅ Data filtering logic
- ✅ Sorting behavior
- ✅ Edge cases (empty data, nulls)
- ✅ Business rules

### `test_data_processing.py` (15 tests)
Tests for CSV parsing and data cleaning - **NOT tied to report structure**.

Tests:
- `parse_amount()` - Currency string parsing
- `read_donation_data()` - CSV reading and type conversion

These tests verify:
- ✅ Amount parsing ($1,000.00 → 1000.0)
- ✅ Date conversion and year extraction
- ✅ Column name cleaning
- ✅ Error handling

### `test_report_snapshot.py` (9 tests)
**Golden master tests** - These ARE tied to report structure.

Tests verify that report output hasn't changed unexpectedly by:
1. **Structure tests** - Check key elements exist (tables, headers, totals)
2. **Data integrity tests** - Verify correct data appears in output
3. **Golden master tests** - Compare full output to saved reference files

**Golden master files** stored in `tests/golden_masters/`:
- `recurring_donations.html` - Reference HTML output
- `recurring_donations.md` - Reference Markdown output

## Running Tests

### Run all tests:
```bash
uv run pytest tests/ -v
```

### Run specific test file:
```bash
uv run pytest tests/test_analysis.py -v
uv run pytest tests/test_data_processing.py -v
uv run pytest tests/test_report_snapshot.py -v
```

### Run tests with coverage:
```bash
uv run pytest tests/ --cov=fidchar --cov-report=html
```

## Golden Master Tests

### What are Golden Master Tests?

Golden master (or snapshot) tests save a "known good" output and compare future runs against it. They catch unexpected changes during refactoring.

### When Golden Master Tests Fail

If a golden master test fails:

1. **Review the changes**: Check the diff file saved in `tests/golden_masters/`
   - `recurring_donations_current.html` or `recurring_donations_current.md`

2. **Determine if change is intentional**:
   - If the change is a **bug** → Fix your code
   - If the change is **intentional** → Update the golden master

3. **Update golden master** (if change is intentional):
   ```bash
   cp tests/golden_masters/recurring_donations_current.html tests/golden_masters/recurring_donations.html
   cp tests/golden_masters/recurring_donations_current.md tests/golden_masters/recurring_donations.md
   ```

4. **Rerun tests** to verify they pass

### When to Update Golden Masters

Update golden masters when you:
- Intentionally change report formatting
- Add new fields to reports
- Change calculation display format
- Refactor report generation (output should be identical)

**Do NOT update** golden masters if:
- You're getting unexpected output (fix the bug instead)
- Tests fail after refactoring (output should match!)
- You're not sure what changed (investigate first)

## Test Philosophy

### Tests Independent of Report Structure ✅
- Core analysis logic (`test_analysis.py`)
- Data processing (`test_data_processing.py`)
- These can remain unchanged during report refactoring

### Tests Dependent on Report Structure ⚠️
- Snapshot tests (`test_report_snapshot.py`)
- These will need updates when report format changes
- But they catch unintended changes during refactoring!

## Adding New Tests

### For new analysis functions:
Add to `test_analysis.py` - focus on data correctness, not formatting

### For new report sections:
Add golden master tests to `test_report_snapshot.py`:
1. Create test data fixture
2. Add structure test (check key elements exist)
3. Add data integrity test (verify correct data)
4. Add golden master comparison test

## Test Results

**Current status**: ✅ **51 tests passing**
- 27 analysis tests
- 15 data processing tests
- 9 snapshot tests

## Dependencies

Tests require:
- `pytest` - Testing framework
- Standard library only (no additional test dependencies)

Run `uv add pytest` to install.
