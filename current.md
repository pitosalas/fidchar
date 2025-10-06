# Charitable Donation Analysis System - Current State

*Last Updated: October 6, 2025*

## System Overview

A comprehensive charitable donation analysis system that processes CSV donation data and generates professional reports with visualizations and charity evaluations. The system follows Tufte design principles and provides markdown, text, and HTML outputs with configurable section ordering and parameters.

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
│   │   ├── base_report_builder.py    # Base class for reports
│   │   ├── formatters.py             # Format-specific formatters
│   │   ├── markdown_report_builder.py # Markdown reports
│   │   ├── text_report_builder.py    # Text reports
│   │   ├── html_report_builder.py    # HTML report sections
│   │   ├── comprehensive_report.py   # HTML report composition
│   │   ├── reporting.py              # Console output
│   │   └── charity_evaluator.py      # Charapi integration
│   ├── tables/                # Table generation
│   │   └── great_tables_builder.py   # Great Tables HTML generation
│   ├── main.py                # Orchestration
│   └── config.yaml            # Configuration file
├── tests/                     # Unit tests
│   ├── test_data_processing.py
│   ├── test_analysis.py
│   └── test_report_generation.py
├── archive/                   # Archived old files
├── data.csv                   # Input donation data
└── output/                    # Generated reports and charts
```

### Code Quality Compliance
- ✅ All files ≤ 300 lines (CLAUDE.md requirement)
- ✅ All functions ≤ 50 lines (CLAUDE.md requirement)
- ✅ Inheritance-based architecture with DRY principles
- ✅ Proper error handling and documentation
- ✅ Unit test coverage for core functions

## Core Capabilities

### Data Processing
- CSV input with configurable file paths
- Monetary amount parsing ($1,000.00 → 1000.0)
- Date normalization and year extraction
- Charity identification by Tax ID (not name)
- Data validation and cleaning

### Analysis Features
- **Charitable Sector**: Categorization and totals
- **Yearly Trends**: Donation amounts and counts over time
- **Top Charities**: Top 10 by total donations with full history
- **Consistent Donations**: Configurable years (default: 10) and minimum amount (default: $1000)
- **Recurring Donations**: Charities receiving donations for 4+ years (configurable)
  - Shows first year of donation
  - Shows total years supported
  - No longer uses "Recurring" field from CSV
- **Donation Patterns**: One-time vs recurring analysis
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
- **Markdown Report**: Text-based with embedded charts and Great Tables links
- **Text Report**: Plain text with tabulated data
- **HTML Report**: Professional with inline Great Tables, CSS styling, and analysis section
- **Great Tables**: Professional HTML tables with configurable font sizes
- **Section Ordering**: Fully configurable via YAML config
- **Configurable Parameters**: min_years, min_amount, sort_by, max_shown
- **PDF Generation**: Browser-based (Print to PDF)

## Configuration System

### YAML Configuration (`config.yaml`)
```yaml
# Input/Output
input_file: "../data.csv"
output_dir: "../output"

# Report Generation
generate_html: true
generate_markdown: true
generate_textfile: false

# Section Ordering with Options
sections:
  - name: exec          # Executive Summary
  - name: sectors       # Charitable Sector Analysis
  - name: consistent    # Consistent Donations
    min_years: 10       # Minimum consecutive years
    min_amount: 1000    # Minimum amount per year
  - name: yearly        # Yearly Analysis
  - name: top_charities # Top 10 Charities
  - name: recurring     # Recurring Donations List
    options:
      max_shown: 90
      sort_by: "total"  # "total" or "annual"
      min_years: 4      # Minimum years to be considered recurring
  - name: patterns      # One-Time vs Recurring
  - name: detailed      # Detailed Analysis
  - name: analysis      # Strategic Analysis (Efficiency Frontier)

# API Configuration
charity_navigator:
  app_id: "3069"
  app_key: null  # Set via CHARITY_NAVIGATOR_APP_KEY environment variable

