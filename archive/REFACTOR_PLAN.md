# Main.py Refactoring Plan

## Current Structure Analysis
- **500 lines** in single file
- **12 functions** with distinct responsibilities
- Clear logical groupings already exist

## Proposed 4-Module Organization

### 1. `data_processing.py` - Data Input & Cleaning
```python
# Functions:
- parse_amount()
- read_donation_data()

# Responsibility:
- CSV reading and parsing
- Data cleaning and type conversion
- Basic data validation
```

### 2. `analysis.py` - Data Analysis & Calculations
```python
# Functions:
- analyze_by_category()
- analyze_by_year()
- analyze_donation_patterns()
- analyze_top_charities()

# Responsibility:
- All pandas groupby operations
- Statistical analysis
- Data aggregations
```

### 3. `visualization.py` - Charts & Graphs
```python
# Functions:
- create_yearly_histograms()
- create_charity_yearly_graphs()
- All matplotlib/seaborn styling setup

# Responsibility:
- Tufte-style graph generation
- Chart styling and formatting
- Graph file output
```

### 4. `reporting.py` - Report Generation
```python
# Functions:
- get_charity_description() (API calls)
- generate_markdown_report()
- generate_console_report()

# Responsibility:
- External API integration
- Markdown report generation
- Table formatting (tabulate)
- File output
```

### Updated `main.py` - Orchestration Only
```python
# Functions:
- main() only

# Responsibility:
- Import all modules
- Orchestrate the analysis pipeline
- Handle command-line arguments
- Error handling at top level
```

## Benefits of This Organization

1. **Single Responsibility Principle** - Each module has one clear purpose
2. **Easy Testing** - Can test each module independently
3. **Maintainability** - Much easier to find and modify specific functionality
4. **Reusability** - Modules can be imported and used separately
5. **Collaboration** - Different people can work on different modules

## File Structure After Refactoring
```
fidchar/
├── __init__.py
├── main.py              # ~50 lines - orchestration only
├── data_processing.py   # ~80 lines - data input/cleaning
├── analysis.py          # ~150 lines - core analysis functions
├── visualization.py     # ~120 lines - charts and graphs
└── reporting.py         # ~150 lines - report generation
```

## Implementation Strategy
1. Create the 4 new modules
2. Move functions to appropriate modules
3. Update imports in each module
4. Simplify main.py to just orchestrate
5. Test that everything still works
6. Add proper module docstrings

**Estimated effort: 2-3 hours of careful refactoring**