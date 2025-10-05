#!/usr/bin/env python3
"""Reporting module for charitable donation analysis.

Handles API calls, report generation, and file output.
"""

import requests
import time
import pandas as pd
from datetime import datetime
from tabulate import tabulate


def get_charity_description(tax_id, app_id=None, app_key=None):
    """Fetch charity description from Charity Navigator API"""
    if not app_id or not app_key:
        return "API credentials not configured"

    try:
        # Format tax ID (remove dashes)
        clean_tax_id = tax_id.replace("-", "") if tax_id else ""

        # Charity Navigator API endpoint
        url = f"https://api.data.charitynavigator.org/v2/Organizations/{clean_tax_id}"
        params = {
            "app_id": app_id,
            "app_key": app_key
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return _extract_charity_mission(data)

        elif response.status_code == 404:
            return "Organization not found in Charity Navigator"
        else:
            return f"API error: {response.status_code}"

    except Exception as e:
        return f"Error fetching description: {str(e)}"


def _extract_charity_mission(data):
    """Extract mission or description from API response"""
    # Extract mission or description from the response
    mission = data.get("mission")
    if mission:
        return mission

    # Fallback to other description fields
    cause = data.get("cause", {})
    if isinstance(cause, dict):
        cause_name = cause.get("causeName", "")
        if cause_name:
            return f"Focuses on: {cause_name}"

    return "No description available"


def get_charity_descriptions(top_charities, app_id=None, app_key=None):
    """Fetch descriptions for all top charities"""
    charity_descriptions = {}

    for tax_id in top_charities.index:
        # Fetch charity description from API
        description = get_charity_description(tax_id, app_id, app_key)
        charity_descriptions[tax_id] = description

        # Add small delay to be respectful to API
        time.sleep(0.1)

    return charity_descriptions


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


def create_category_summary_table(category_totals, total_amount):
    """Create category totals table using tabulate"""
    category_data = []
    for category, amount in category_totals.items():
        percentage = (amount / total_amount) * 100
        category_data.append([category, f"${amount:,.2f}", f"{percentage:.1f}%"])

    category_table = tabulate(category_data,
                            headers=["Charitable Sector", "Total Amount", "Percentage"],
                            tablefmt="simple")

    return category_table


def create_yearly_analysis_table(yearly_amounts, yearly_counts):
    """Create yearly analysis table using tabulate"""
    yearly_data = []
    for year in sorted(yearly_amounts.index):
        amount = yearly_amounts[year]
        count = yearly_counts[year]
        yearly_data.append([year, f"${amount:,.2f}", count])

    yearly_table = tabulate(yearly_data,
                          headers=["Year", "Total Amount", "Number of Donations"],
                          tablefmt="simple")

    return yearly_table


def create_one_time_donations_table(one_time):
    """Create one-time donations table using tabulate"""
    one_time_data = []
    for tax_id, data in one_time.head(20).iterrows():  # Show top 20
        org_name = data["Organization_Name"]
        one_time_data.append([org_name, f"${data['Total_Amount']:,.2f}", data["First_Date"].strftime("%m/%d/%Y")])

    one_time_table = tabulate(one_time_data,
                            headers=["Organization", "Amount", "Date"],
                            tablefmt="simple")

    return one_time_table


def create_stopped_recurring_table(stopped_recurring):
    """Create stopped recurring donations table using tabulate"""
    stopped_data = []
    for tax_id, data in stopped_recurring.head(15).iterrows():  # Show top 15
        org_name = data["Organization_Name"]
        stopped_data.append([org_name, f"${data['Total_Amount']:,.2f}", data["Donation_Count"],
                           data["First_Date"].strftime("%m/%d/%Y"), data["Last_Date"].strftime("%m/%d/%Y")])

    stopped_table = tabulate(stopped_data,
                           headers=["Organization", "Total Amount", "Donations", "First Date", "Last Date"],
                           tablefmt="simple")

    return stopped_table


def create_top_charities_table(top_charities):
    """Create top charities ranking table using tabulate"""
    top_charities_data = []
    for i, (tax_id, data) in enumerate(top_charities.iterrows(), 1):
        org_name = data["Organization"]
        tax_id_display = tax_id if pd.notna(tax_id) else "N/A"
        top_charities_data.append([i, org_name, f"${data['Amount_Numeric']:,.2f}", tax_id_display])

    top_charities_table = tabulate(top_charities_data,
                                 headers=["Rank", "Organization", "Total Amount", "Tax ID"],
                                 tablefmt="simple")

    return top_charities_table


def create_donation_history_table(org_donations):
    """Create individual charity donation history table"""
    donation_history_data = []
    for _, donation in org_donations.iterrows():
        donation_history_data.append([donation["Submit Date"].strftime("%m/%d/%Y"),
                                    f"${donation['Amount_Numeric']:,.2f}"])

    donation_history_table = tabulate(donation_history_data,
                                     headers=["Date", "Amount"],
                                     tablefmt="simple")

    return donation_history_table