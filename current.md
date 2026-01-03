# Charitable Donation Analysis System - Current State

*Last Updated: January 2, 2026*

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

**Current Code**:
```python
# Lines 442-458 in prepare_combined_recurring_data
org_donations = self.df.groupby("Tax ID").agg({
    "Amount_Numeric": ["sum", "count"],
    "Submit Date": ["min", "max"],
    "Recurring": "first",
    "Organization": "first"
}).round(2)
org_donations.columns = ["Total_Amount", "Donation_Count", "First_Date", "Last_Date", "Recurring_Status", "Organization_Name"]

stopped_recurring = org_donations[
    (org_donations["Donation_Count"] > 1) &
    (org_donations["Last_Date"].dt.year < current_year - 1) &
    (org_donations["Recurring_Status"].str.contains("annually|semi-annually", case=False, na=False))
]
stopped_eins = set(stopped_recurring.index)
```

**Fix**: Pass `stopped_recurring` DataFrame from caller (already calculated in main.py line 68) instead of recalculating.

#### 3. Defensive Null-Checking Pattern Duplication
Lines 461 and 554 use identical null-checking pattern:
```python
csv_eins = set(csv_recurring_df.index) if csv_recurring_df is not None and not csv_recurring_df.empty else set()
```

**Fix**: Extract to helper method `_extract_ein_set(df)`.

#### 4. Per-Charity Data Extraction Loop Duplication
Lines 474-509 and 568-591 have nearly identical loops that:
- Filter df by Tax ID
- Check if empty
- Extract organization name
- Calculate totals and build year strings

**Fix**: Extract to shared `_build_charity_rows(ein_list, column_builder_callback)` method.

#### 5. DataFrame Construction Pattern Duplication
Lines 520-529 and 594-602 are identical:
```python
result_df = pd.DataFrame(rows)
result_df = result_df.set_index('EIN')
result_df = result_df.sort_values(...)
if condition:
    result_df = result_df.head(max_shown)
return result_df
```

**Fix**: Extract to `_finalize_dataframe(rows, index_col, sort_col, max_shown)`.

### Code Quality Issues in charity_evaluator.py

**File**: `fidchar/reports/charity_evaluator.py`

#### Missing Required Comments
- **Line 2**: Missing "Author: Pito Salas and Claude Code" (rules.md line 12)
- **Line 3**: Missing "Open Source Under MIT license" (rules.md line 13)

#### Function Too Long
- `get_charity_evaluations()` is 74 lines (lines 12-86)
- **VIOLATES** rules.md line 16: "You shall ensure functions and methods are no longer than 50 lines"
- 24 lines over limit

#### Too Many Parameters
- Function has 6 parameters: `top_charities, charapi_config_path, donation_df, recurring_config, one_time, stopped_recurring`
- **VIOLATES** rules.md line 28: "You shall avoid functions with more than 3 arguments"
- 3 parameters over limit

#### Default Parameters
- Uses `recurring_config=None`, `one_time=None`, `stopped_recurring=None`
- **VIOLATES** rules.md line 40: "You shall not provide default parameters to functions"

#### Defensive Exception Handling
- Lines 76-84 catch broad `Exception` instead of letting it bubble up
- **VIOLATES** rules.md line 41: "You shall not code defensively"

**Recommended Refactoring**:
```python
# Split into smaller functions:
def _get_pattern_recurring(df, pattern_config)  # Lines 34-43
def _get_csv_recurring(df, csv_config)          # Lines 45-49
def _combine_charity_sets(...)                  # Lines 56-67
def _batch_evaluate_charities(...)              # Lines 69-74

# Consider config object to reduce parameters:
@dataclass
class RecurringConfig:
    pattern_based: dict
    csv_field_based: dict
```

## 💡 Ideas for Future Enhancements

### High Priority (Code Quality)
1. **Fix rules.md Violations**
   - Move imports to top of files
   - Eliminate code duplication in base_report_builder.py
   - Refactor charity_evaluator.py to comply with function length/parameter limits
   - Add missing author/license comments
   - Remove defensive exception handling

