#!/usr/bin/env python3
"""Analysis module for charitable donation data.

Handles all pandas groupby operations and statistical analysis.
"""

from datetime import datetime


def analyze_by_category(df):
    """Group donations by charitable sector and calculate totals"""
    category_totals = df.groupby("Charitable Sector")["Amount_Numeric"].sum().sort_values(ascending=False)
    return category_totals


def analyze_by_year(df):
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


def determine_recurring_charities(df, count, min_years, min_amount):
    """Determine recurring charities based on YOUR donation patterns.

    A charity is a "recurring" charity if:
    1. You donated to them in the previous calendar year
    2. In the last 'count' years, you donated in at least 'min_years' years
    3. Each qualifying year had donations >= min_amount
   """
    current_year = datetime.now().year
    previous_year = current_year - 1

    work = df.copy()
    if 'Year' not in work.columns:
        work['Year'] = work['Submit Date'].dt.year

    # Only look at recent years
    recent_years = list(range(current_year - count, current_year + 1))
    work = work[work['Year'].isin(recent_years)]

    recurring_charities = set()

    for tax_id in work['Tax ID'].dropna().unique():
        charity_data = work[work['Tax ID'] == tax_id]

        # Check if donated in previous year
        prev_year_donations = charity_data[charity_data['Year'] == previous_year]
        if prev_year_donations.empty:
            continue

        prev_year_total = prev_year_donations['Amount_Numeric'].sum()
        if prev_year_total < min_amount:
            continue

        # Count qualifying years in the recent period
        yearly_totals = charity_data.groupby('Year')['Amount_Numeric'].sum()
        qualifying_years = sum(1 for amount in yearly_totals if amount >= min_amount)

        if qualifying_years >= min_years:
            recurring_charities.add(tax_id)

    return recurring_charities