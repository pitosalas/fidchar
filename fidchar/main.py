#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from decimal import Decimal
import re
import os
from datetime import datetime
import requests
import time

# Set seaborn style for Tufte-inspired minimalist charts
sns.set_style("white")
sns.set_context("notebook", rc={"axes.linewidth": 0.5})
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False


def parse_amount(amount_str):
    """Convert amount string like '$1,000.00' to float"""
    if pd.isna(amount_str) or amount_str == "":
        return 0.0
    # Remove dollar sign, commas, and convert to float
    cleaned = re.sub(r'[$,]', '', str(amount_str))
    return float(cleaned)


def read_donation_data():
    """Read and parse the CSV donation data"""
    # Read the CSV file starting from the actual data (no need to skip rows)
    df = pd.read_csv('../data.csv')

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert amount column to numeric
    df['Amount_Numeric'] = df['Amount'].apply(parse_amount)

    # Convert dates to datetime
    df['Submit Date'] = pd.to_datetime(df['Submit Date'])
    df['Year'] = df['Submit Date'].dt.year

    return df


def analyze_by_category(df):
    """Group donations by charitable sector and calculate totals"""
    category_totals = df.groupby('Charitable Sector')['Amount_Numeric'].sum().sort_values(ascending=False)
    return category_totals


def analyze_by_year(df):
    """Analyze donations by year"""
    yearly_amounts = df.groupby('Year')['Amount_Numeric'].sum().sort_index()
    yearly_counts = df.groupby('Year').size().sort_index()
    return yearly_amounts, yearly_counts