2. **Apply YAGNI Principle**
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
├── fidchar/                    # Main package
│   ├── core/                   # Core functionality
│   │   ├── data_processing.py # CSV reading & cleaning
│   │   ├── analysis.py        # Data analysis functions
│   │   └── visualization.py   # Chart generation (Tufte-style)
│   ├── reports/               # Report generation
│   │   ├── base_report_builder.py    # Base class (⚠️ has duplication issues)
│   │   ├── formatters.py             # Format-specific formatters
│   │   ├── markdown_report_builder.py # Markdown reports
│   │   ├── text_report_builder.py    # Text reports
│   │   ├── html_report_builder.py    # HTML report sections
│   │   ├── comprehensive_report.py   # HTML report composition
│   │   ├── reporting.py              # Console output
│   │   ├── charity_evaluator.py      # Charapi integration (⚠️ rules violations)
│   │   ├── styles.css                # All CSS (screen + print consolidated)
│   │   └── colors.css                # Color definitions
│   ├── report_generator/      # Reusable rendering library
│   │   ├── models.py          # ReportTable, ReportCard data models
│   │   └── renderers.py       # HTML/Text/Markdown renderers
│   ├── tables/                # Table generation
│   │   └── great_tables_builder.py   # Great Tables HTML generation
│   ├── main.py                # Orchestration
│   ├── config.yaml            # Configuration file
│   └── definitions.md         # Definitions section (Bootstrap grid HTML)
├── tests/                     # Unit tests
│   ├── test_data_processing.py
│   ├── test_analysis.py
│   └── test_report_generation.py
├── archive/                   # Archived old files
├── data.csv                   # Input donation data (gitignored)
├── output/                    # Generated reports and charts
└── rules.md                   # Coding standards and conventions
```

### Code Quality Compliance
- ⚠️ **Function Length**: charity_evaluator.py has 74-line function (limit: 50)
- ⚠️ **Imports**: base_report_builder.py has imports in function bodies (should be at top)
- ⚠️ **Code Duplication**: Significant duplication in base_report_builder.py
- ⚠️ **Parameter Count**: charity_evaluator.py has 6-parameter function (limit: 3)
- ✅ All files ≤ 300 lines
- ✅ Inheritance-based architecture with DRY principles (but needs cleanup)
- ✅ Proper error handling and documentation
- ✅ Unit test coverage for core functions

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

### Immediate Priority: Fix rules.md Violations

1. **Fix base_report_builder.py**
   - Move `from datetime import datetime` to top of file (currently lines 443, 551)
   - Extract duplicated stopped recurring calculation (pass from caller instead)
   - Create helper method `_extract_ein_set(df)` for null-checking pattern
   - Create helper method `_build_charity_rows(ein_list, column_builder)` for loop pattern
   - Create helper method `_finalize_dataframe(rows, index, sort, limit)` for DataFrame construction

2. **Refactor charity_evaluator.py**
   - Add author and license comments (lines 2-3)
   - Split `get_charity_evaluations()` into smaller functions (currently 74 lines)
   - Reduce parameter count from 6 to ≤3 (consider config object)
   - Remove default parameters
   - Remove defensive exception handling (let errors bubble up)

3. **Test After Refactoring**
   - Run `uv run python main.py` to ensure report still generates
   - Verify "Rule" column still shows correct values
   - Check that no functionality was broken

### Context for AI
- Recent work focused on fixing Rule column bug where CSV-only charities incorrectly showed ✓
- Solution: Separated pattern_based_ein_set from combined recurring_ein_set
- This introduced code duplication that needs cleanup
- System is functional but has technical debt in base_report_builder.py and charity_evaluator.py
- Follow rules.md strictly for all refactoring work

---

**System Status**: Production-ready and functional, but requires refactoring to meet coding standards defined in rules.md.
