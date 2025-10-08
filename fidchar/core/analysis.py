#!/usr/bin/env python3
"""Analysis module for charitable donation data.

Handles all pandas groupby operations and statistical analysis.
"""

import pandas as pd
from datetime import datetime


def analyze_by_category(df):
    """Group donations by charitable sector and calculate totals"""
    category_totals = df.groupby("Charitable Sector")["Amount_Numeric"].sum().sort_values(ascending=False)
    return category_totals


def analyze_by_year(df):
    """Analyze donations by year"""
    yearly_amounts = df.groupby("Year")["Amount_Numeric"].sum().sort_index()
    yearly_counts = df.groupby("Year").size().sort_index()
    return yearly_amounts, yearly_counts


def analyze_donation_patterns(df):
    """Analyze one-time vs recurring donation patterns"""
    # Group by Tax ID to analyze donation patterns (same charity regardless of name variations)
    org_donations = df.groupby("Tax ID").agg({
        "Amount_Numeric": ["sum", "count"],
        "Submit Date": ["min", "max"],
        "Recurring": "first",
        "Organization": "first"  # Keep one organization name for display
    }).round(2)

    org_donations.columns = ["Total_Amount", "Donation_Count", "First_Date", "Last_Date", "Recurring_Status", "Organization_Name"]

    # One-time donations (single donation)
    one_time = org_donations[org_donations["Donation_Count"] == 1].sort_values("Total_Amount", ascending=False)

    # Organizations with multiple donations that appear to have stopped
    # (multiple donations but last donation was more than 1 year ago and marked as recurring)
    current_year = datetime.now().year
    stopped_recurring = org_donations[
        (org_donations["Donation_Count"] > 1) &
        (org_donations["Last_Date"].dt.year < current_year - 1) &
        (org_donations["Recurring_Status"].str.contains("annually|semi-annually", case=False, na=False))
    ].sort_values("Total_Amount", ascending=False)

    return one_time, stopped_recurring


def get_top_charities_basic(df, top_n=10):
    """Get top charities by total donations, grouped by Tax ID"""
    top_charities = df.groupby("Tax ID").agg({
        "Amount_Numeric": "sum",
        "Organization": "first"  # Keep one organization name for display
    }).sort_values("Amount_Numeric", ascending=False).head(top_n)

    return top_charities


def get_charity_details(df, top_charities):
    """Get detailed donation history for each top charity"""
    charity_details = {}

    for tax_id in top_charities.index:
        # Get all donations for this Tax ID
        charity_data = df[df["Tax ID"] == tax_id][
            ["Submit Date", "Amount_Numeric", "Tax ID", "Charitable Sector", "Organization"]
        ].sort_values("Submit Date")
        charity_details[tax_id] = charity_data

    return charity_details


def analyze_consistent_donors(df, min_years=5, min_amount=500):
    """Find charities with consistent donations over specified years and minimum amount

    Args:
        df: DataFrame with donation data
        min_years: Minimum number of consecutive years required (default: 5)
        min_amount: Minimum amount per year required (default: $500)
    """
    current_year = datetime.now().year
    year_range = list(range(current_year - min_years + 1, current_year + 1))

    yearly_donations = df.groupby(['Tax ID', 'Year'])['Amount_Numeric'].sum().reset_index()

    consistent_donors = {}

    for tax_id in df['Tax ID'].dropna().unique():
        charity_yearly = yearly_donations[yearly_donations['Tax ID'] == tax_id]

        qualifying_years = 0
        yearly_amounts = {}

        for year in year_range:
            year_data = charity_yearly[charity_yearly['Year'] == year]
            if not year_data.empty:
                total_amount = year_data['Amount_Numeric'].sum()
                if total_amount >= min_amount:
                    qualifying_years += 1
                    yearly_amounts[year] = total_amount
                else:
                    break
            else:
                break

        if qualifying_years == min_years:
            org_info = df[df['Tax ID'] == tax_id].iloc[0]
            consistent_donors[tax_id] = {
                'organization': org_info['Organization'],
                'sector': org_info['Charitable Sector'],
                'yearly_amounts': yearly_amounts,
                'total_5_year': sum(yearly_amounts.values()),
                'average_per_year': sum(yearly_amounts.values()) / min_years
            }

    return consistent_donors


def analyze_recurring_donations(df, sort_by="total", min_years=4, stale_years=2):
    """Analyze recurring donations with richer logic.

    Features:
    - Derives Year from Submit Date if not present.
    - Identifies recurring candidates by Recurring field containing 'annually' or 'semi-annually'.
    - Groups by Tax ID and requires at least `min_years` distinct donation years.
    - Excludes charities whose last donation is older than `stale_years` years (stopped schedules).
    - Computes average annual amount (Amount), total ever donated, first year, years supported.
    - Adds Period column inferred from Recurring string: 'Annual', 'Semi-Annual', or 'Unknown'.
    - Sorts by total donated (default) or annual amount.
    """
    if df.empty:
        return pd.DataFrame()

    work = df.copy()

    # Derive Year if missing
    if 'Year' not in work.columns:
        work['Year'] = work['Submit Date'].dt.year

    # Filter to donations that appear to be part of a recurring schedule
    recurring_mask = work['Recurring'].str.contains('annually|semi-annually', case=False, na=False)
    work = work[recurring_mask]
    if work.empty:
        return pd.DataFrame()

    current_year = datetime.now().year

    results = []
    for tax_id in work['Tax ID'].dropna().unique():
        charity = work[work['Tax ID'] == tax_id]
        years = sorted(charity['Year'].unique())
        num_years = len(years)
        if num_years < min_years:
            continue

        last_donation_date = charity['Submit Date'].max()
        if last_donation_date.year < current_year - stale_years:
            # Consider this schedule stale; skip
            continue

        total = charity['Amount_Numeric'].sum()
        avg = total / num_years if num_years else 0
        org_name = charity['Organization'].iloc[0]

        # Determine Period classification
        recurring_values = charity['Recurring'].dropna().astype(str).str.lower().unique()
        if any('semi-annually' in r for r in recurring_values):
            period = 'Semi-Annual'
        elif any('annually' in r for r in recurring_values):
            period = 'Annual'
        else:
            period = 'Unknown'

        results.append({
            'EIN': tax_id,
            'Organization': org_name,
            'First_Year': min(years),
            'Years_Supported': num_years,
            'Amount': avg,
            'Total_Ever_Donated': total,
            'Period': period,
            'Last_Donation_Date': last_donation_date
        })

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)
    sort_col = 'Total_Ever_Donated' if sort_by == 'total' else 'Amount'
    result_df = result_df.sort_values(sort_col, ascending=False).reset_index(drop=True)
    return result_df