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


def analyze_consistent_donors(df):
    """Find charities with consistent donations over last 5 years, $500+ per year"""
    current_year = datetime.now().year
    last_5_years = list(range(current_year - 4, current_year + 1))

    # Group by Tax ID and year to get yearly totals
    yearly_donations = df.groupby(['Tax ID', 'Year'])['Amount_Numeric'].sum().reset_index()

    consistent_donors = {}

    for tax_id in df['Tax ID'].dropna().unique():
        charity_yearly = yearly_donations[yearly_donations['Tax ID'] == tax_id]

        # Check if they donated in each of the last 5 years with $500+ each year
        qualifying_years = 0
        yearly_amounts = {}

        for year in last_5_years:
            year_data = charity_yearly[charity_yearly['Year'] == year]
            if not year_data.empty:
                total_amount = year_data['Amount_Numeric'].sum()
                if total_amount >= 500:
                    qualifying_years += 1
                    yearly_amounts[year] = total_amount
                else:
                    break  # Not consistent if any year is below $500
            else:
                break  # Not consistent if missing any year

        # Must have all 5 years with $500+ each
        if qualifying_years == 5:
            org_info = df[df['Tax ID'] == tax_id].iloc[0]
            consistent_donors[tax_id] = {
                'organization': org_info['Organization'],
                'sector': org_info['Charitable Sector'],
                'yearly_amounts': yearly_amounts,
                'total_5_year': sum(yearly_amounts.values()),
                'average_per_year': sum(yearly_amounts.values()) / 5
            }

    return consistent_donors