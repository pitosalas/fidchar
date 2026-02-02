# Charitable Donation Analysis System - Current State

*Last Updated: February 1, 2026*

## 🚨 URGENT: Known Issues Requiring Attention

### Critical Code Quality Issues in base_report_builder.py

**File**: `fidchar/reports/base_report_builder.py`

#### 1. Imports in Middle of Code (Lines 440, 443, 551)
```python
# VIOLATES rules.md line 30: "You shall put all imports at the top of the file"
def prepare_combined_recurring_data(self, csv_recurring_df, max_shown=100):
    from fidchar.core import analysis as an  # Line 440 - MOVE TO TOP
    from datetime import datetime             # Line 443 - MOVE TO TOP

def prepare_all_charities_data(self, csv_recurring_df, max_shown=None):
    from fidchar.core import analysis as an  # Line 550 - MOVE TO TOP
    from datetime import datetime             # Line 551 - MOVE TO TOP
```

**Fix**: Move `from datetime import datetime` to top of file. The `analysis` import may be intentional to avoid circular dependency.

#### 2. Duplicated Stopped Recurring Calculation (Lines 442-458)
The code in `prepare_combined_recurring_data()` recalculates stopped recurring charities, duplicating logic from `analysis.analyze_donation_patterns()`.

**Fix**: Pass `stopped_recurring` DataFrame from caller (already calculated in main.py line 68) instead of recalculating.

#### 3. Defensive Null-Checking Pattern Duplication
Multiple identical null-checking patterns throughout the file.

**Fix**: Extract to helper method `_extract_ein_set(df)`.

#### 4. Per-Charity Data Extraction Loop Duplication
Multiple methods have nearly identical loops for extracting charity data.

**Fix**: Extract to shared `_build_charity_rows(ein_list, column_builder_callback)` method.

#### 5. DataFrame Construction Pattern Duplication
Multiple methods use identical DataFrame finalization pattern.

**Fix**: Extract to `_finalize_dataframe(rows, index_col, sort_col, max_shown)`.

### Code Quality Issues in charity_evaluator.py

**File**: `fidchar/reports/charity_evaluator.py`

✅ **FIXED**: Author and license comments added (Feb 1, 2026)

#### Method Too Long
- `CharityEvaluator.get_evaluations()` is ~70 lines (lines 27-98)
- **VIOLATES** rules.md line 16: "You shall ensure functions and methods are no longer than 50 lines"
- ~20 lines over limit

#### Default Parameters (Improved, but still present)
- Uses `one_time=None`, `stopped_recurring=None`
- **VIOLATES** rules.md line 40: "You shall not provide default parameters to functions"
- **Note**: Reduced from 3 default params to 2 (improvement from Jan 7 refactoring)

#### Defensive Exception Handling
- Lines 81-96 catch broad `Exception` instead of letting it bubble up
- **VIOLATES** rules.md line 41: "You shall not code defensively"

**Recommended Refactoring**:
```python
# Split into smaller methods:
def _get_pattern_recurring(self)                  # Lines 44-54
def _get_csv_recurring(self)                       # Lines 56-61
def _combine_charity_sets(charities, one_time, stopped)  # Lines 67-74
def _batch_evaluate_charities(charity_list)       # Lines 81-96
```

## 💡 Ideas for Future Enhancements

### High Priority (Code Quality)
1. **Fix rules.md Violations**
   - Move imports to top of files in base_report_builder.py
   - Eliminate code duplication in base_report_builder.py (still present despite refactoring)
   - Refactor charity_evaluator.py to comply with function length/parameter limits
   - Remove defensive exception handling

2. **Improve Test Coverage** ⚠️ CRITICAL
   - **Current Coverage**: 14% overall (1249 statements, 1069 missed)
   - **0% Coverage on Recently Refactored Code**:
     - html_report_builder.py (0/165 statements)
     - html_section_generators.py (0/260 statements)
     - section_handlers.py (0/133 statements)
   - **Add Integration Tests** for report generation workflow
   - **Add Tests** for HTML section generators (currently untested)
   - **Goal**: Achieve at least 60% coverage on report generation modules

3. **Apply YAGNI Principle**
   - Review for unnecessary abstractions
   - Remove unused helper methods
   - Simplify overly defensive error checking

### Medium Priority (Features)
1. **Use py-box for Configuration Management**
   - Replace manual YAML dict access with py-box for cleaner dot notation
   - Would enable `config.input_file` instead of `config["input_file"]`
   - Provides better attribute access and validation
   - Lightweight alternative to OmegaConf without Hydra overhead

