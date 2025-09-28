# Charity Evaluation API - Current State

*Last Updated: September 28, 2025*

## Project Overview

A comprehensive charity evaluation API that analyzes nonprofit organizations using multiple data sources (ProPublica, IRS, Charity Navigator) and provides scoring with letter grades (A-F). Built as a separate Python module for reuse in fidchar and other applications.

## Architecture

### Directory Structure
```
charity_api/
├── api/                    # Main API interfaces
│   └── charity_evaluator.py
├── clients/                # External API clients  
│   └── propublica_client.py
├── analyzers/              # Analysis logic
│   ├── financial_analyzer.py (stub)
│   ├── trend_analyzer.py (stub)
│   ├── compliance_checker.py (stub)
│   └── validation_scorer.py (stub)
├── data/                   # Data models and mock data
│   ├── charity_evaluation_result.py
│   └── mock_data.py
├── config/                 # Configuration files
│   ├── config.yaml
│   └── test_config.yaml
├── tests/                  # Test files
│   └── test_charity_api.py
└── pyproject.toml          # Package configuration
```

### Technology Stack
- **Python 3.12+** with modern uv package management
- **YAML configuration** for API keys and parameters
- **Mock mode support** for development and testing
- **Modular architecture** following CLAUDE.md principles

## Current Implementation Status

### ✅ Completed (15/37 tasks - 40.5%)

#### Infrastructure & Setup
1. **Project Structure**: uv-based Python package with pyproject.toml
2. **Configuration System**: YAML-based with global and service-level mock modes
3. **Directory Organization**: Clean separation of concerns (api/, clients/, analyzers/, data/, config/, tests/)
4. **Version Control**: Comprehensive .gitignore for Python/uv projects

#### ProPublica API Integration
5. **Client Implementation**: Full ProPublica API client with search and organization endpoints
6. **Mock Data System**: Realistic sample data for Red Cross and Salvation Army (5 years of financials)
7. **Error Handling**: API timeouts and rate limiting support
8. **Data Parsing**: JSON response structure handling

#### Core Framework
9. **Data Models**: Complete dataclass structure for evaluation results
10. **Test Infrastructure**: Working end-to-end test with mock mode
11. **Analyzer Stubs**: Framework classes for financial, trend, compliance, and validation analysis
12. **API Interface**: Main evaluate_charity() function with orchestration
13. **Grade Assignment**: Data-driven A-F scoring system
14. **Package Interface**: Clean __init__.py exports
15. **Mock Mode**: Two-level mock system (global + service-specific)

### 🔄 Current Implementation Gaps

#### Core Calculation Logic (Stubs Need Real Implementation)
- **Financial ratios**: All calculations return placeholder values
- **Trend analysis**: Growth and volatility calculations not implemented
- **Scoring algorithms**: Basic 0-100 point system needs actual logic
- **Compliance checking**: Always returns compliant status

#### Missing Integrations
- **IRS data processing**: Bulk CSV file handling not implemented
- **Charity Navigator API**: Registration and integration pending
- **CharityAPI.org**: Real-time verification not implemented
- **Caching system**: API rate limiting and local storage not implemented

## Technical Context for Future Development

### Mock Mode Design
```yaml
# Global mock mode overrides all services
mock_mode: true

# Service-specific mock mode
propublica:
  mock_mode: false  # Ignored if global is true
```

### Financial Scoring Framework (From apifeatures.md)
- **Program Expense Ratio**: Target 75%+ (40 points max)
- **Administrative Expenses**: Target <15% (20 points max)  
- **Fundraising Expenses**: Target <15% (20 points max)
- **Financial Stability**: Positive net assets (20 points max)
- **Total Base Score**: 100 points possible

### Trend Analysis Framework
- **Revenue Growth**: ±10 points based on 5-year consistency
- **Volatility Penalty**: ±10 points for financial stability
- **Data Requirements**: Minimum 3 years for meaningful analysis

