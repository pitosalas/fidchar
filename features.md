# Charitable Donation Analysis Features

## Data Processing
- Read CSV data file
- Parse monetary amounts from text format
- Convert dates to datetime objects
- Clean and normalize column names
- Group charities by tax ID (not name) for consistency

## Analysis Features
- List all charitable categories with total amounts
- Calculate yearly donation totals and counts
- Identify top 10 charities by total donations
- Find consistent donors (5+ years, $500+ annually)
- Analyze one-time vs recurring donation patterns
- Track charities that received single donations only
- Identify stopped recurring donation patterns

## Visualization
- Use seaborn for all graphs
- Follow Tufte's guidelines for minimal, data-focused charts
- Create small inline graphs integrated with text
- Generate yearly amount histograms
- Generate yearly count histograms
- Create individual charity donation graphs (full history, not just 10 years)
- Remove chart junk and unnecessary visual elements

## Reporting
- Generate markdown output file
- Create comprehensive HTML report with Great Tables
- Make reports visually appealing and professional
- Include detailed analysis of top 10 charities
- Show individual donation lists with tax IDs
- Integrate charity descriptions from Charity Navigator API

## Technical Features
- Organize as standard Python package structure
- Clean output directory before each run automatically
- Store all outputs in dedicated output directory
- Minimal console output (input file, reports generated, output files)
- YAML configuration file for comprehensive settings control
- Configurable section ordering with future options support
- Great Tables for professional HTML table formatting with larger fonts
- Tufte-style minimal design principles throughout
- Modular architecture with focused, single-responsibility modules
- Full compliance with code quality constraints (≤300 lines per file, ≤50 lines per function)

## Configuration Management
- YAML-based configuration system (`config.yaml`)
- Configurable input file paths
- Flexible report section ordering with descriptive identifiers
- Optional report format generation (markdown, PDF)
- Future-ready section-specific options framework
- Environment variable support for API credentials

## Output Formats
- Markdown analysis report with embedded charts and table links
- HTML comprehensive report with inline Great Tables and styling
- Individual PNG chart files (yearly trends, charity histories)
- Individual HTML table files for each analysis section
- Browser-based PDF generation (Print to PDF recommended)
- Configurable output directory structure