2. **Add Page Breaks for PDF Printing**
   - Insert CSS page break hints when HTML is printed to PDF from browser
   - Use `page-break-before: always` or `page-break-after: always` CSS properties
   - Ensure each major section starts on a new page in PDF output
   - Improve professional appearance of printed reports

## System Overview

A comprehensive charitable donation analysis system that processes CSV donation data and generates professional HTML reports with visualizations and charity evaluations. The system follows Tufte design principles and provides Bootstrap-styled HTML output with configurable section ordering and parameters.

## Architecture

### File Structure
```
fidchar/
├── config.yaml                # Configuration file (MOVED from fidchar/ on Feb 1, 2026)
├── fidchar/                    # Main package
│   ├── core/                   # Core functionality
│   │   ├── data_processing.py # CSV reading & cleaning (83% test coverage)
│   │   ├── analysis.py        # Data analysis functions (14% test coverage)
│   │   ├── models.py          # Data models (76% test coverage)
│   │   └── visualization.py   # Chart generation (16% test coverage)
│   ├── reports/               # Report generation
│   │   ├── base_report_builder.py    # Base class with ReportData dataclass (0% coverage)
│   │   ├── html_report_builder.py    # Core orchestration - 312 lines (0% coverage)
│   │   ├── html_section_generators.py # Mixin with generate_* methods - 431 lines (0% coverage)
│   │   ├── section_handlers.py       # Section handlers - 253 lines (0% coverage)
│   │   ├── html_templates.py         # HTML template functions
│   │   ├── formatters.py             # Format-specific formatters
│   │   ├── markdown_report_builder.py # Markdown reports
│   │   ├── text_report_builder.py    # Text reports
│   │   ├── comprehensive_report.py   # HTML report composition
│   │   ├── reporting.py              # Console output
│   │   ├── charity_evaluator.py      # Charapi integration (0% coverage)
│   │   ├── styles.css                # All CSS (screen + print consolidated)
│   │   └── colors.css                # Color definitions
│   ├── report_generator/      # Reusable rendering library
│   │   ├── models.py          # ReportTable, ReportCard data models
│   │   └── renderers.py       # HTML/Text/Markdown renderers
│   ├── tables/                # Table generation
│   │   └── great_tables_builder.py   # Great Tables HTML generation
│   ├── main.py                # Orchestration (0% coverage)
│   └── definitions.md         # Definitions section (Bootstrap grid HTML)
├── tests/                     # Unit tests (33 tests, all passing)
│   ├── test_data_processing.py
│   ├── test_analysis.py
│   ├── test_export_csv.py
│   ├── test_for_consideration.py
│   └── test_report_generation.py
├── archive/                   # Archived old files
├── data.csv                   # Input donation data (gitignored)
├── output/                    # Generated reports and charts
└── rules.md                   # Coding standards and conventions
```

### Code Quality Compliance
- ⚠️ **Function Length**: charity_evaluator.py has 70-line method (limit: 50)
- ⚠️ **Imports**: base_report_builder.py has imports in function bodies (should be at top)
- ⚠️ **Code Duplication**: Significant duplication in base_report_builder.py
- ⚠️ **Parameter Count**: Improved from 7→3 with ReportData dataclass (Feb 1, 2026)
- ⚠️ **Test Coverage**: 14% overall, 0% on report generation modules
- ✅ All files ≤ 500 lines (html_report_builder 312, generators 431, handlers 253)
- ✅ Inheritance-based architecture with mixin pattern
- ✅ All 33 tests passing
- ✅ Proper error handling and documentation

## Core Capabilities

### Recurring Charity Detection (Dual Method)

**Pattern-Based Detection** (Analyzes YOUR donation history):
- Configurable: `count` (years to look back, default: 15)
- Configurable: `min_years` (must donate in N years, default: 5)
- Configurable: `min_amount` (minimum per year, default: $1000)
- Returns: `pattern_based_ein_set`

