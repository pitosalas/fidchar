# Definitions

<div class="row">
<div class="col-md-6 border-end">

## Recurring Charity
A charity that meets specific criteria based on your giving history:
- You donated to them in the previous calendar year
- You donated at least the minimum amount in at least the minimum number of years within the recent period
- Default criteria: At least 5 years of donations ≥ $1,000 in the last 15 years
- Identified automatically from your donation data

## One-Time Donation
Organizations to which you donated exactly once in your entire donation history. These may represent:
- Event-based giving (disaster relief, special campaigns)
- Trial donations to explore new causes
- Organizations you supported but chose not to continue with

## Stopped Recurring Donation
Organizations that were previously recurring but have stopped:
- Had multiple donations with an "annually" or "semi-annually" pattern
- Last donation was more than 1 year ago
- May indicate charities you previously supported regularly but have discontinued

## Alignment Score
A score (0-100) that measures how well a charity aligns with your personal giving preferences:
- **Mission Alignment** (0-50 points): Based on the charity's NTEE code matching your priority sectors (high/medium/low)
- **Geographic Alignment** (0-30 points): Based on the charity's location matching your preferred or acceptable states
- **Size Alignment** (0-20 points): Based on the charity's revenue matching your preferred organization size (small/medium/large)

### Badge System

The report uses compact, italic badges to highlight important charity attributes displayed in the header of each detail card.


**Status Badges:**
- **RECUR**: Charity receives regular donations from you based on historical pattern
- **CONSDR**: High-quality charity meeting alignment and evaluation thresholds (not shown for recurring charities)

**Alignment Badge:**
Shows the alignment score as a percentage:
- **ALIGN: X%**: Where X is the alignment score (0-100)
  - 90-100: Excellent alignment
  - 70-89: Good alignment
  - 50-69: Moderate alignment
  - 30-49: Limited alignment
  - 0-29: Poor alignment

</div>
<div class="col-md-6">

## Metric Status

### Outstanding ⭐
The charity exceeds best-practice standards in this metric.

### Acceptable ✓
The charity meets minimum acceptable standards in this metric.

### Unacceptable ⚠
The charity falls below acceptable standards in this metric and may warrant additional scrutiny.

## Financial Metrics

### Program Expense Ratio
Percentage of total expenses spent on program services (the charity's mission). Higher is generally better.
- Outstanding: ≥ 75%
- Acceptable: ≥ 65%

### Administrative Expense Ratio
Percentage of total expenses spent on management and general administration. Lower is generally better.
- Outstanding: ≤ 15%
- Acceptable: ≤ 25%

### Fundraising Expense Ratio
Percentage of total expenses spent on fundraising activities. Lower is generally better.
- Outstanding: ≤ 10%
- Acceptable: ≤ 20%

</div>
<div class="row">
<div class="col-md-6 border-end">


## Organization Types

### NTEE Code
National Taxonomy of Exempt Entities - a classification system for nonprofits by their mission and activities.

### Subsection
IRS tax code subsection under which the organization is exempt (e.g., 501(c)(3)).

### Foundation Type
Indicates whether the organization is a private foundation, public charity, or other type.

## Charity Detail Cards

Each charity receives a detailed analysis card with a three-row layout:

### Card Header
- Charity name (left, 75% width)
- Status and alignment badges (right, 25% width)

### Row 1: Basic Information and Trend Graph
**Left Column (58%):**
- Tax ID (EIN)
- Charitable sector
- Total donated across all years
- Number of donations

**Right Column (42%):**
- Visual representation of your donation history over time

### Row 2: Evaluations (Side by Side)
**Left Column (50%):**
- Charity Evaluation summary showing:
  - **Outstanding (⭐)**: Metrics exceeding best practices
  - **Acceptable (✓)**: Metrics meeting minimum standards
  - **Unacceptable (⚠)**: Metrics below acceptable standards

**Right Column (50%):**
- Alignment with Your Goals breakdown:
  - Overall alignment score (0-100)
  - Mission priority match
  - Geographic preference match
  - Organization size match

### Row 3: Narrative Summary
Full-width descriptive text about the charity's performance and alignment with your goals.

## Data Sources

### ProPublica Nonprofit Explorer
Provides IRS Form 990 data including financial information and organizational details.

### CharityAPI
Provides comprehensive nonprofit data including tax status, NTEE codes, and organizational information.

### Charity Navigator
Provides ratings, mission statements, and additional evaluation data for rated organizations. All charities with CharityNavigator data include:
- Mission statements
- ENCOMPASS scores and star ratings
- Beacon metrics (Financial Health, Accountability & Transparency)
- Advisory alerts (when applicable)
</div>
<div class="col-md-6">

## For Consideration (CONSDR Badge)

Charities that meet quality thresholds and warrant consideration for detailed analysis, even if they're not in the top N by donation amount. These charities are marked with a **CONSDR** badge.

A charity receives the CONSDR badge if it meets **both** criteria:
- **Alignment Score** ≥ configured minimum (default: 70/100)
- **Evaluation Score** ≥ configured minimum (default: 70%)
- **Not a recurring charity** (recurring charities already receive the RECUR badge)

**Evaluation Score** is calculated as the percentage of metrics that are Acceptable or Outstanding:
```
Evaluation Score = (Outstanding + Acceptable) / Total Metrics × 100
```

This ensures the detailed analysis includes not just your largest donations, but also high-quality charities that align well with your goals.

## Report Configuration

The report can be customized via `config.yaml`:

### Top Charities
- `count`: Number of top charities by donation amount (default: 10)
- Additional charities meeting "for consideration" criteria are automatically included
- Final list is sorted **alphabetically by organization name**

### Patterns Section
- `max_one_time_shown`: Maximum one-time donations to display (default: 20)
- `max_stopped_shown`: Maximum stopped recurring donations to display (default: 15)

### Recurring Summary Section
- `max_recurring_shown`: Maximum recurring charities to display (default: 20)

### Recurring Charity Criteria
- `count`: Years of history to consider (default: 15)
- `min_years`: Minimum years of qualifying donations (default: 5)
- `min_amount`: Minimum donation per qualifying year (default: $1,000)

### For Consideration Criteria
- `enabled`: Enable/disable for consideration feature (default: true)
- `min_alignment_score`: Minimum alignment score 0-100 (default: 70)
- `min_evaluation_score`: Minimum evaluation score percentage (default: 70)

</div>
</div>