def create_yearly_histograms(yearly_amounts, yearly_counts):
    """Create Tufte-style minimalist histograms for yearly data"""
    # Create amount histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(yearly_amounts.index, yearly_amounts.values,
                  color='steelblue', alpha=0.7, width=0.6)

    # Tufte style: minimal text, remove chart junk
    ax.set_title('Donations by Year', fontsize=12, pad=15, fontweight='normal')
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Format y-axis as currency, remove grid
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K' if x >= 1000 else f'${x:,.0f}'))
    ax.tick_params(axis='both', which='major', labelsize=9)

    # Remove spines and ticks for Tufte style
    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)

    plt.tight_layout()
    plt.savefig('../output/yearly_amounts.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    # Create count histogram
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(yearly_counts.index, yearly_counts.values,
                  color='darkgreen', alpha=0.7, width=0.6)

    ax.set_title('Number of Donations by Year', fontsize=12, pad=15, fontweight='normal')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='both', which='major', labelsize=9)

    sns.despine(left=True, bottom=True)
    ax.tick_params(left=False, bottom=False)

    plt.tight_layout()
    plt.savefig('../output/yearly_counts.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()


def get_charity_description(tax_id, app_id=None, app_key=None):
    """Fetch charity description from Charity Navigator API"""
    if not app_id or not app_key:
        return "API credentials not configured"

    try:
        # Format tax ID (remove dashes)
        clean_tax_id = tax_id.replace('-', '') if tax_id else ''

        # Charity Navigator API endpoint
        url = f"https://api.data.charitynavigator.org/v2/Organizations/{clean_tax_id}"
        params = {
            "app_id": app_id,
            "app_key": app_key
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Extract mission or description from the response
            mission = data.get('mission')
            if mission:
                return mission

            # Fallback to other description fields
            cause = data.get('cause', {})
            if isinstance(cause, dict):
                cause_name = cause.get('causeName', '')
                if cause_name:
                    return f"Focuses on: {cause_name}"

            return "No description available"

        elif response.status_code == 404:
            return "Organization not found in Charity Navigator"
        else:
            return f"API error: {response.status_code}"

    except Exception as e:
        return f"Error fetching description: {str(e)}"


def analyze_donation_patterns(df):
    """Analyze one-time vs recurring donation patterns"""
    # Group by Tax ID to analyze donation patterns (same charity regardless of name variations)
    org_donations = df.groupby('Tax ID').agg({
        'Amount_Numeric': ['sum', 'count'],
        'Submit Date': ['min', 'max'],
        'Recurring': 'first',
        'Organization': 'first'  # Keep one organization name for display
    }).round(2)

    org_donations.columns = ['Total_Amount', 'Donation_Count', 'First_Date', 'Last_Date', 'Recurring_Status', 'Organization_Name']

    # One-time donations (single donation)
    one_time = org_donations[org_donations['Donation_Count'] == 1].sort_values('Total_Amount', ascending=False)

    # Organizations with multiple donations that appear to have stopped
    # (multiple donations but last donation was more than 1 year ago and marked as recurring)
    current_year = datetime.now().year
    stopped_recurring = org_donations[
        (org_donations['Donation_Count'] > 1) &
        (org_donations['Last_Date'].dt.year < current_year - 1) &
        (org_donations['Recurring_Status'].str.contains('annually|semi-annually', case=False, na=False))
    ].sort_values('Total_Amount', ascending=False)

    return one_time, stopped_recurring


def analyze_top_charities(df, top_n=10, app_id=None, app_key=None):
    """Analyze top charities by total donations, grouped by Tax ID"""
    # Group by Tax ID and calculate totals
    top_charities = df.groupby('Tax ID').agg({
        'Amount_Numeric': 'sum',
        'Organization': 'first'  # Keep one organization name for display
    }).sort_values('Amount_Numeric', ascending=False).head(top_n)

    # Get detailed donation history for each top charity and fetch descriptions
    charity_details = {}
    charity_descriptions = {}

    for tax_id in top_charities.index:
        # Get all donations for this Tax ID
        charity_data = df[df['Tax ID'] == tax_id][['Submit Date', 'Amount_Numeric', 'Tax ID', 'Charitable Sector', 'Organization']].sort_values('Submit Date')
        charity_details[tax_id] = charity_data

        # Fetch charity description from API
        description = get_charity_description(tax_id, app_id, app_key)
        charity_descriptions[tax_id] = description

        # Add small delay to be respectful to API
        time.sleep(0.1)

    # Create yearly graphs for each charity
    create_charity_yearly_graphs(top_charities, charity_details)

    return top_charities, charity_details, charity_descriptions


def create_charity_yearly_graphs(top_charities, charity_details):
    """Create Tufte-style minimalist yearly donation graphs for each top charity"""
    current_year = datetime.now().year
    last_10_years = list(range(current_year - 9, current_year + 1))

    for i, (tax_id, charity_data) in enumerate(top_charities.iterrows(), 1):
        org_name = charity_data['Organization']
        donations = charity_details[tax_id].copy()

        # Group by year and sum donations
        donations['Year'] = donations['Submit Date'].dt.year
        yearly_totals = donations.groupby('Year')['Amount_Numeric'].sum()

        # Create complete year range with zeros for missing years
        year_amounts = []
        for year in last_10_years:
            amount = yearly_totals.get(year, 0)
            year_amounts.append(amount)

        # Create very small, embedded thumbnail graph
        fig, ax = plt.subplots(figsize=(3, 1.5))  # Very compact for embedding

        # Use seaborn color palette
        color = sns.color_palette("husl", 10)[i-1] if i <= 10 else 'steelblue'
        bars = ax.bar(last_10_years, year_amounts, color=color, alpha=0.8, width=0.7)

        # Ultra-minimal: no title for embedded thumbnail
        # Only show essential data

        # Remove labels and minimize text
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Smart y-axis formatting
        max_amount = max(year_amounts) if year_amounts else 0
        if max_amount >= 10000:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K' if x > 0 else ''))
        else:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}' if x > 0 else ''))

        # Ultra-minimal tick marks for thumbnail
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.tick_params(axis='x', rotation=0)

        # Show only first, middle, and last year for compact display
        years_to_show = [last_10_years[0], last_10_years[4], last_10_years[-1]]
        ax.set_xticks(years_to_show)

        # Remove all spines except bottom (Tufte style)
        sns.despine(left=True, right=True, top=True)
        ax.tick_params(left=False, right=False, top=False)

        # No grid (Tufte principle: remove non-data ink)
        ax.grid(False)

        plt.tight_layout()

        # Save very compact thumbnail
        filename = f'../output/charity_{i:02d}_{tax_id.replace("-", "")}.png'
        plt.savefig(filename, dpi=100, bbox_inches='tight', pad_inches=0.05,
                    facecolor='white', edgecolor='none')
        plt.close()


def generate_markdown_report(category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring, top_charities, charity_details, charity_descriptions):
    """Generate markdown report with analysis results"""
    total_amount = category_totals.sum()
    total_donations = len(df)

    report = f"""# Charitable Donation Analysis Report

*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

## Summary

- **Total Donations:** {total_donations:,} donations
- **Total Amount:** ${total_amount:,.2f}
- **Years Covered:** {df['Year'].min()} - {df['Year'].max()}

## Donations by Charitable Sector

| Charitable Sector | Total Amount | Percentage |
|------------------|--------------|------------|
"""

    for category, amount in category_totals.items():
        percentage = (amount / total_amount) * 100
        report += f"| {category} | ${amount:,.2f} | {percentage:.1f}% |\n"

    report += f"\n**Total:** ${total_amount:,.2f}\n\n"

    report += """## Yearly Analysis

### Total Donation Amounts by Year

![Yearly Amounts](yearly_amounts.png)

| Year | Total Amount | Number of Donations |
|------|--------------|--------------------|
"""

    for year in sorted(yearly_amounts.index):
        amount = yearly_amounts[year]
        count = yearly_counts[year]
        report += f"| {year} | ${amount:,.2f} | {count} |\n"

    report += "\n### Number of Donations by Year\n\n![Yearly Counts](yearly_counts.png)\n"

    # Add one-time donations section
    report += f"\n## One-Time Donations\n\n"
    report += f"Organizations that received a single donation ({len(one_time)} organizations):\n\n"
    report += "| Organization | Amount | Date |\n"
    report += "|--------------|--------|------|\n"

    for tax_id, data in one_time.head(20).iterrows():  # Show top 20
        org_name = data['Organization_Name']
        report += f"| {org_name} | ${data['Total_Amount']:,.2f} | {data['First_Date'].strftime('%m/%d/%Y')} |\n"

    if len(one_time) > 20:
        report += f"\n*... and {len(one_time) - 20} more organizations*\n"

    one_time_total = one_time['Total_Amount'].sum()
    report += f"\n**One-time donations total:** ${one_time_total:,.2f}\n"

    # Add stopped recurring donations section
    report += f"\n## Stopped Recurring Donations\n\n"
    report += f"Organizations with recurring donations that appear to have stopped ({len(stopped_recurring)} organizations):\n\n"
    report += "| Organization | Total Amount | Donations | First Date | Last Date |\n"
    report += "|--------------|--------------|-----------|------------|-----------|\n"

    for tax_id, data in stopped_recurring.head(15).iterrows():  # Show top 15
        org_name = data['Organization_Name']
        report += f"| {org_name} | ${data['Total_Amount']:,.2f} | {data['Donation_Count']} | {data['First_Date'].strftime('%m/%d/%Y')} | {data['Last_Date'].strftime('%m/%d/%Y')} |\n"

    if len(stopped_recurring) > 15:
        report += f"\n*... and {len(stopped_recurring) - 15} more organizations*\n"

    stopped_total = stopped_recurring['Total_Amount'].sum()
    report += f"\n**Stopped recurring donations total:** ${stopped_total:,.2f}\n"

    # Add top charities section
    report += f"\n## Top 10 Charities by Total Donations\n\n"
    report += "| Rank | Organization | Total Amount | Tax ID |\n"
    report += "|------|--------------|--------------|--------|\n"

    for i, (tax_id, data) in enumerate(top_charities.iterrows(), 1):
        org_name = data['Organization']
        tax_id_display = tax_id if pd.notna(tax_id) else 'N/A'
        report += f"| {i} | {org_name} | ${data['Amount_Numeric']:,.2f} | {tax_id_display} |\n"

    # Add detailed sections for each top charity
    report += "\n### Detailed Donation History\n\n"

    for i, (tax_id, _) in enumerate(top_charities.iterrows(), 1):
        org_donations = charity_details[tax_id]
        org_name = org_donations['Organization'].iloc[0] if not org_donations.empty else 'Unknown'
        sector = org_donations['Charitable Sector'].iloc[0] if pd.notna(org_donations['Charitable Sector'].iloc[0]) else 'N/A'
        description = charity_descriptions.get(tax_id, 'No description available')

        # Generate graph filename
        graph_filename = f"charity_{i:02d}_{tax_id.replace('-', '')}.png"

        # Create compact embedded layout with graph in table
        report += f"#### {i}. {org_name}\n\n"

        # Compact info table with embedded thumbnail
        report += f"| Info | Value | 10-Year Trend |\n"
        report += f"|:-----|:------|:-------------:|\n"
        report += f"| **Tax ID** | {tax_id} | ![trend]({graph_filename}) |\n"
        report += f"| **Sector** | {sector} | |\n"
        report += f"| **Total** | ${org_donations['Amount_Numeric'].sum():,.2f} | |\n"
        report += f"| **Donations** | {len(org_donations)} | |\n\n"

        # Description on separate line if available
        if description and description != 'API credentials not configured':
            desc_short = description[:100] + '...' if len(description) > 100 else description
            report += f"*{desc_short}*\n\n"

        report += "**Complete Donation History:**\n\n"
        report += "| Date | Amount |\n"
        report += "|------|---------|\n"

        for _, donation in org_donations.iterrows():
            report += f"| {donation['Submit Date'].strftime('%m/%d/%Y')} | ${donation['Amount_Numeric']:,.2f} |\n"

        report += "\n"

    with open('../output/donation_analysis.md', 'w') as f:
        f.write(report)


def generate_console_report(category_totals):
    """Generate console report of category totals"""
    print("CHARITABLE DONATION ANALYSIS")
    print("=" * 40)
    print()
    print("Total Donations by Charitable Sector:")
    print("-" * 40)

    total_amount = 0
    for category, amount in category_totals.items():
        print(f"{category:<25} ${amount:>10,.2f}")
        total_amount += amount

    print("-" * 40)
    print(f"{'TOTAL':<25} ${total_amount:>10,.2f}")


def main():
    """Main program execution"""
    try:
        # Read the donation data
        df = read_donation_data()

        # Analyze by category
        category_totals = analyze_by_category(df)

        # Analyze by year
        yearly_amounts, yearly_counts = analyze_by_year(df)

        # Generate console report
        generate_console_report(category_totals)

        # Create histograms
        create_yearly_histograms(yearly_amounts, yearly_counts)

        # Analyze donation patterns
        one_time, stopped_recurring = analyze_donation_patterns(df)

        # Analyze top charities (add your Charity Navigator API credentials here)
        app_id = os.getenv('CHARITY_NAVIGATOR_APP_ID', '3069')  # Your app ID
        app_key = os.getenv('CHARITY_NAVIGATOR_APP_KEY')  # You need to provide the app_key
        top_charities, charity_details, charity_descriptions = analyze_top_charities(df, app_id=app_id, app_key=app_key)

        # Generate markdown report
        generate_markdown_report(category_totals, yearly_amounts, yearly_counts, df, one_time, stopped_recurring, top_charities, charity_details, charity_descriptions)

        print("\nReports generated in ../output/ directory")

    except FileNotFoundError:
        print("Error: data.csv file not found")
    except Exception as e:
        print(f"Error processing data: {e}")


if __name__ == "__main__":
    main()