### External Validation Bonuses
- **Charity Navigator**: 5 points per star (1-4 stars)
- **No Advisory Alerts**: +5 points
- **Transparency Seal**: +10 points  
- **Negative News**: -10 points
- **Maximum Bonus**: 45 points

### Compliance System
- **IRS Pub. 78 Status**: Tax-deductible eligibility
- **Revocation Check**: Auto-revocation list monitoring
- **Recent Filing**: Form 990 within 3 years
- **Penalty**: -50 points for non-compliance

## Current Todo List (22 pending tasks)

### Priority 1: Core Financial Analysis (5 tasks)
1. Implement actual financial ratio calculations
2. Create real calculate_financial_score function (0-100 scale)
3. Add proper handling of missing financial data
4. Implement net assets stability validation
5. Add support for different form types (990, 990-EZ, 990-PF)

### Priority 2: Trend Analysis (3 tasks)
1. Implement revenue growth rate calculation over 5 years
2. Create growth consistency scoring (±10 points)
3. Add volatility penalty calculation (±10 points)

### Priority 3: Testing & Validation (6 tasks)
1. Add EIN format validation (9-digit tax ID)
2. Create comprehensive unit tests for financial calculations
3. Add unit tests for API client methods
4. Test with real organizations (Red Cross, Salvation Army)
5. Validate scoring against manual calculations
6. Create example usage script for Phase 1

### Priority 4: Data Integration (8 tasks)
1. Download and process IRS bulk CSV files
2. Implement real compliance checking functions
3. Register for Charity Navigator API
4. Implement external validation bonus system
5. Add CharityAPI.org integration
6. Create API response caching system
7. Add algorithm validation against known charities
8. Create comprehensive documentation

## Proposed Technical Changes

### 1. Configuration Enhancement
```yaml
# Add to config.yaml
data_sources:
  irs:
    pub78_url: "https://www.irs.gov/pub/irs-soi/eo_xx.csv"
    cache_refresh_days: 30
  
caching:
  enabled: true
  api_cache_hours: 24
  local_storage_path: "cache/"
```

### 2. Error Handling Strategy
- **Fail Fast**: Follow CLAUDE.md principle of not coding defensively
- **Specific Exceptions**: Replace generic error handling with business logic errors
- **Graceful Degradation**: Continue evaluation with partial data when possible

### 3. Performance Optimizations
- **Async API Calls**: Implement concurrent requests to multiple data sources
- **Intelligent Caching**: Cache based on data freshness requirements
- **Batch Processing**: Support multiple EIN evaluations in single request

### 4. Code Quality Improvements
- **Method Length**: Ensure all methods stay under 50 lines (CLAUDE.md)
- **File Size**: Keep all files under 300 lines (CLAUDE.md)
- **No Default Parameters**: Force explicit parameter passing
- **Intention-Revealing Names**: Make method purposes clear from names

## Integration Context

### Current fidchar Integration Points
- **Package Import**: `from charity_api import evaluate_charity`
- **Configuration**: Shared YAML config with existing fidchar patterns
- **Data Output**: Compatible with fidchar's analysis pipeline
- **Mock Mode**: Allows fidchar development without API dependencies

### Future Enhancement Opportunities
1. **Interactive HTML Reports**: JavaScript-based sortable tables
2. **Export Formats**: Excel/CSV exports of analysis results
3. **Sector Benchmarking**: Industry-specific scoring adjustments
4. **News Sentiment Analysis**: Automated news impact scoring
5. **Comparative Ranking**: Multi-charity comparison features

## Development Environment

- **Python**: 3.12+ (managed by uv)
- **Package Manager**: uv (modern Python dependency management)
- **Testing**: Built-in test runner, no external framework dependencies
- **Configuration**: YAML-based, environment variable support planned
- **Mock Data**: Realistic 5-year financial datasets for major charities

---

**Status**: Infrastructure complete, core calculation logic pending implementation. Ready for financial analysis development phase.