**CSV Field-Based Detection** (Uses Fidelity's export):
- Reads "Recurring" field from CSV (e.g., "annually through indefinitely")
- Enabled by default
- Returns: `csv_recurring_ein_set`

**Combined Set**:
- `recurring_ein_set = pattern_based | csv_based`
- Used for RECUR badge display in reports
- Both methods tracked separately for transparency

**Key Implementation**:
- File: `fidchar/reports/charity_evaluator.py`
- Returns: `(evaluations, recurring_ein_set, pattern_based_ein_set)`
- Pattern-based used for "Rule" column
- CSV-based used for "CSV" column
- Combined used for RECUR badge

### Data Processing
- CSV input with configurable file paths
- Monetary amount parsing ($1,000.00 → 1000.0)
- Date normalization and year extraction
- Charity identification by Tax ID (not name)
- Data validation and cleaning

### Analysis Features
- **Charitable Sector**: Categorization and totals
- **Yearly Trends**: Donation amounts and counts over time
- **Top Charities**: Configurable count (default: 25, set via `top_charities_count`)
- **All Charities Report**: Comprehensive list with CSV/Rule indicators, years, current year amount
- **Combined Recurring**: Merges rule-based and CSV-based with Source column
- **Donation Patterns**: One-time vs recurring analysis
- **Stopped Recurring**: Identifies charities where recurring donations ceased
- **For Consideration**: Charities meeting quality thresholds (alignment score ≥70, evaluation score ≥70)
- **Charity Evaluations**: Integration with charapi for performance metrics

### Visualization
- Tufte-style minimalist charts using seaborn and matplotlib
- Yearly amount and count histograms
- Individual charity trend graphs (full donation history)
- **Efficiency Frontier**: Shows evaluation scores vs total donated
  - Score formula: Outstanding×2 + Acceptable - Unacceptable
  - Single blue color for all bubbles (no color coding)
  - All charities labeled
  - Reference lines at score 0 and 5
- Small inline graphs integrated with reports
- PNG output for all visualizations

### Reporting
- **HTML Report**: Professional Bootstrap 5.3.2 styling with `report_generator` renderers
- **Report Generator**: Reusable module for data-driven table/card rendering
  - `ReportTable` and `ReportCard` data models
  - HTML renderers for Bootstrap components
  - Bootstrap card components with sections (text, key_value, list, progress_bar, table)
  - Text/Markdown renderers kept in library for potential reuse
- **Section Ordering**: Fully configurable via YAML config
- **Configurable Parameters**: See Active Configuration Options below
- **PDF Generation**: Browser-based (Print to PDF)

## Configuration System

### Current YAML Configuration (`fidchar/config.yaml`)
```yaml
# Input/Output
input_file: "data.csv"
output_dir: "output"

# Top charities configuration (NEW: Dec 27, 2024)
top_charities_count: 25  # Number of top charities to include in detailed analysis

# Report sections (currently enabled)
sections:
  - name: exec          # Executive Summary
  - name: sectors       # Charitable Sector Analysis
    options:
      show_percentages: true
  - name: yearly        # Yearly Analysis
    options:
      include: false
  - name: top_charities # Top N Charities
    options:
      count: 20
  - name: all_charities # All Charities (comprehensive list)
    # options:
      # max_shown: 200  # Omit to show all charities
  - name: detailed      # Detailed Analysis of Top Charities
  - name: definitions   # Definitions of terms

# Recurring charity determination - two methods
recurring_charity:
  pattern_based:
    enabled: true
    count: 15           # Look at last 15 years
    min_years: 5        # Must have donated in at least 5 of those years
    min_amount: 1000    # Each qualifying year must have >= $1000 in donations
  csv_field_based:
    enabled: true

# For consideration criteria (charities to include even if not in top N)
for_consideration:
  enabled: true
  min_alignment_score: 70        # Minimum alignment score (0-100)
  min_evaluation_score: 70       # Minimum evaluation score (0-100)

# Charapi Integration (handles all Charity Navigator API access)
charapi_config_path: "/Users/pitosalas/mydev/charapi/charapi/config/config.yaml"
```

### Available Report Sections
- `exec`: Executive Summary
- `sectors`: Donation Analysis by Charitable Sector
- `yearly`: Yearly Donation Analysis
- `top_charities`: Top N Charities by Total Donations
- `combined_recurring`: Combined Recurring Charities (rule-based + CSV-based with Source column)
- `recurring_summary`: Recurring Charities Summary (rule-based only)
- `csv_recurring`: CSV-Based Recurring Charities (Fidelity's recurring field only)
- `all_charities`: All Charities (comprehensive list with CSV/Rule indicators)
- `high_alignment_opportunities`: **NEW** - High-alignment charities not recurring (potential recurring candidates)
- `remaining`: Remaining Charities (multi-year, multi-donation but not recurring)
- `patterns`: One-Time vs Recurring Donation Patterns
- `detailed`: Detailed Analysis of Top N Charities
- `definitions`: Definitions of terms used in the report

## Dependencies

### Python Packages (managed by uv)
- `pandas` - Data processing
- `matplotlib` - Chart generation
- `seaborn` - Statistical visualizations
- `great-tables` - Professional HTML tables
- `pyyaml` - Configuration file parsing
- `tabulate` - Text table formatting
- `markdown-it-py` - Markdown parsing for definitions section

### External Dependencies
- `uv` - Python package management
- `charapi` - Charity evaluation system (separate project, exclusive source for Charity Navigator data)
- Browser with Print to PDF capability

## Recent Development History

### February 1, 2026 - Major Refactoring: HTML Report Builder Modularization

**Focus**: Breaking down html_report_builder.py into focused modules to improve maintainability and reduce file size.

**Status**: ✅ Completed and tested. All 33 tests passing. Report generation working correctly.

**Changes**:

1. **HTML Report Builder Refactoring (67% Reduction)**
   - **Before**: Single 960-line file (html_report_builder.py)
   - **After**: Three focused modules:
     - `html_report_builder.py` - 312 lines (core orchestration, inherits from mixin)
     - `html_section_generators.py` - 431 lines (mixin with all generate_* methods)
     - `section_handlers.py` - 253 lines (standalone handler functions)
   - **Architecture**:
     - `HTMLReportBuilder` now inherits from `HTMLSectionGeneratorsMixin` and `BaseReportBuilder`
     - Separation of concerns: core (orchestration), generators (HTML creation), handlers (section logic)
     - All section generation moved to handlers that call builder methods
   - **Files Created**:
     - `fidchar/reports/html_section_generators.py` - Mixin class with generate_* methods
     - `fidchar/reports/section_handlers.py` - Handler functions and `generate_table_sections()`

2. **ReportData Dataclass Implementation**
   - **Before**: BaseReportBuilder.__init__() had 7 parameters
   - **After**: Uses ReportData dataclass with 3 parameters
   ```python
   @dataclass
   class ReportData:
       charity_details: dict
       graph_info: dict
       evaluations: dict
       recurring_ein_set: set = field(default_factory=set)
       pattern_based_ein_set: set = field(default_factory=set)
   ```
   - **Benefit**: Cleaner API, easier to extend, complies with rules.md parameter limits
   - **Files Modified**:
     - `fidchar/reports/base_report_builder.py` - Added dataclass
     - `fidchar/main.py` - Updated to use ReportData
     - All test files updated to use new API

3. **Charapi Duplicate Warning Fix**
   - **Problem**: Error message printed 3 times (once per API client initialization)
   - **Solution**: Implemented shared cache pattern
     - Create cache once in `_create_clients()`
     - Pass shared cache to all 3 API clients (ProPublica, CharityAPI, CharityNavigator)
     - Warning now shown once with compact format: "⚠️ 25 cached API errors (HTTPError: 21, AttributeError: 4)"
   - **Files Modified**:
     - `charapi/charapi/api/charity_evaluator.py` - Create shared cache
     - `charapi/charapi/clients/base_client.py` - Accept shared_cache parameter
     - `charapi/charapi/clients/charityapi_client.py` - Use shared cache
     - `charapi/charapi/clients/propublica_client.py` - Use shared cache
     - `charapi/charapi/clients/charitynavigator_client.py` - Use shared cache

4. **Configuration File Moved**
   - Moved `config.yaml` from `fidchar/config.yaml` to project root using `git mv`
   - Preserves git history
   - Easier access for users
   - Updated `fidchar/main.py` to load from new location

5. **Enhanced Charity Detail Cards**
   - Added most recent donation info to summary boxes
   - Format: `Donations: $6,500 (5x) | Latest: $1,500 on Jan 15, 2025`
   - Extracts from donation history DataFrame

6. **Test Suite Improvements**
   - Fixed test_export_csv.py syntax errors
   - Updated test_for_consideration.py to use ReportData
   - Fixed badge test to check pattern_based_ein_set
   - **Fixed import error**: Added `_extract_section_options` to imports in html_report_builder.py
   - **All 33 tests passing** ✅
   - **Test Coverage**: 14% overall
     - Strong: data_processing.py (83%), models.py (76%)
     - Weak: All report builders (0%), main.py (0%), charity_evaluator (0%)
     - **⚠️ Critical**: Newly refactored modules have 0% coverage

**Rules.md Compliance**:
- ✅ Reduced parameter count from 7 to 3 (ReportData pattern)
- ✅ File sizes under 500 lines (html_report_builder 312, generators 431, handlers 253)
- ⚠️ Still has issues in base_report_builder.py (imports in function bodies, duplication)
- ⚠️ Still has issues in charity_evaluator.py (70-line method, default params)

**Architecture Pattern Established**:
When a file grows too large:
1. Extract standalone functions to separate handler module
2. Extract related methods to mixin class
3. Keep core orchestration in main class
4. Use dataclasses to reduce parameter passing

**Test Coverage Gaps Identified** ⚠️:
- 0% coverage on html_report_builder.py (165 statements)
- 0% coverage on html_section_generators.py (260 statements)
- 0% coverage on section_handlers.py (133 statements)
- **Action Required**: Add integration tests for report generation

**Files Modified**:
- `fidchar/reports/html_report_builder.py` - Refactored to 312 lines
- `fidchar/reports/base_report_builder.py` - Added ReportData dataclass
- `fidchar/main.py` - Use ReportData, update config path
- `config.yaml` - Moved to project root
- `charapi/` - 5 files modified for shared cache
- `tests/` - Updated all tests to use ReportData

### January 18, 2026 - CSV Export Enhancement

**Changes**:
Added two new columns to `charity_export.csv`:

1. **DonationYears** - Comma-separated list of years when donations were made (e.g., "2019, 2020, 2022, 2023"), sorted chronologically
2. **TotalDonations** - Sum of all donation amounts ever made to that charity

Fixed ServiceArea column (was Geography, always empty):
- Renamed column from `Geography` to `ServiceArea` to match HTML report
- Changed data source from `client_geography` to `service_areas` (same as HTML report)
- Now correctly shows values like "US", "GLOBAL", "MA"

**Implementation** (main.py lines 118-135):
```python
# ServiceArea extraction (lines 118-123)
service_areas_data = vals.get('service_areas', [])
if service_areas_data:
    if isinstance(service_areas_data, list):
        service_area = ", ".join(service_areas_data)
    else:
        service_area = str(service_areas_data)

# Years with donations (lines 131-135)
years = sorted(org_df["Submit Date"].dt.year.unique())
donation_years = ", ".join(str(y) for y in years)
total_donations = org_df["Amount_Numeric"].sum()
```

**Updated CSV Columns** (11 total):
EIN, Name, Mission, Budget, ServiceArea, Alignment, MostRecentAmount, MostRecentDate, IsRecurring, DonationYears, TotalDonations

**Files Modified**:
- `fidchar/main.py`: Added DonationYears, TotalDonations, and fixed ServiceArea extraction

### January 7, 2026 - Code Quality Refactoring: Reduced Parameter Counts & Eliminated Duplication

**Focus**: Addressing rules.md violations by refactoring functions with too many parameters and eliminating duplicate calculations.

**Changes**:

1. **Removed Global "Top Charities" Concept**
   - **Before**: Global `top_charities_count` variable controlled charity selection throughout system
   - **After**: Each section independently controls display using `max_shown` option
   - Renamed config keys: `top_charities_sort` → `charities_sort`, `top_charities_min_grant` → `charities_min_grant`
   - Renamed variables throughout: `top_charities` → `charities`
   - **Benefit**: More flexible - different sections can show different numbers of charities

2. **Created CharityEvaluator Class** (charity_evaluator.py)
   - **Before**: Standalone `get_charity_evaluations()` function with 6 parameters
     ```python
     def get_charity_evaluations(top_charities, charapi_config_path, donation_df,
                                 recurring_config, one_time, stopped_recurring)
     ```
   - **After**: Class-based design with 3 method parameters
     ```python
     class CharityEvaluator:
         def __init__(self, donation_df, config):
             # Store config settings as instance variables

         def get_evaluations(self, charities, one_time=None, stopped_recurring=None):
             # Use instance variables for configuration
     ```
   - **Improvement**: 6 parameters → 3 parameters (50% reduction)
   - **Files Modified**: `charity_evaluator.py`, `main.py`

3. **Converted generate_html_header_section to Instance Method** (html_report_builder.py)
   - **Before**: Standalone function with 8 parameters
     ```python
     def generate_html_header_section(total_donations, total_amount, years_covered,
                                      one_time_total, one_time_count, stopped_total,
                                      stopped_count, options)
     ```
   - **After**: Instance method with 1 parameter
     ```python
     class HTMLReportBuilder:
         def generate_html_header_section(self, options=None):
             # Calculate from instance variables (self.df, self.one_time, etc.)
     ```
   - **Improvement**: 8 parameters → 1 parameter (87.5% reduction!)

4. **Precomputed Summary Statistics** (html_report_builder.py)
   - **Problem**: Calculations like `len(self.one_time)` and `self.one_time["Total_Amount"].sum()` were duplicated in:
     - `generate_html_header_section()` method (lines 112-115)
     - `_handle_patterns()` function (lines 826-827, 831-832)
   - **Solution**: Precompute in `generate_report()` as instance variables:
     ```python
     self.total_amount = category_totals.sum()
     self.one_time_total = one_time["Total_Amount"].sum()
     self.one_time_count = len(one_time)
     self.stopped_total = stopped_recurring["Total_Amount"].sum()
     self.stopped_count = len(stopped_recurring)
     ```
   - **Benefit**: DRY principle - calculations done once, used multiple times

**Files Modified**:
- `fidchar/reports/charity_evaluator.py`: Created CharityEvaluator class
- `fidchar/main.py`: Updated to use CharityEvaluator class, removed top_charities global logic
- `fidchar/reports/html_report_builder.py`: Converted function to method, added precomputed stats
- `fidchar/reports/base_report_builder.py`: Renamed method `prepare_top_charities_data()` → `prepare_charities_data()`
- `fidchar/core/analysis.py`: Renamed `get_top_charities_basic()` → `get_charities_basic()`
- `fidchar/core/visualization.py`: Updated parameter names
- `fidchar/config.yaml`: Updated config keys and removed global top_charities_count

**Rules.md Compliance**:
- ✅ **Reduced** charity_evaluator.py from 6 parameters to 3 (still above limit of 3, but improved)
- ✅ **Reduced** generate_html_header_section from 8 parameters to 1
- ✅ **Eliminated** duplicate calculations (DRY principle)
- ✅ **Better encapsulation** with class-based design

**Pattern Established**:
When functions have many parameters, consider:
1. Which parameters are configuration/context that rarely changes? → Move to instance variables
2. Which parameters vary per call? → Keep as method parameters
3. Are calculations duplicated? → Precompute as instance variables

### January 2, 2026 - High Alignment Opportunities Report & Code Refactoring

**Changes**:
1. **New "High Alignment Opportunities" Report Section**
   - Shows charities with alignment score ≥80% that are NOT rule-based recurring
   - Identifies high-quality charities that could become recurring donations
   - Configurable minimum alignment score (default: 80)
   - Reuses all_charities infrastructure with filter_func parameter
   - Found 35 candidates in current dataset
   - Example: ACLU Foundation of MA ($30K, 80% alignment, 6 donations)

2. **Refactored All Charities Report for Reusability**
   - Added `filter_func` parameter to `prepare_all_charities_data()`
   - Function signature: `filter_func(ein, in_csv, in_rule, evaluation) -> bool`
   - Enables filtering by any criteria (alignment score, evaluation metrics, etc.)
   - Eliminated need for duplicate report code
   - Same HTML renderer works for both all_charities and high_alignment_opportunities

3. **Enhanced Charity Detail Cards**
   - Added **Mission** (was "Tags"), **Service Area**, and **Donations** to main info box
   - Removed "Sector" (less useful than specific mission tags)
   - Added **Overall evaluation score** to Charity Evaluation section
   - Format: "Overall: 62% (10/16)" showing ratio of acceptable/outstanding metrics
   - Tags and service areas pulled from charapi evaluation data

4. **Test Suite Fixes** (All 32 tests now passing)
   - Fixed 5 data processing tests (added 8-line CSV header to test data)
   - Fixed 5 for_consideration badge tests (added data_field_values attribute)
   - Updated MockEvaluation to match real evaluation structure
   - Badge styling test now checks for CSS class instead of inline styles

5. **Label Improvements**
   - Changed "Tags:" to "Mission:" in charity detail cards
   - More intuitive for end users (shows "Mission: civil_rights" vs "Tags: civil_rights")

**Files Modified**:
- `fidchar/reports/base_report_builder.py`: Added filter_func parameter to prepare_all_charities_data()
- `fidchar/reports/html_report_builder.py`: Added high_alignment_opportunities section, enhanced card generation
- `fidchar/config.yaml`: Added high_alignment_opportunities section with min_alignment_score option
- `tests/test_data_processing.py`: Fixed all CSV header tests
- `tests/test_for_consideration.py`: Fixed MockEvaluation and styling tests

**Configuration**:
```yaml
sections:
  - name: high_alignment_opportunities
    options:
      min_alignment_score: 80  # Minimum alignment score (default: 80)
      # max_shown: 50  # Omit to show all
```

### December 27, 2024 - Bug Fix and Configuration Enhancement

**Commit**: `83fd2d8` - "Fix Rule column bug and add configurable top charities count"

**Changes**:
1. **Fixed Rule Column Bug in All Charities Report**
   - **Issue**: "Rule" column showed ✓ for CSV-only recurring charities
   - **Root Cause**: `recurring_ein_set` contained combined pattern+CSV charities
   - **Fix**: Separated `pattern_based_ein_set` from `recurring_ein_set`
   - **Files Modified**:
     - `charity_evaluator.py`: Now returns 3 values: `(evaluations, recurring_ein_set, pattern_based_ein_set)`
     - `base_report_builder.py`: Stores both sets, uses `pattern_based_ein_set` for "Rule" column
     - `html_report_builder.py`: Passes both sets through constructors
     - `main.py`: Handles 3-value return, passes both sets to builders

2. **Added Configurable Top Charities Count**
   - Added `top_charities_count: 25` to config.yaml
   - Moved from section options to top-level config
   - `main.py` reads from `config.get("top_charities_count", 10)`

3. **All Charities Report Section**
   - Shows all charities ordered by total donation
   - Columns: Organization, Total, CSV, Rule, Years, 2025, Count
   - CSV column: ✓ if in Fidelity's CSV recurring field
   - Rule column: ✓ if meets pattern-based criteria
   - Configurable `max_shown` (None = show all)

**Known Issues Introduced**:
- Code duplication in `base_report_builder.py` (see Urgent Issues section)
- Imports in function bodies violate rules.md
- `charity_evaluator.py` needs refactoring for rules.md compliance

### Earlier Work
- Inheritance-based report builder architecture (BaseReportBuilder)
- Redefined recurring donations based on years supported (not CSV field)
- Efficiency Frontier visualization with configurable scoring
- CSS Consolidation: Merged print.css into styles.css
- Definitions Section: Uses Bootstrap grid with HTML embedded in markdown
- Bootstrap-First approach: Minimal custom CSS

## Running the System

### Basic Usage
```bash
cd /Users/pitosalas/mydev/fidchar/fidchar/
uv run python main.py
```

### Configuration
To modify configuration parameters, edit `fidchar/config.yaml` directly.

### Output
```
Cleaned output directory
Processing input file: data.csv
Identified XX pattern-based recurring charities
Identified YY CSV field-based recurring charities
Total recurring charities (combined): ZZ
Evaluating NNN charities (top + recurring + one-time + stopped)
Generating HTML report...
Report generated: donation_analysis.html in the output directory
```

### Generated Files
- `donation_analysis.html` - Professional HTML report with Bootstrap styling and visualizations
- `images/` - Directory containing all generated charts and visualizations
  - `yearly_*.png` - Yearly trend charts
  - `charity_*.png` - Individual charity trend graphs
  - `efficiency_frontier.png` - Strategic analysis visualization

## System Health

### Performance
- **Processing Time**: ~10-15 seconds for full analysis
- **Memory Usage**: Efficient pandas operations
- **File Sizes**: Optimized chart and table generation

### Reliability
- **Error Handling**: Comprehensive try/catch blocks (⚠️ some overly defensive)
- **Data Validation**: Input validation and cleaning
- **Graceful Degradation**: Works without API keys or charapi
- **Output Validation**: Verifies file generation success
- **Unit Tests**: Coverage for data processing, analysis, and report generation

### Maintainability
- **Modular Design**: Single responsibility principle
- **Configuration Driven**: Behavior controlled via YAML
- **Inheritance-based**: DRY with base classes (⚠️ needs cleanup for duplication)
- **Well Documented**: Comprehensive docstrings
- **Type Safety**: Consistent data types and validation
- ⚠️ **Code Quality Issues**: See Urgent Issues section

## Development Environment

- **Python Version**: 3.12+ (managed by uv, .python-version specifies 3.12)
- **Package Manager**: uv (modern Python package management)
- **Version Control**: Git with GitHub remote
- **Development OS**: macOS (Darwin 25.2.0)
- **Testing**: Unit tests with pytest

## Key Design Decisions

### Dual Recurring Charity Detection
- **Pattern-Based**: Analyzes YOUR donation history (≥5 years, ≥$1,000/year, donated in previous year)
- **CSV Field-Based**: Uses Fidelity's "Recurring" designation from CSV export
- **Separation**: Both methods tracked separately for transparency
- **Combined Set**: Used for RECUR badge display
- **Benefit**: More accurate than single method, allows comparison of detection approaches

### Report Columns Meaning
- **CSV Column**: ✓ if charity marked as recurring in Fidelity's CSV export
- **Rule Column**: ✓ if charity meets pattern-based criteria (≥5 years, ≥$1,000/year)
- **RECUR Badge**: Shows if charity is in EITHER CSV or Rule set (combined)

### Efficiency Frontier Scoring
- **Formula**: Outstanding×2 + Acceptable - Unacceptable
- **Can be negative**: Yes, charities with many unacceptable metrics get negative scores
- **Thresholds**: Score ≥5 is high, 0-5 is medium, <0 is low
- **Visualization**: Single blue color, all labels shown, Tufte-style minimal design

### Report Architecture
- **Base Classes**: BaseReportBuilder provides common functionality
- **HTML-Only**: System generates only professional HTML reports with Bootstrap 5.3.2 styling
- **Report Generator**: Separate reusable library for table/card rendering (supports Text/Markdown/HTML)
- **Simple Configuration**: YAML-based configuration with no external framework dependencies

## Next Steps for AI Continuation

### Immediate Priority 1: Improve Test Coverage ⚠️ CRITICAL

**Current State**:
- 33 tests passing (100% pass rate) ✅
- Overall coverage: 14% (1249 statements, 1069 missed) ⚠️
- **Newly refactored modules have 0% coverage**:
  - html_report_builder.py (0/165 statements)
  - html_section_generators.py (0/260 statements)
  - section_handlers.py (0/133 statements)
  - charity_evaluator.py (0/43 statements)
  - main.py (0/44 statements)

**Action Items**:
1. **Add Integration Tests for Report Generation**
   - Test full HTML report generation workflow
   - Test section handlers with real data
   - Test charity card generation with evaluations
   - Verify filter functions work correctly

2. **Add Unit Tests for HTML Section Generators**
   - Test each generate_* method in html_section_generators.py
   - Test with edge cases (empty data, missing fields)
   - Verify HTML output structure

3. **Add Tests for Section Handlers**
   - Test each _handle_* function
   - Test section options parsing
   - Test filter functions (e.g., high alignment filter)

4. **Goal**: Achieve 60%+ coverage on report generation modules

### Immediate Priority 2: Fix rules.md Violations

1. **Fix base_report_builder.py**
   - Move `from datetime import datetime` to top of file (currently in function bodies)
   - Extract duplicated stopped recurring calculation (pass from caller instead)
   - Create helper method `_extract_ein_set(df)` for null-checking pattern
   - Create helper method `_build_charity_rows(ein_list, column_builder)` for loop pattern
   - Create helper method `_finalize_dataframe(rows, index, sort, limit)` for DataFrame construction

2. **Refactor charity_evaluator.py**
   - Split `get_evaluations()` into smaller methods (currently 70 lines, limit 50)
   - Remove default parameters (`one_time=None`, `stopped_recurring=None`)
   - Remove defensive exception handling (let errors bubble up)
   - Break into: `_get_pattern_recurring()`, `_get_csv_recurring()`, `_combine_charity_sets()`, `_batch_evaluate_charities()`

3. **Test After Refactoring**
   - Run full test suite: `python -m pytest tests/ --cov=fidchar`
   - Run report generation: `uv run python fidchar/main.py`
   - Verify "Rule" column still shows correct values
   - Check that no functionality was broken

### Context for AI (February 1, 2026)

**Recent Work Completed**:
- Major refactoring: Split html_report_builder.py (960 lines) into 3 focused modules (312+431+253 lines)
- Implemented ReportData dataclass to reduce parameter counts (7→3)
- Fixed charapi duplicate warning with shared cache pattern
- Moved config.yaml to project root
- Enhanced charity cards with most recent donation info
- All 33 tests passing ✅

**Current System State**:
- **Functional**: Report generation works correctly, all features operational
- **Architecture**: Clean separation with mixin pattern, good modular design
- **Technical Debt**:
  - 0% test coverage on newly refactored report modules ⚠️
  - Imports in function bodies (base_report_builder.py)
  - Code duplication (base_report_builder.py)
  - Method too long (charity_evaluator.py, 70 lines)
  - Defensive exception handling (charity_evaluator.py)

**Key Files to Focus On**:
- `fidchar/reports/base_report_builder.py` - Duplication and import issues
- `fidchar/reports/charity_evaluator.py` - Method length and defensive coding
- `tests/` - Need integration tests for report generation

**Follow rules.md strictly** for all refactoring work. System is production-ready but needs test coverage and cleanup.

---

**System Status**: Production-ready and functional. Major refactoring completed successfully. Next priority is adding comprehensive test coverage for report generation modules, then addressing remaining rules.md violations.