# Charapi Integration
charapi_config_path: "/Users/pitosalas/mydev/charapi/charapi/config/config.yaml"
```

## Dependencies

### Python Packages (managed by uv)
- `pandas` - Data processing
- `matplotlib` - Chart generation
- `seaborn` - Statistical visualizations
- `great-tables` - Professional HTML tables
- `pyyaml` - Configuration file parsing
- `tabulate` - Text table formatting

### External Dependencies
- `uv` - Python package management
- `charapi` - Charity evaluation system (separate project)
- Browser with Print to PDF capability

## Current Status

### ✅ Recently Completed Features
- Inheritance-based report builder architecture (BaseReportBuilder)
- Configurable consistent donations (min_years, min_amount parameters)
- Redefined recurring donations based on years supported (not CSV field)
- Added First Year and Years Supported columns to recurring donations table
- Removed Period/Recurring field dependency
- Efficiency Frontier visualization with configurable scoring
- Updated scoring formula: Outstanding×2 + Acceptable - Unacceptable
- Single-color bubble chart (removed color coding)
- All charities labeled on efficiency frontier
- Updated HTML report to include analysis section
- Comprehensive unit test suite
- Moved obsolete files to archive/

### 📋 Active Configuration Options
1. ✅ `recurring.max_shown` - Maximum rows in recurring donations table
2. ✅ `recurring.sort_by` - Sort by "total" or "annual"
3. ✅ `recurring.min_years` - Minimum years for recurring classification
4. ✅ `consistent.min_years` - Minimum consecutive years
5. ✅ `consistent.min_amount` - Minimum annual amount

### 🔧 Future Enhancement Opportunities

#### Section-Specific Options (Not Yet Implemented)
- `sectors.show_percentages` - Show percentage breakdowns
- `yearly.include_charts` - Toggle yearly charts
- `top_charities.count` - Number of top charities to analyze
- `patterns.max_one_time_shown` - Limit one-time donations shown
- `analysis.include_impact_commitment` - Toggle impact/commitment scatter
- `analysis.include_efficiency_frontier` - Toggle efficiency frontier

#### Potential Improvements
1. **Interactive HTML**: JavaScript for sortable tables
2. **Data Validation**: Enhanced CSV format validation
3. **Export Formats**: Excel, CSV exports of analysis tables
4. **Caching**: API response caching for repeated runs
5. **Logging**: Detailed operation logging
6. **More Visualizations**: Additional analysis charts

## Running the System

### Basic Usage
```bash
cd /Users/pitosalas/mydev/fidchar/fidchar/
uv run python main.py
```

### Output
```
Cleaned output directory
Processing input file: ../data.csv
Creating analysis visualizations...
Generating reports...
Generating Great Tables HTML files...
Reports generated: comprehensive_report.html, donation_analysis.md in the output directory
```

### Generated Files
- `comprehensive_report.html` - Professional HTML report with Great Tables and analysis
- `donation_analysis.md` - Markdown analysis report
- `donation_analysis.txt` - Plain text report (if enabled)
- `gt_*.html` - Individual Great Tables (categories, yearly, consistent, top charities)
- `yearly_*.png` - Yearly trend charts
- `charity_*.png` - Individual charity trend graphs
- `efficiency_frontier.png` - Strategic analysis visualization

## System Health

### Performance
- **Processing Time**: ~10-15 seconds for full analysis
- **Memory Usage**: Efficient pandas operations
- **File Sizes**: Optimized chart and table generation

### Reliability
- **Error Handling**: Comprehensive try/catch blocks
- **Data Validation**: Input validation and cleaning
- **Graceful Degradation**: Works without API keys or charapi
- **Output Validation**: Verifies file generation success
- **Unit Tests**: Coverage for data processing, analysis, and report generation

### Maintainability
- **Modular Design**: Single responsibility principle
- **Configuration Driven**: Behavior controlled via YAML
- **Inheritance-based**: DRY with base classes and formatters
- **Well Documented**: Comprehensive docstrings
- **Type Safety**: Consistent data types and validation

## Development Environment

- **Python Version**: 3.13+ (managed by uv)
- **Package Manager**: uv (modern Python package management)
- **Version Control**: Git with GitHub remote
- **Development OS**: macOS (Darwin 25.0.0)
- **Testing**: Unit tests with pytest

## Key Design Decisions

### Recurring Donations Redefinition
- **Old**: Based on "Recurring" field in CSV (often empty or inconsistent)
- **New**: Based on years supported (4+ years by default, configurable)
- **Benefits**: More accurate, includes charities like "47 PALMER INC" with consistent yearly giving

### Efficiency Frontier Scoring
- **Formula**: Outstanding×2 + Acceptable - Unacceptable
- **Can be negative**: Yes, charities with many unacceptable metrics get negative scores
- **Thresholds**: Score ≥5 is high, 0-5 is medium, <0 is low
- **Visualization**: Single blue color, all labels shown, Tufte-style minimal design

### Report Architecture
- **Base Classes**: BaseReportBuilder provides common functionality
- **Formatters**: HTMLFormatter, MarkdownFormatter, TextFormatter for DRY output
- **Inheritance**: MarkdownReportBuilder, TextReportBuilder extend base

---

**System is production-ready and fully functional. All core features implemented with configurable parameters and comprehensive testing.**
